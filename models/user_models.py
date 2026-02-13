"""
TrustHire User & Auth Models
Pydantic schemas for auth, users, and SaaS subscription management
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from uuid import uuid4


# ==================== ENUMS ====================

class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"


# ==================== AUTH ====================

class TokenData(BaseModel):
    """Decoded JWT payload"""
    user_id: str
    tier: UserTier = UserTier.FREE


class Token(BaseModel):
    """Auth tokens response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24h in seconds
    tier: UserTier


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# ==================== USER ====================

class UserPublic(BaseModel):
    """Safe user data for public API responses"""
    id: str
    email: str
    name: str
    tier: UserTier
    created_at: datetime
    analyses_today: int = 0
    analyses_total: int = 0
    daily_limit: int

    @property
    def can_analyze(self) -> bool:
        return self.analyses_today < self.daily_limit


class UserInDB(BaseModel):
    """Full user record (internal only — never expose hashed_password)"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    email: str
    name: str
    hashed_password: str
    tier: UserTier = UserTier.FREE
    is_active: bool = True
    is_verified: bool = False
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: Optional[SubscriptionStatus] = None
    api_key_hash: Optional[str] = None  # Only ONE active key per user
    analyses_today: int = 0
    analyses_total: int = 0
    last_analysis_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_public(self) -> UserPublic:
        from config import settings
        limits = {
            UserTier.FREE: settings.FREE_TIER_DAILY_LIMIT,
            UserTier.PRO: settings.PRO_TIER_DAILY_LIMIT,
            UserTier.ENTERPRISE: settings.ENTERPRISE_TIER_DAILY_LIMIT,
        }
        return UserPublic(
            id=self.id,
            email=self.email,
            name=self.name,
            tier=self.tier,
            created_at=self.created_at,
            analyses_today=self.analyses_today,
            analyses_total=self.analyses_total,
            daily_limit=limits[self.tier],
        )


# ==================== API KEYS ====================

class APIKeyCreate(BaseModel):
    """Request to generate a new API key"""
    label: Optional[str] = Field(None, max_length=50)


class APIKeyResponse(BaseModel):
    """API key creation response (key shown ONCE)"""
    key: str  # Raw key — shown once, never stored
    label: Optional[str]
    created_at: datetime
    prefix: str  # e.g. "th_abc123..." (first 10 chars for identification)


# ==================== SUBSCRIPTION ====================

class PlanInfo(BaseModel):
    """Pricing plan details"""
    id: str
    name: str
    tier: UserTier
    price_monthly: float
    price_yearly: float
    daily_limit: int
    features: List[str]
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None


class SubscriptionInfo(BaseModel):
    """Current subscription details"""
    tier: UserTier
    status: Optional[SubscriptionStatus]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool = False
    stripe_subscription_id: Optional[str] = None


class CheckoutRequest(BaseModel):
    """Create Stripe checkout session"""
    plan: str  # "pro_monthly" | "pro_yearly" | "enterprise_monthly"
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    """Stripe checkout session URL"""
    checkout_url: str
    session_id: str


class PortalRequest(BaseModel):
    """Create Stripe billing portal session"""
    return_url: str


class PortalResponse(BaseModel):
    portal_url: str
