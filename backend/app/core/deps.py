import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.enums import AccountStatus, Role
from app.models.user import User

bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou expiré")
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Type de token invalide")
    user = await db.get(User, uuid.UUID(payload["sub"]))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable")
    if user.status in (AccountStatus.SUSPENDED, AccountStatus.BANNED):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Compte suspendu ou radié")
    return user


def require_roles(*roles: Role):
    """RBAC : n'autorise que les rôles listés."""

    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès interdit pour ce rôle")
        return user

    return checker


def require_active(*roles: Role):
    """Rôle autorisé ET compte validé (KYC OK) — pour vendeurs/transporteurs."""

    base = require_roles(*roles)

    async def checker(user: User = Depends(base)) -> User:
        if user.status != AccountStatus.ACTIVE:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Compte en attente de validation")
        return user

    return checker
