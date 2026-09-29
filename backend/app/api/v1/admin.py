import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.enums import AccountStatus, DisputeStatus, KycStatus, OrderStatus, Role
from app.models.order import Order
from app.models.support import Dispute, PlatformSetting
from app.models.user import User
from app.schemas.auth import UserOut
from app.services.audit import log_action

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_roles(Role.ADMIN))])
# TODO: exiger la 2FA pour tous les comptes admin (v1.0 obligatoire) + restriction réseau


@router.get("/accounts/pending", response_model=list[UserOut])
async def pending_accounts(db: AsyncSession = Depends(get_db)):
    q = select(User).where(User.status == AccountStatus.PENDING, User.role.in_([Role.SELLER, Role.CARRIER]))
    return (await db.execute(q)).scalars().all()


async def _get_user(user_id: uuid.UUID, db: AsyncSession) -> User:
    u = await db.get(User, user_id)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    return u


@router.post("/accounts/{user_id}/approve", response_model=UserOut)
async def approve(user_id: uuid.UUID, admin: User = Depends(require_roles(Role.ADMIN)),
                  db: AsyncSession = Depends(get_db)):
    u = await _get_user(user_id, db)
    u.status, u.kyc_status = AccountStatus.ACTIVE, KycStatus.APPROVED
    await log_action(db, admin.id, "account.approve", "user", str(u.id))
    await db.commit()
    return u


@router.post("/accounts/{user_id}/reject", response_model=UserOut)
async def reject(user_id: uuid.UUID, admin: User = Depends(require_roles(Role.ADMIN)),
                 db: AsyncSession = Depends(get_db)):
    u = await _get_user(user_id, db)
    u.kyc_status = KycStatus.REJECTED
    await log_action(db, admin.id, "account.reject", "user", str(u.id))
    await db.commit()
    return u


@router.post("/accounts/{user_id}/suspend", response_model=UserOut)
async def suspend(user_id: uuid.UUID, ban: bool = False, admin: User = Depends(require_roles(Role.ADMIN)),
                  db: AsyncSession = Depends(get_db)):
    u = await _get_user(user_id, db)
    u.status = AccountStatus.BANNED if ban else AccountStatus.SUSPENDED
    await log_action(db, admin.id, "account.ban" if ban else "account.suspend", "user", str(u.id))
    await db.commit()
    return u


@router.get("/disputes")
async def disputes(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Dispute).where(Dispute.status != DisputeStatus.RESOLVED))).scalars().all()
    return [{"id": d.id, "order_id": d.order_id, "reason": d.reason, "status": d.status} for d in rows]


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    orders = (await db.execute(select(func.count(Order.id)))).scalar_one()
    delivered = (await db.execute(select(func.count(Order.id)).where(Order.status == OrderStatus.DELIVERED))).scalar_one()
    revenue = (await db.execute(select(func.coalesce(func.sum(Order.commission_fcfa), 0))
                                .where(Order.status == OrderStatus.DELIVERED))).scalar_one()
    return {"orders": orders, "delivered": delivered, "commission_fcfa": revenue}
    # TODO: délai moyen par région, taux de livraison réussie, cartographie d'activité


class SettingIn(BaseModel):
    value: dict


@router.put("/settings/{key}")
async def put_setting(key: str, body: SettingIn, admin: User = Depends(require_roles(Role.ADMIN)),
                      db: AsyncSession = Depends(get_db)):
    s = await db.get(PlatformSetting, key)
    if s:
        s.value = body.value
    else:
        db.add(PlatformSetting(key=key, value=body.value))
    await log_action(db, admin.id, "setting.update", "setting", key, body.value)
    await db.commit()
    return {"key": key, "value": body.value}
