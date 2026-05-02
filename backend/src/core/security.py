"""
Étape 5 — Authentification par API Key multi-tenant.
Chaque tenant possède une clé dans la table `api_keys`.
Le header `X-API-Key` est obligatoire sur tous les endpoints protégés.
"""
import secrets
from datetime import datetime

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from core.database import get_db
from core.tenant_models import ApiKey, Tenant

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_tenant(
    api_key: str = Security(API_KEY_HEADER),
    db: Session = Depends(get_db),
) -> Tenant:
    """Valide l'API Key et retourne le tenant correspondant."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header manquant.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    record = (
        db.query(ApiKey)
        .filter(ApiKey.key == api_key, ApiKey.is_active == True)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key invalide ou révoquée.",
        )

    # Mise à jour de la dernière utilisation
    record.last_used_at = datetime.utcnow()
    db.commit()

    return record.tenant


def generate_api_key() -> str:
    """Génère une API Key sécurisée préfixée `if_`."""
    return "if_" + secrets.token_urlsafe(32)
