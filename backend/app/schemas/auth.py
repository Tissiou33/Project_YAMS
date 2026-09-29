import re
import uuid

from pydantic import BaseModel, field_validator

from app.models.enums import Role

PHONE_RE = re.compile(r"^\+228\d{8}$")  # numéros togolais


class OtpRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, v: str) -> str:
        v = v.replace(" ", "")
        if not PHONE_RE.match(v):
            raise ValueError("Numéro invalide (format attendu : +228XXXXXXXX)")
        return v


class OtpVerify(OtpRequest):
    code: str
    role: Role = Role.CLIENT  # admin non auto-attribuable, cf. route

    @field_validator("code")
    @classmethod
    def digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Code invalide")
        return v


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: uuid.UUID
    phone: str
    role: Role
    status: str
    kyc_status: str
    first_name: str | None = None
    last_name: str | None = None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    sex: str | None = None
    city_id: uuid.UUID | None = None
