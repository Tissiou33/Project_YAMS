"""Machine à états des commandes (section 3.1.4 / 3.2)."""
from app.models.enums import OrderStatus as S

ALLOWED: dict[S, set[S]] = {
    S.PENDING: {S.ACCEPTED, S.REFUSED, S.CANCELLED},
    S.ACCEPTED: {S.PREPARING, S.CANCELLED},
    S.PREPARING: {S.HANDED_TO_CARRIER},
    S.HANDED_TO_CARRIER: {S.IN_TRANSIT},
    S.IN_TRANSIT: {S.DELIVERED, S.DISPUTED},
    S.DELIVERED: {S.DISPUTED},
    S.REFUSED: set(),
    S.CANCELLED: set(),
    S.DISPUTED: {S.DELIVERED, S.CANCELLED},  # issue décidée par l'arbitrage admin
}


def can_transition(current: S, target: S) -> bool:
    return target in ALLOWED.get(current, set())
