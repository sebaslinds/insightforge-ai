import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import get_settings
from core.database import get_db
from core.tenant_models import ApiKey, Tenant, AdminUser

settings = get_settings()

# Configuration Password Hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Configuration JWT
SECRET_KEY = settings.OPENAI_API_KEY # On réutilise la clé API comme sel par défaut si pas de JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 jour

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# --- Password Utilities ---

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- JWT Utilities ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Dependency Injections ---

async def get_current_tenant(
    api_key: str = Security(API_KEY_HEADER),
    db: Session = Depends(get_db),
) -> Tenant:
    """Valide l'API Key pour les appels SDK."""
    if not api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header manquant.")
    
    record = db.query(ApiKey).filter(ApiKey.key == api_key, ApiKey.is_active == True).first()
    if not record:
        raise HTTPException(status_code=403, detail="API Key invalide.")
    
    record.last_used_at = datetime.utcnow()
    db.commit()
    return record.tenant

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Valide le token JWT pour l'accès Dashboard."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(AdminUser).filter(AdminUser.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def generate_api_key() -> str:
    """Génère une API Key sécurisée préfixée `if_`."""
    return "if_" + secrets.token_urlsafe(32)
