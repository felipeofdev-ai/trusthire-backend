"""
TrustHire Ultimate Configuration — SaaS Edition
Multi-language, ATS Resume Optimization, Job Scam Detection
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # ==================== APPLICATION ====================
    APP_NAME: str = "TrustHire Ultimate"
    APP_VERSION: str = "3.0.0"
    ENV: str = "dev"            # dev | staging | prod
    DEBUG: bool = False

    # ==================== API ====================
    API_V1_PREFIX: str = "/api/v1"
    API_TITLE: str = "TrustHire Ultimate API"
    API_DESCRIPTION: str = """
    AI-powered platform for:
    - Job offer verification and scam detection
    - ATS-optimized resume generation
    - Multi-language support
    - Integration with major ATS systems
    """

    # ==================== SECURITY ====================
    SECRET_KEY: str = "dev-secret-key-change-in-production-please"
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_HOSTS: str = "*"
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000,https://felipeofdev-ai.github.io,https://trusthire.dev,https://trusthire.app"

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS_STR.split(",") if o.strip()]

    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_FREE: str = "10/minute"
    RATE_LIMIT_PRO: str = "100/minute"
    RATE_LIMIT_ENTERPRISE: str = "1000/minute"

    # ==================== AI ====================
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-sonnet-4-20250514"
    AI_MAX_TOKENS: int = 4000
    AI_TIMEOUT: int = 30
    AI_TEMPERATURE: float = 0.3

    # ==================== ANALYSIS ENGINE ====================
    ENGINE_VERSION: str = "3.0.0"
    RULESET_VERSION: str = "2026.02"
    MAX_TEXT_LENGTH: int = 10000
    MIN_CONFIDENCE_THRESHOLD: float = 0.75
    ENABLE_PATTERN_ENGINE: bool = True
    ENABLE_AI_LAYER: bool = True
    ENABLE_ML_DETECTOR: bool = False
    FAIL_OPEN: bool = True

    # ==================== RESUME OPTIMIZATION ====================
    ENABLE_RESUME_OPTIMIZER: bool = True
    SUPPORTED_RESUME_FORMATS: list[str] = ["pdf", "docx", "txt"]
    MAX_RESUME_SIZE_MB: int = 5
    
    # ATS Systems supported
    SUPPORTED_ATS: list[str] = [
        "workday", "greenhouse", "lever", "bamboohr", 
        "icims", "smartrecruiters", "taleo", "jobvite"
    ]
    
    # Job boards supported
    SUPPORTED_JOB_BOARDS: list[str] = [
        "linkedin", "indeed", "glassdoor", "ziprecruiter",
        "vagas.com", "infojobs", "catho", "angellist",
        "monster", "careerbuilder"
    ]

    # ==================== INTERNATIONALIZATION ====================
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: list[str] = [
        "en",      # English
        "pt-BR",   # Portuguese (Brazil)
        "es",      # Spanish
        "fr",      # French
        "de",      # German
        "it",      # Italian
        "zh",      # Chinese
        "ja",      # Japanese
    ]

    # ==================== DATABASE ====================
    DATABASE_URL: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ==================== CACHE ====================
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    CACHE_PREFIX: str = "trusthire:"

    # ==================== MONITORING ====================
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    METRICS_ENABLED: bool = True

    # ==================== STRIPE ====================
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_PRO_MONTHLY: str = ""
    STRIPE_PRICE_PRO_YEARLY: str = ""
    STRIPE_PRICE_ENTERPRISE_MONTHLY: str = ""
    STRIPE_PRICE_ENTERPRISE_YEARLY: str = ""

    # ==================== FEATURES ====================
    FEATURE_JOB_SCAM_DETECTION: bool = True
    FEATURE_RESUME_OPTIMIZATION: bool = True
    FEATURE_ATS_COMPATIBILITY: bool = True
    FEATURE_PDF_REPORTS: bool = True
    FEATURE_DOMAIN_REPUTATION: bool = True
    FEATURE_LINK_ANALYSIS: bool = True
    FEATURE_SOCIAL_ENGINEERING: bool = True
    FEATURE_COMMUNITY_REPORTS: bool = False
    FEATURE_RECRUITER_PROFILES: bool = False
    FEATURE_MULTI_LANGUAGE: bool = True

    # ==================== TIERS ====================
    FREE_TIER_DAILY_LIMIT: int = 10
    FREE_TIER_RESUME_LIMIT: int = 3
    PRO_TIER_DAILY_LIMIT: int = 100
    PRO_TIER_RESUME_LIMIT: int = 50
    ENTERPRISE_TIER_DAILY_LIMIT: int = 10000
    ENTERPRISE_TIER_RESUME_LIMIT: int = 1000

    # ==================== EXTERNAL ====================
    VIRUSTOTAL_API_KEY: Optional[str] = None
    URLSCAN_API_KEY: Optional[str] = None

    # ==================== FILE STORAGE ====================
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def validate_production_config():
    """
    Warn about missing optional config — but NEVER crash the app.
    """
    warnings = []

    if not settings.ANTHROPIC_API_KEY:
        warnings.append("⚠️  ANTHROPIC_API_KEY not set — AI features disabled")

    if not settings.DATABASE_URL:
        warnings.append("⚠️  DATABASE_URL not set — using in-memory store")

    if not settings.STRIPE_SECRET_KEY:
        warnings.append("⚠️  STRIPE_SECRET_KEY not set — billing disabled")
    else:
        if not all([
            settings.STRIPE_PRICE_PRO_MONTHLY,
            settings.STRIPE_PRICE_PRO_YEARLY,
            settings.STRIPE_PRICE_ENTERPRISE_MONTHLY,
            settings.STRIPE_PRICE_ENTERPRISE_YEARLY
        ]):
            warnings.append("⚠️  STRIPE PRICE IDs not configured - billing may fail!")

    if "dev-secret-key" in settings.SECRET_KEY:
        warnings.append("⚠️  SECRET_KEY is default — change for production!")

    for w in warnings:
        import logging
        logging.getLogger("config").warning(w)

    return True
