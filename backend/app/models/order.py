import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus
from app.models.mixins import Timestamps, UUIDPk


class Address(UUIDPk, Base):
    __tablename__ = "addresses"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    label: Mapped[str] = mapped_column(String(40))  # domicile / bureau / autre
    city_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id"))
    details: Mapped[str] = mapped_column(String(300))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)


class Order(UUIDPk, Timestamps, Base):
    __tablename__ = "orders"
    tracking_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    address_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"))

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod))
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    subtotal_fcfa: Mapped[int] = mapped_column(Integer)
    delivery_fee_fcfa: Mapped[int] = mapped_column(Integer, default=0)
    commission_fcfa: Mapped[int] = mapped_column(Integer, default=0)
    total_fcfa: Mapped[int] = mapped_column(Integer)
    express: Mapped[bool] = mapped_column(default=False)

    # Codes à usage unique — stockés hachés (voir core.security.hash_code)
    pickup_code_hash: Mapped[str | None] = mapped_column(String(64))    # vendeur -> livreur
    delivery_code_hash: Mapped[str | None] = mapped_column(String(64))  # client -> livreur

    refusal_reason: Mapped[str | None] = mapped_column(String(300))
    status_history: Mapped[list | None] = mapped_column(JSON, default=list)  # horodatage de chaque étape (litiges)

    items: Mapped[list["OrderItem"]] = relationship(cascade="all, delete-orphan", lazy="selectin")


class OrderItem(UUIDPk, Base):
    __tablename__ = "order_items"
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    variety: Mapped[str] = mapped_column(String(80))            # snapshot au moment de la commande
    quantity: Mapped[float] = mapped_column(Numeric(10, 2))
    unit_price_fcfa: Mapped[int] = mapped_column(Integer)
