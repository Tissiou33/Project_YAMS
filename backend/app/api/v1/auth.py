import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.enums import AccountStatus, Role
from app.models.user import User
from app.schemas.auth import (OtpRequest, OtpVerify, ProfileUpdate, RefreshRequest,
                              TokenPair, UserOut)
from app.services import otp
from app.services.audit import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request")
async def otp_request(body: OtpRequest):
    try:
        code = await otp.request_otp(body.phone)
    except otp.OtpError as e:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e))
    return {"sent": True, "debug_code": code}  # debug_code = None en production


@router.post("/otp/verify", response_model=TokenPair)
async def otp_verify(body: OtpVerify, db: AsyncSession = Depends(get_db)):
    try:
        await otp.verify_otp(body.phone, body.code)
    except otp.OtpError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

    user = (await db.execute(select(User).where(User.phone == body.phone))).scalar_one_or_none()
    if user is None:
        if body.role == Role.ADMIN:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Rôle non autorisé à l'inscription")
        # Vendeurs et transporteurs : en attente de validation KYC ; clients : actifs d'emblée
        initial = AccountStatus.ACTIVE if body.role == Role.CLIENT else AccountStatus.PENDING
        user = User(phone=body.phone, role=body.role, status=initial,
                    accepted_terms_at=datetime.now(timezone.utc))
        db.add(user)
        await db.flush()
        await log_action(db, user.id, "user.register", "user", str(user.id), {"role": body.role.value})
    elif user.status in (AccountStatus.SUSPENDED, AccountStatus.BANNED):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Compte suspendu ou radié")
    await db.commit()
    return TokenPair(access_token=create_access_token(str(user.id), user.role.value),
                     refresh_token=create_refresh_token(str(user.id), user.role.value))


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token invalide")
    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Type de token invalide")
    user = await db.get(User, uuid.UUID(payload["sub"]))
    if not user or user.status in (AccountStatus.SUSPENDED, AccountStatus.BANNED):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session révoquée")
    # TODO: liste de révocation (Redis) pour perte de terminal
    return TokenPair(access_token=create_access_token(str(user.id), user.role.value),
                     refresh_token=create_refresh_token(str(user.id), user.role.value))


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(body: ProfileUpdate, user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    await db.commit()
    return user
