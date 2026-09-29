"""Envoi / vérification d'OTP.

Stockage Redis si REDIS_URL est défini, sinon mémoire (dev/tests).
L'envoi SMS réel est à brancher dans `_send_sms` (Africa's Talking ou agrégateur local).
"""
import time

from app.core.config import settings
from app.core.security import check_code, generate_numeric_code, hash_code


class OtpError(Exception):
    pass


class _MemoryStore:
    def __init__(self):
        self.data: dict[str, tuple[str, float, int]] = {}
        self.last_sent: dict[str, float] = {}

    async def set(self, phone, code_hash, ttl):
        self.data[phone] = (code_hash, time.time() + ttl, 0)
        self.last_sent[phone] = time.time()

    async def get(self, phone):
        item = self.data.get(phone)
        if not item or item[1] < time.time():
            self.data.pop(phone, None)
            return None
        return item

    async def bump(self, phone):
        h, exp, n = self.data[phone]
        self.data[phone] = (h, exp, n + 1)

    async def delete(self, phone):
        self.data.pop(phone, None)

    async def cooldown_active(self, phone, seconds):
        return time.time() - self.last_sent.get(phone, 0) < seconds


_store = _MemoryStore()  # TODO: implémentation Redis (redis.asyncio) quand settings.redis_url est défini


async def _send_sms(phone: str, message: str) -> None:
    # TODO: brancher le fournisseur SMS. En dev, on trace simplement.
    if settings.debug:
        print(f"[SMS -> {phone}] {message}")


async def request_otp(phone: str) -> str | None:
    if await _store.cooldown_active(phone, settings.otp_request_cooldown_seconds):
        raise OtpError("Patientez avant de redemander un code")
    code = generate_numeric_code(settings.otp_length)
    await _store.set(phone, hash_code(code), settings.otp_ttl_seconds)
    await _send_sms(phone, f"Igname Express : votre code est {code} (valable 5 min)")
    return code if settings.debug else None  # le code n'est renvoyé qu'en dev


async def verify_otp(phone: str, code: str) -> None:
    item = await _store.get(phone)
    if not item:
        raise OtpError("Code expiré ou inexistant")
    code_hash, _, attempts = item
    if attempts >= settings.otp_max_attempts:
        await _store.delete(phone)
        raise OtpError("Trop de tentatives, redemandez un code")
    if not check_code(code, code_hash):
        await _store.bump(phone)
        raise OtpError("Code incorrect")
    await _store.delete(phone)
