import uuid

from pydantic import BaseModel, Field

from app.models.enums import OrderStatus, PaymentMethod


class OrderLineIn(BaseModel):
    product_id: uuid.UUID
    quantity: float = Field(gt=0)


class OrderCreate(BaseModel):
    shop_id: uuid.UUID
    address_id: uuid.UUID
    payment_method: PaymentMethod
    express: bool = False
    items: list[OrderLineIn] = Field(min_length=1)


class OrderOut(BaseModel):
    id: uuid.UUID
    tracking_number: str
    status: OrderStatus
    subtotal_fcfa: int
    delivery_fee_fcfa: int
    commission_fcfa: int
    total_fcfa: int

    model_config = {"from_attributes": True}


class OrderCreated(OrderOut):
    delivery_code: str  # affiché UNE seule fois au client ; à donner au livreur


class RefuseRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=300)


class PickupAccepted(OrderOut):
    pickup_code: str  # affiché UNE seule fois au vendeur ; à donner au livreur


class CodeConfirm(BaseModel):
    code: str = Field(min_length=4, max_length=8)
