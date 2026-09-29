import enum


class Role(str, enum.Enum):
    CLIENT = "client"
    SELLER = "seller"
    CARRIER = "carrier"
    ADMIN = "admin"


class AccountStatus(str, enum.Enum):
    PENDING = "pending"      # « en attente de validation »
    ACTIVE = "active"        # « validé »
    SUSPENDED = "suspended"
    BANNED = "banned"        # radié


class KycStatus(str, enum.Enum):
    NOT_SUBMITTED = "not_submitted"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"                  # en attente
    ACCEPTED = "accepted"                # acceptée
    REFUSED = "refused"
    PREPARING = "preparing"              # en préparation
    HANDED_TO_CARRIER = "handed_to_carrier"  # remise au transporteur
    IN_TRANSIT = "in_transit"            # en route
    DELIVERED = "delivered"              # livrée
    CANCELLED = "cancelled"              # annulée
    DISPUTED = "disputed"                # litige


class PaymentMethod(str, enum.Enum):
    FLOOZ = "flooz"
    TMONEY = "tmoney"
    CARD = "card"
    CASH_ON_DELIVERY = "cash_on_delivery"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    ESCROW = "escrow"        # fonds séquestrés (v1.1)
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class DeliveryStatus(str, enum.Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"        # client absent, adresse erronée…


class DeliveryMode(str, enum.Enum):
    LOCAL = "local"
    LONG_DISTANCE = "long_distance"


class Unit(str, enum.Enum):
    KG = "kg"
    TUBER = "tubercule"
    HEAP = "tas"


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
