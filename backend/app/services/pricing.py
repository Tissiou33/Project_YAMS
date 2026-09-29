"""Calculs métier : commission, frais de livraison, prix dégressifs, distance."""
from math import asin, cos, radians, sin, sqrt

from app.core.config import settings


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


def compute_commission(subtotal_fcfa: int, rate: float | None = None) -> int:
    rate = settings.commission_rate if rate is None else rate
    return round(subtotal_fcfa * rate)


def compute_delivery_fee(
    distance_km: float,
    *,
    express: bool = False,
    rural: bool = False,
    base_fee: int | None = None,
    per_km: int | None = None,
) -> int:
    base = settings.delivery_base_fee if base_fee is None else base_fee
    per_km = settings.delivery_fee_per_km if per_km is None else per_km
    fee = base + per_km * max(distance_km, 0)
    if rural:
        fee *= settings.delivery_rural_multiplier
    if express:
        fee *= settings.delivery_express_multiplier
    return int(round(fee / 50.0) * 50)  # arrondi aux 50 FCFA


def unit_price_for_quantity(base_price: int, tiers: list[tuple[float, int]], quantity: float) -> int:
    """tiers = [(min_qty, unit_price)] ; retourne le meilleur prix applicable."""
    price = base_price
    for min_qty, tier_price in sorted(tiers):
        if quantity >= min_qty:
            price = tier_price
    return price
