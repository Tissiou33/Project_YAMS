# Importer tous les modèles pour que Base.metadata les connaisse (création de tables / Alembic).
from app.models.delivery import Delivery  # noqa: F401
from app.models.geo import City, Prefecture, Region  # noqa: F401
from app.models.order import Address, Order, OrderItem  # noqa: F401
from app.models.shop import PriceTier, Product, Shop, shop_delivery_zones  # noqa: F401
from app.models.support import AuditLog, Dispute, PlatformSetting, Review  # noqa: F401
from app.models.user import User  # noqa: F401
