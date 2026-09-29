import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import require_active, require_roles
from app.core.security import generate_numeric_code, hash_code
from app.models.delivery import Delivery
from app.models.enums import OrderStatus, PaymentMethod, Role
from app.models.order import Address, Order, OrderItem
from app.models.shop import Product, Shop
from app.models.user import User
from app.schemas.order import (OrderCreate, OrderCreated, OrderOut, PickupAccepted, RefuseRequest)
from app.services.audit import log_action
from app.services.order_state import can_transition
from app.services.pricing import (compute_commission, compute_delivery_fee, haversine_km,
                                  unit_price_for_quantity)

router = APIRouter(prefix="/orders", tags=["orders"])


def _push_history(order: Order, new_status: OrderStatus) -> None:
    hist = list(order.status_history or [])
    hist.append({"status": new_status.value, "at": datetime.now(timezone.utc).isoformat()})
    order.status_history = hist
    order.status = new_status


@router.post("", response_model=OrderCreated, status_code=201)
async def create_order(body: OrderCreate, client: User = Depends(require_roles(Role.CLIENT)),
                       db: AsyncSession = Depends(get_db)):
    shop = await db.get(Shop, body.shop_id)
    address = await db.get(Address, body.address_id)
    if not shop or not address or address.user_id != client.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Boutique ou adresse introuvable")

    subtotal, items = 0, []
    for line in body.items:
        product = await db.get(Product, line.product_id)
        if not product or product.shop_id != shop.id or not product.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Produit indisponible")
        if float(product.stock_qty) < line.quantity:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Stock insuffisant pour {product.variety}")
        tiers = [(float(t.min_qty), t.unit_price_fcfa) for t in product.price_tiers]
        unit_price = unit_price_for_quantity(product.unit_price_fcfa, tiers, line.quantity)
        subtotal += round(unit_price * line.quantity)
        items.append(OrderItem(product_id=product.id, variety=product.variety,
                               quantity=line.quantity, unit_price_fcfa=unit_price))

    distance = 0.0
    if None not in (shop.latitude, shop.longitude, address.latitude, address.longitude):
        distance = haversine_km(shop.latitude, shop.longitude, address.latitude, address.longitude)
    fee = compute_delivery_fee(distance, express=body.express)
    commission = compute_commission(subtotal)

    delivery_code = generate_numeric_code(6)
    order = Order(
        tracking_number="IGN-" + secrets.token_hex(4).upper(),
        client_id=client.id, shop_id=shop.id, address_id=address.id,
        payment_method=body.payment_method, subtotal_fcfa=subtotal,
        delivery_fee_fcfa=fee, commission_fcfa=commission, total_fcfa=subtotal + fee,
        express=body.express, delivery_code_hash=hash_code(delivery_code), items=items,
        status_history=[{"status": "pending", "at": datetime.now(timezone.utc).isoformat()}],
    )
    db.add(order)
    await db.flush()
    await log_action(db, client.id, "order.create", "order", str(order.id), {"total": order.total_fcfa})
    await db.commit()
    # TODO: déclencher le paiement (passerelle certifiée), notifier le vendeur (push + SMS)
    return OrderCreated.model_validate({**OrderOut.model_validate(order).model_dump(), "delivery_code": delivery_code})


@router.get("/me", response_model=list[OrderOut])
async def my_orders(user: User = Depends(require_roles(Role.CLIENT, Role.SELLER)),
                    db: AsyncSession = Depends(get_db)):
    if user.role == Role.CLIENT:
        q = select(Order).where(Order.client_id == user.id)
    else:
        q = select(Order).join(Shop, Shop.id == Order.shop_id).where(Shop.owner_id == user.id)
    return (await db.execute(q.order_by(Order.created_at.desc()))).scalars().all()


async def _seller_order(order_id: uuid.UUID, user: User, db: AsyncSession) -> Order:
    order = await db.get(Order, order_id)
    shop = await db.get(Shop, order.shop_id) if order else None
    if not order or not shop or shop.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Commande introuvable")
    return order


@router.post("/{order_id}/accept", response_model=PickupAccepted)
async def accept_order(order_id: uuid.UUID, user: User = Depends(require_active(Role.SELLER)),
                       db: AsyncSession = Depends(get_db)):
    order = await _seller_order(order_id, user, db)
    if not can_transition(order.status, OrderStatus.ACCEPTED):
        raise HTTPException(status.HTTP_409_CONFLICT, "Transition impossible")
    pickup_code = generate_numeric_code(6)
    order.pickup_code_hash = hash_code(pickup_code)
    _push_history(order, OrderStatus.ACCEPTED)
    db.add(Delivery(order_id=order.id))  # course proposée aux transporteurs
    await log_action(db, user.id, "order.accept", "order", str(order.id))
    await db.commit()
    return PickupAccepted.model_validate({**OrderOut.model_validate(order).model_dump(), "pickup_code": pickup_code})


@router.post("/{order_id}/refuse", response_model=OrderOut)
async def refuse_order(order_id: uuid.UUID, body: RefuseRequest,
                       user: User = Depends(require_active(Role.SELLER)), db: AsyncSession = Depends(get_db)):
    order = await _seller_order(order_id, user, db)
    if not can_transition(order.status, OrderStatus.REFUSED):
        raise HTTPException(status.HTTP_409_CONFLICT, "Transition impossible")
    order.refusal_reason = body.reason
    _push_history(order, OrderStatus.REFUSED)
    await log_action(db, user.id, "order.refuse", "order", str(order.id), {"reason": body.reason})
    await db.commit()
    return order


@router.post("/{order_id}/preparing", response_model=OrderOut)
async def mark_preparing(order_id: uuid.UUID, user: User = Depends(require_active(Role.SELLER)),
                         db: AsyncSession = Depends(get_db)):
    order = await _seller_order(order_id, user, db)
    if not can_transition(order.status, OrderStatus.PREPARING):
        raise HTTPException(status.HTTP_409_CONFLICT, "Transition impossible")
    _push_history(order, OrderStatus.PREPARING)
    await db.commit()
    return order


@router.post("/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(order_id: uuid.UUID, user: User = Depends(require_roles(Role.CLIENT)),
                       db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order or order.client_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Commande introuvable")
    if order.status != OrderStatus.PENDING:  # annulation possible tant que le vendeur n'a pas accepté
        raise HTTPException(status.HTTP_409_CONFLICT, "Annulation impossible : commande déjà traitée")
    _push_history(order, OrderStatus.CANCELLED)
    await log_action(db, user.id, "order.cancel", "order", str(order.id))
    await db.commit()
    return order
