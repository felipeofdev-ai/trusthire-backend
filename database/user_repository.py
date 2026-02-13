"""
TrustHire User Repository
Async database operations for user management
Uses SQLAlchemy Core with asyncpg for PostgreSQL
"""

from typing import Optional
from datetime import datetime, date

from models.user_models import UserInDB, UserTier, SubscriptionStatus
from utils.logger import get_logger

logger = get_logger("database.users")


class UserRepository:
    """
    Async repository for user CRUD operations.
    
    Currently uses an in-memory store for development.
    Replace _store with actual DB calls using SQLAlchemy / asyncpg.
    
    Production setup:
        pip install asyncpg sqlalchemy[asyncio]
        DATABASE_URL=postgresql+asyncpg://user:pass@host/db
    """

    # ─── IN-MEMORY STORE (dev only) ───────────────────────────────────────────
    # In production, replace every method body with an actual DB query.
    _store: dict[str, UserInDB] = {}
    _email_index: dict[str, str] = {}  # email -> user_id
    _stripe_index: dict[str, str] = {}  # stripe_customer_id -> user_id
    _api_key_index: dict[str, str] = {}  # hashed_key -> user_id

    # ─── CREATE ───────────────────────────────────────────────────────────────

    async def create_user(
        self,
        email: str,
        name: str,
        hashed_password: str,
    ) -> UserInDB:
        user = UserInDB(
            email=email,
            name=name,
            hashed_password=hashed_password,
        )
        self._store[user.id] = user
        self._email_index[email.lower()] = user.id
        logger.info("user_created", extra={"user_id": user.id})
        return user

    # ─── READ ─────────────────────────────────────────────────────────────────

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        return self._store.get(user_id)

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        uid = self._email_index.get(email.lower())
        if uid:
            return self._store.get(uid)
        return None

    async def get_by_api_key_hash(self, hashed_key: str) -> Optional[UserInDB]:
        uid = self._api_key_index.get(hashed_key)
        if uid:
            return self._store.get(uid)
        return None

    async def get_by_stripe_customer(self, customer_id: str) -> Optional[UserInDB]:
        uid = self._stripe_index.get(customer_id)
        if uid:
            return self._store.get(uid)
        return None

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    async def update_password(self, user_id: str, hashed_password: str) -> None:
        if user_id in self._store:
            self._store[user_id].hashed_password = hashed_password
            self._store[user_id].updated_at = datetime.utcnow()

    async def update_api_key(self, user_id: str, hashed_key: Optional[str]) -> None:
        if user_id in self._store:
            user = self._store[user_id]
            # Remove old key from index
            if user.api_key_hash:
                self._api_key_index.pop(user.api_key_hash, None)
            # Set new key
            user.api_key_hash = hashed_key
            user.updated_at = datetime.utcnow()
            if hashed_key:
                self._api_key_index[hashed_key] = user_id

    async def update_stripe_customer(self, user_id: str, customer_id: str) -> None:
        if user_id in self._store:
            self._store[user_id].stripe_customer_id = customer_id
            self._store[user_id].updated_at = datetime.utcnow()
            self._stripe_index[customer_id] = user_id

    async def update_subscription(
        self,
        user_id: str,
        tier: UserTier,
        subscription_id: Optional[str],
        status: SubscriptionStatus,
    ) -> None:
        if user_id in self._store:
            user = self._store[user_id]
            user.tier = tier
            user.stripe_subscription_id = subscription_id
            user.subscription_status = status
            user.updated_at = datetime.utcnow()
            logger.info("subscription_updated", extra={
                "user_id": user_id,
                "tier": tier.value,
                "status": status.value,
            })

    async def update_subscription_status(
        self,
        user_id: str,
        status: SubscriptionStatus,
    ) -> None:
        if user_id in self._store:
            self._store[user_id].subscription_status = status
            self._store[user_id].updated_at = datetime.utcnow()

    async def increment_analysis_count(self, user_id: str) -> None:
        if user_id in self._store:
            user = self._store[user_id]
            today = date.today()
            # Reset daily counter if new day
            if user.last_analysis_date and user.last_analysis_date.date() < today:
                user.analyses_today = 0
            user.analyses_today += 1
            user.analyses_total += 1
            user.last_analysis_date = datetime.utcnow()
            user.updated_at = datetime.utcnow()

    # ─── RATE LIMIT CHECK ─────────────────────────────────────────────────────

    async def check_daily_limit(self, user_id: str) -> tuple[bool, int, int]:
        """
        Returns: (can_analyze, used_today, daily_limit)
        """
        from config import settings
        user = self._store.get(user_id)
        if not user:
            return False, 0, 0

        limits = {
            UserTier.FREE: settings.FREE_TIER_DAILY_LIMIT,
            UserTier.PRO: settings.PRO_TIER_DAILY_LIMIT,
            UserTier.ENTERPRISE: settings.ENTERPRISE_TIER_DAILY_LIMIT,
        }
        daily_limit = limits[user.tier]

        # Reset if new day
        today = date.today()
        used = user.analyses_today
        if user.last_analysis_date and user.last_analysis_date.date() < today:
            used = 0

        return used < daily_limit, used, daily_limit
