"""
Modèles SQLAlchemy pour le multi-tenant : Tenant + ApiKey.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name       = Column(String(120), nullable=False, unique=True)
    slug       = Column(String(60),  nullable=False, unique=True)   # ex: "acme-corp"
    plan       = Column(String(20),  nullable=False, default="free")  # free/pro/enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active  = Column(Boolean, default=True)

    api_keys = relationship("ApiKey", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant {self.slug}>"


class ApiKey(Base):
    __tablename__ = "api_keys"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id    = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    key          = Column(String(80), nullable=False, unique=True, index=True)
    label        = Column(String(120), nullable=True)   # ex: "Production Key"
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="api_keys")

    def __repr__(self):
        return f"<ApiKey {self.key[:12]}… tenant={self.tenant_id}>"
