"""
TrustHire Auth API Endpoints
Register, login, refresh tokens, manage API keys
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials

from models.user_models import (
    RegisterRequest, LoginRequest, RefreshRequest,
    Token, UserPublic, APIKeyCreate, APIKeyResponse,
    ChangePasswordRequest,
)
from auth.auth_service import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_api_key, hash_api_key,
    require_auth, get_current_user,
)
from database.user_repository import UserRepository
from utils.logger import get_logger

logger = get_logger("api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==================== REGISTER ====================

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
):
    """
    Register a new user account.
    
    Creates a FREE tier account. Upgrade via /billing/checkout.
    """
    db = UserRepository()

    # Check if email already exists
    existing = await db.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    hashed = hash_password(request.password)
    user = await db.create_user(
        email=request.email,
        name=request.name,
        hashed_password=hashed,
    )

    # TODO: background_tasks.add_task(send_verification_email, user.email)

    # Generate tokens
    access_token = create_access_token(
        data={"sub": user.id, "tier": user.tier.value},
        expires_delta=timedelta(hours=24),
    )
    refresh_token = create_refresh_token(user.id)

    logger.info("user_registered", extra={"user_id": user.id})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        tier=user.tier,
    )


# ==================== LOGIN ====================

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """
    Login with email and password.
    
    Returns JWT access token (24h) and refresh token (30d).
    """
    db = UserRepository()

    user = await db.get_by_email(request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled. Contact support@trusthire.dev",
        )

    access_token = create_access_token(
        data={"sub": user.id, "tier": user.tier.value},
        expires_delta=timedelta(hours=24),
    )
    refresh_token = create_refresh_token(user.id)

    logger.info("user_login", extra={"user_id": user.id, "tier": user.tier.value})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        tier=user.tier,
    )


# ==================== REFRESH ====================

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest):
    """
    Exchange a refresh token for a new access token.
    
    Refresh tokens are valid for 30 days.
    """
    token_data = decode_token(request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    db = UserRepository()
    user = await db.get_by_id(token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
        )

    access_token = create_access_token(
        data={"sub": user.id, "tier": user.tier.value},
        expires_delta=timedelta(hours=24),
    )
    new_refresh = create_refresh_token(user.id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh,
        tier=user.tier,
    )


# ==================== ME ====================

@router.get("/me", response_model=UserPublic)
async def get_me(user=Depends(require_auth)):
    """Get current user profile and usage stats"""
    db = UserRepository()
    user_db = await db.get_by_id(user.user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db.to_public()


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: ChangePasswordRequest,
    user=Depends(require_auth),
):
    """Change account password"""
    db = UserRepository()
    user_db = await db.get_by_id(user.user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(request.current_password, user_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    new_hash = hash_password(request.new_password)
    await db.update_password(user.user_id, new_hash)
    logger.info("password_changed", extra={"user_id": user.user_id})


# ==================== API KEYS ====================

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreate,
    user=Depends(require_auth),
):
    """
    Generate a new API key for programmatic access.
    
    ⚠️ The key is shown ONLY ONCE. Store it securely.
    Previous key is invalidated when a new one is created.
    """
    raw_key, hashed_key = generate_api_key(prefix="th")
    prefix_display = raw_key[:13] + "..."  # "th_XXXXXXXXXX..."

    db = UserRepository()
    await db.update_api_key(user.user_id, hashed_key)

    from datetime import datetime
    logger.info("api_key_generated", extra={"user_id": user.user_id})

    return APIKeyResponse(
        key=raw_key,
        label=request.label,
        created_at=datetime.utcnow(),
        prefix=prefix_display,
    )


@router.delete("/api-keys", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(user=Depends(require_auth)):
    """Revoke current API key"""
    db = UserRepository()
    await db.update_api_key(user.user_id, None)
    logger.info("api_key_revoked", extra={"user_id": user.user_id})
