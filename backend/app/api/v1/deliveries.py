import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_active, require_roles
from app.core.security import check_code
from app.models.delivery import Delivery
from app.models.enums import DeliveryStatus, OrderStatus, Role
from app.models.order import Order
from app.models.user import User
from app.schemas.order import CodeConfirm
from app.services.audit import log_action
from app.services.order_state import can_transition

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


class Position(BaseModel):
    lat: float
    lng: float


@router.get("/available")
async def available(user: User = Depends(require_active(Role.CARRIER)), db: AsyncSession = Depends(get_db)):
    # TODO: filtrer par zone couverte et proximité (PostGIS) ; affectation auto (section 8.2)
    q = select(Delivery).where(Delivery.status == DeliveryStatus.PROPOSED, Delivery.carrier_id.is_(None))
    rows = (await db.execute(q.limit(50))).scalars().all()
    return [{"id": d.id, "order_id": d.order_id, "distance_km": d.distance_km, "fee_fcfa": d.fee_fcfa} for d in rows]


async def _my_delivery(delivery_id: uuid.UUID, user: User, db: AsyncSession) -> Delivery:
    d = await db.get(Delivery, delivery_id)
    if not d or d.carrier_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course introuvable")
    return d


@router.post("/{delivery_id}/accept")
async def accept(delivery_id: uuid.UUID, user: User = Depends(require_active(Role.CARRIER)),
                 db: AsyncSession = Depends(get_db)):
    d = await db.get(Delivery, delivery_id)
    if not d or d.status != DeliveryStatus.PROPOSED or d.carrier_id is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Course indisponible")
    d.carrier_id, d.status = user.id, DeliveryStatus.ACCEPTED
    await log_action(db, user.id, "delivery.accept", "delivery", str(d.id))
    await db.commit()
    return {"status": d.status}


@router.post("/{delivery_id}/pickup")
async def pickup(delivery_id: uuid.UUID, body: CodeConfirm, user: User = Depends(require_active(Role.CARRIER)),
                 db: AsyncSession = Depends(get_db)):
    d = await _my_delivery(delivery_id, user, db)
    order = await db.get(Order, d.order_id)
    if d.status != DeliveryStatus.ACCEPTED or not order.pickup_code_hash or \
            not check_code(body.code, order.pickup_code_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Code de remise invalide")
    order.pickup_code_hash = None  # usage unique
    d.status, d.picked_up_at = DeliveryStatus.PICKED_UP, datetime.now(timezone.utc)
    order.status = OrderStatus.HANDED_TO_CARRIER
    await log_action(db, user.id, "delivery.pickup", "delivery", str(d.id))
    await db.commit()
    return {"status": d.status}


@router.post("/{delivery_id}/position")
async def update_position(delivery_id: uuid.UUID, body: Position,
                          user: User = Depends(require_active(Role.CARRIER)), db: AsyncSession = Depends(get_db)):
    d = await _my_delivery(delivery_id, user, db)
    d.current_lat, d.current_lng = body.lat, body.lng
    if d.status == DeliveryStatus.PICKED_UP:
        d.status = DeliveryStatus.IN_TRANSIT
        order = await db.get(Order, d.order_id)
        order.status = OrderStatus.IN_TRANSIT
    await db.commit()
    return {"ok": True}  # TODO: pousser en temps réel (WebSocket / SSE) au client


@router.post("/{delivery_id}/deliver")
async def deliver(delivery_id: uuid.UUID, body: CodeConfirm, user: User = Depends(require_active(Role.CARRIER)),
                  db: AsyncSession = Depends(get_db)):
    d = await _my_delivery(delivery_id, user, db)
    order = await db.get(Order, d.order_id)
    if d.status not in (DeliveryStatus.PICKED_UP, DeliveryStatus.IN_TRANSIT) or \
            not order.delivery_code_hash or not check_code(body.code, order.delivery_code_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Code de livraison invalide")
    order.delivery_code_hash = None
    d.status, d.delivered_at = DeliveryStatus.DELIVERED, datetime.now(timezone.utc)
    if can_transition(order.status, OrderStatus.DELIVERED):
        order.status = OrderStatus.DELIVERED
    # TODO: libérer le séquestre (escrow), créditer vendeur/transporteur, prélever la commission
    await log_action(db, user.id, "delivery.deliver", "delivery", str(d.id))
    await db.commit()
    return {"status": d.status}


@router.post("/{delivery_id}/incident")
async def incident(delivery_id: uuid.UUID, reason: str, user: User = Depends(require_active(Role.CARRIER)),
                   db: AsyncSession = Depends(get_db)):
    d = await _my_delivery(delivery_id, user, db)
    d.incident = reason[:300]  # client absent, adresse erronée, produit endommagé…
    await log_action(db, user.id, "delivery.incident", "delivery", str(d.id), {"reason": d.incident})
    await db.commit()
    return {"ok": True}
