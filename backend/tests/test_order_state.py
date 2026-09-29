from app.models.enums import OrderStatus as S
from app.services.order_state import can_transition


def test_happy_path():
    path = [S.PENDING, S.ACCEPTED, S.PREPARING, S.HANDED_TO_CARRIER, S.IN_TRANSIT, S.DELIVERED]
    assert all(can_transition(a, b) for a, b in zip(path, path[1:]))


def test_forbidden():
    assert not can_transition(S.DELIVERED, S.PENDING)
    assert not can_transition(S.REFUSED, S.ACCEPTED)
    assert not can_transition(S.PREPARING, S.CANCELLED)
