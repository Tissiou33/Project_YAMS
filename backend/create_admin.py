"""Crée le premier compte administrateur : python create_admin.py +22890000000"""
import asyncio
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.enums import AccountStatus, KycStatus, Role
from app.models.user import User


async def main(phone: str):
    async with SessionLocal() as db:
        if (await db.execute(select(User).where(User.phone == phone))).scalar_one_or_none():
            print("Ce numéro existe déjà")
            return
        db.add(User(phone=phone, role=Role.ADMIN, status=AccountStatus.ACTIVE, kyc_status=KycStatus.APPROVED))
        await db.commit()
        print(f"Admin créé : {phone}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage : python create_admin.py +228XXXXXXXX")
    asyncio.run(main(sys.argv[1]))
