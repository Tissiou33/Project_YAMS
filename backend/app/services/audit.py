import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.support import AuditLog


async def log_action(
    db: AsyncSession,
    actor_id: uuid.UUID | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    payload: dict | None = None,
) -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, entity=entity, entity_id=entity_id, payload=payload))
