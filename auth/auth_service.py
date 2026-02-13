"""
TrustHire Authentication Service
JWT-based auth with API key support for SaaS tiers
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from models.user_models import UserInDB, UserTier, TokenData
from config import settings
from utils.logger import get_logger

logger = get_logger("auth")

# ==================== CRYPTO ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

ALGORITHM = "HS256"


# ==================== PASSWORD UTILS ====================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ==================== JWT ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    data = {"sub": user_id, "type": "refresh"}
    expire = datetime.utcnow() + timedelta(days=30)
    data["exp"] = expire
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        tier: str = payload.get("tier", "free")
        if user_id is None:
            return None
        return TokenData(user_id=user_id, tier=UserTier(tier))
    except JWTError:
        return None


# ==================== API KEYS ====================

def generate_api_key(prefix: str = "th") -> tuple[str, str]:
    """
    Generate API key and its hash.
    Returns (raw_key, hashed_key).
    Raw key shown once to user, only hash stored in DB.
    """
    raw = f"{prefix}_{secrets.token_urlsafe(32)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


# ==================== AUTH DEPENDENCIES ====================

async def get_current_user_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> Optional[TokenData]:
    """Extract user from JWT Bearer token"""
    if credentials is None:
        return None
    token_data = decode_token(credentials.credentials)
    return token_data


async def get_current_user_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[TokenData]:
    """Extract user from API Key header"""
    if api_key is None:
        return None

    # In production: lookup hashed key in database
    # For now: validate format
    hashed = hash_api_key(api_key)

    # TODO: query DB for user with this hashed key
    # user = await db.get_user_by_api_key(hashed)
    # if not user: return None
    # return TokenData(user_id=user.id, tier=user.tier)

    # Placeholder for demo
    if api_key.startswith("th_"):
        return TokenData(user_id="api_user", tier=UserTier.PRO)
    return None


async def get_current_user(
    jwt_user: Optional[TokenData] = Depends(get_current_user_jwt),
    api_key_user: Optional[TokenData] = Depends(get_current_user_api_key),
) -> Optional[TokenData]:
    """Accept both JWT and API key authentication"""
    return jwt_user or api_key_user


def require_auth(user: Optional[TokenData] = Depends(get_current_user)) -> TokenData:
    """Dependency: requires authenticated user"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_pro(user: TokenData = Depends(require_auth)) -> TokenData:
    """Dependency: requires PRO or ENTERPRISE tier"""
    if user.tier not in [UserTier.PRO, UserTier.ENTERPRISE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PRO or ENTERPRISE plan required. Upgrade at /billing/upgrade",
        )
    return user


def require_enterprise(user: TokenData = Depends(require_auth)) -> TokenData:
    """Dependency: requires ENTERPRISE tier"""
    if user.tier != UserTier.ENTERPRISE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ENTERPRISE plan required. Contact sales@trusthire.dev",
        )
    return user
