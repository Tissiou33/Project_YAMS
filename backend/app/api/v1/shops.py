import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import require_active, require_roles
from app.models.enums import Role
from app.models.shop import PriceTier, Product, Shop, shop_delivery_zones
from app.models.user import User
from app.schemas.shop import (ProductCreate, ProductOut, ProductUpdate, ShopCreate, ShopOut)

router = APIRouter(tags=["shops & products"])


# ---------- Boutique (vendeur) ----------
@router.post("/shops", response_model=ShopOut, status_code=201)
async def create_shop(body: ShopCreate, user: User = Depends(require_active(Role.SELLER)),
                      db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Shop).where(Shop.owner_id == user.id))).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Vous avez déjà une boutique")
    data = body.model_dump(exclude={"delivery_prefecture_ids"})
    shop = Shop(owner_id=user.id, **data)
    db.add(shop)
    await db.flush()
    for pid in body.delivery_prefecture_ids:
        await db.execute(shop_delivery_zones.insert().values(shop_id=shop.id, prefecture_id=pid))
    await db.commit()
    return shop


@router.get("/shops/me", response_model=ShopOut)
async def my_shop(user: User = Depends(require_roles(Role.SELLER)), db: AsyncSession = Depends(get_db)):
    shop = (await db.execute(select(Shop).where(Shop.owner_id == user.id))).scalar_one_or_none()
    if not shop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aucune boutique")
    return shop


# ---------- Catalogue public ----------
@router.get("/products", response_model=list[ProductOut])
async def search_products(
    variety: str | None = None,
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
    verified_only: bool = False,
    limit: int = Query(20, le=50),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(Product).join(Shop).where(Product.is_active, Product.is_moderated_ok, Product.stock_qty > 0)
    if variety:
        q = q.where(Product.variety.ilike(f"%{variety}%"))
    if min_price is not None:
        q = q.where(Product.unit_price_fcfa >= min_price)
    if max_price is not None:
        q = q.where(Product.unit_price_fcfa <= max_price)
    if verified_only:
        q = q.where(Shop.is_verified_badge)
    # TODO: filtre géographique (PostGIS), tri par note / mise en avant, filtre zone de livraison
    q = q.order_by(Product.featured_until.desc().nulls_last(), Product.created_at.desc()).limit(limit).offset(offset)
    return (await db.execute(q)).scalars().all()


@router.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    p = await db.get(Product, product_id)
    if not p or not p.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produit introuvable")
    return p


# ---------- Gestion des annonces (vendeur) ----------
async def _my_shop_or_404(user: User, db: AsyncSession) -> Shop:
    shop = (await db.execute(select(Shop).where(Shop.owner_id == user.id))).scalar_one_or_none()
    if not shop:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Créez d'abord votre boutique")
    return shop


@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(body: ProductCreate, user: User = Depends(require_active(Role.SELLER)),
                         db: AsyncSession = Depends(get_db)):
    shop = await _my_shop_or_404(user, db)
    data = body.model_dump(exclude={"price_tiers"})
    product = Product(shop_id=shop.id, **data)
    product.price_tiers = [PriceTier(**t.model_dump()) for t in body.price_tiers]
    db.add(product)
    await db.commit()
    return product


@router.patch("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: uuid.UUID, body: ProductUpdate,
                         user: User = Depends(require_active(Role.SELLER)), db: AsyncSession = Depends(get_db)):
    shop = await _my_shop_or_404(user, db)
    product = await db.get(Product, product_id)
    if not product or product.shop_id != shop.id:  # un vendeur ne touche jamais aux données d'un autre
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produit introuvable")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(product, k, v)
    await db.commit()
    return product


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: uuid.UUID, user: User = Depends(require_active(Role.SELLER)),
                         db: AsyncSession = Depends(get_db)):
    shop = await _my_shop_or_404(user, db)
    product = await db.get(Product, product_id)
    if not product or product.shop_id != shop.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produit introuvable")
    product.is_active = False  # retrait logique (historique des commandes préservé)
    await db.commit()
