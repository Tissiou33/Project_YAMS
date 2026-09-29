from fastapi.testclient import TestClient

from app.core.config import settings
settings.auto_create_tables = False  # pas de DB pour ce test

from app.main import app  # noqa: E402


def test_health():
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_phone_validation_rejects_bad_number():
    with TestClient(app) as c:
        r = c.post("/api/v1/auth/otp/request", json={"phone": "12345"})
        assert r.status_code == 422


def test_otp_flow_request_returns_debug_code():
    with TestClient(app) as c:
        r = c.post("/api/v1/auth/otp/request", json={"phone": "+22890000001"})
        assert r.status_code == 200 and len(r.json()["debug_code"]) == 6


def test_protected_route_requires_token():
    with TestClient(app) as c:
        assert c.get("/api/v1/auth/me").status_code in (401, 403)
        assert c.get("/api/v1/admin/stats").status_code in (401, 403)
