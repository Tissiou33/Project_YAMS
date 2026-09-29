import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import AccountStatus, KycStatus, Role
from app.models.mixins import Timestamps, UUIDPk


class User(UUIDPk, Timestamps, Base):
    __tablename__ = "users"

    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # format E.164 (+228…)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.CLIENT)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    kyc_status: Mapped[KycStatus] = mapped_column(Enum(KycStatus), default=KycStatus.NOT_SUBMITTED)

    first_name: Mapped[str | None] = mapped_column(String(80))
    last_name: Mapped[str | None] = mapped_column(String(80))
    sex: Mapped[str | None] = mapped_column(String(1))
    birth_date: Mapped[date | None] = mapped_column(Date)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    email: Mapped[str | None] = mapped_column(String(160))
    city_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id"))

    # KYC (pièces chiffrées au repos côté stockage objet)
    id_document_type: Mapped[str | None] = mapped_column(String(20))  # CNI / carte d'électeur / passeport
    id_document_url: Mapped[str | None] = mapped_column(String(500))
    rccm_number: Mapped[str | None] = mapped_column(String(60))       # coopératives (optionnel)

    # Sécurité
    hashed_password: Mapped[str | None] = mapped_column(String(255))  # argon2, si utilisé
    two_factor_enabled: Mapped[bool] = mapped_column(default=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_terms_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # CGU/CGV
    fcm_token: Mapped[str | None] = mapped_column(String(300))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # droit à l'effacement
