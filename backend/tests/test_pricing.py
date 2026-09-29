from app.services.pricing import (compute_commission, compute_delivery_fee, haversine_km,
                                  unit_price_for_quantity)


def test_commission_rounding():
    assert compute_commission(10_000, 0.08) == 800


def test_delivery_fee_grows_with_distance_and_express():
    local = compute_delivery_fee(5)
    far = compute_delivery_fee(50)
    express = compute_delivery_fee(5, express=True)
    assert far > local
    assert express > local
    assert local % 50 == 0


def test_tiered_price():
    tiers = [(50, 450), (100, 400)]
    assert unit_price_for_quantity(500, tiers, 10) == 500
    assert unit_price_for_quantity(500, tiers, 60) == 450
    assert unit_price_for_quantity(500, tiers, 150) == 400


def test_haversine_lome_kara():
    d = haversine_km(6.1725, 1.2314, 9.5511, 1.1861)  # Lomé -> Kara
    assert 350 < d < 420
