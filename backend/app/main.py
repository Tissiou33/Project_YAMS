from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (enregistre les modèles)
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables and settings.env == "dev":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)  # dev uniquement -> Alembic ensuite
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# TODO: rate limiting (Redis) sur /auth/otp/*, paiement ; en-têtes de sécurité ; WAF en frontal


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": settings.app_name}


app.include_router(api_router, prefix="/api/v1")
