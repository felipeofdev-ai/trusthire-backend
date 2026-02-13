"""
TrustHire Data Models
Production-grade data structures with validation
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from uuid import uuid4


# ==================== ENUMS ====================

class RiskLevel(str, Enum):
    """Risk classification levels"""
    SAFE = "safe"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_score(cls, score: int) -> "RiskLevel":
        """Convert numeric score to risk level"""
        if score < 20:
            return cls.SAFE
        elif score < 40:
            return cls.LOW
        elif score < 60:
            return cls.MODERATE
        elif score < 80:
            return cls.HIGH
        else:
            return cls.CRITICAL


class Severity(str, Enum):
    """Signal severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    def weight(self) -> int:
        """Get numeric weight for scoring"""
        weights = {
            self.INFO: 1,
            self.LOW: 5,
            self.MEDIUM: 15,
            self.HIGH: 30,
            self.CRITICAL: 50,
        }
        return weights[self]


class SignalCategory(str, Enum):
    """Categories of risk signals"""
    FINANCIAL = "financial"
    URGENCY = "urgency"
    PERSONAL_DATA = "personal_data"
    UNREALISTIC_PROMISE = "unrealistic_promise"
    OFF_PLATFORM = "off_platform"
    SUSPICIOUS_LINK = "suspicious_link"
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    DOMAIN_REPUTATION = "domain_reputation"
    LINGUISTIC_PATTERN = "linguistic_pattern"


class UserTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ==================== REQUEST MODELS ====================

class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., min_length=10, max_length=10000)
    include_ai_analysis: bool = Field(default=True)
    include_link_scan: bool = Field(default=True)
    user_id: Optional[str] = None
    
    @validator('text')
    def sanitize_text(cls, v):
        """Remove potential injection attempts"""
        # Remove null bytes
        v = v.replace('\x00', '')
        # Limit consecutive whitespace
        import re
        v = re.sub(r'\s+', ' ', v)
        return v.strip()


class FeedbackRequest(BaseModel):
    """User feedback on analysis results"""
    analysis_id: str
    was_accurate: bool
    actual_outcome: Optional[str] = None  # "scam" | "legitimate"
    comments: Optional[str] = Field(None, max_length=500)
    user_id: Optional[str] = None


class ReportScamRequest(BaseModel):
    """Community scam reporting"""
    message_text: str = Field(..., max_length=5000)
    recruiter_email: Optional[str] = None
    company_name: Optional[str] = None
    domain: Optional[str] = None
    evidence_urls: List[HttpUrl] = Field(default_factory=list, max_items=5)
    description: str = Field(..., max_length=1000)
    reported_by: Optional[str] = None


# ==================== RESPONSE MODELS ====================

class Signal(BaseModel):
    """Individual risk signal detected"""
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    category: SignalCategory
    message: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4",
                "category": "financial",
                "message": "Requests upfront payment",
                "severity": "critical",
                "confidence": 0.95,
                "evidence": "mentions 'send $500'"
            }
        }


class DomainReputation(BaseModel):
    """Domain trust information"""
    domain: str
    is_trusted: bool
    trust_score: int = Field(ge=0, le=100)
    report_count: int = 0
    verified: bool = False
    verification_source: Optional[str] = None
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class LinkAnalysis(BaseModel):
    """Analysis of URLs in message"""
    url: str
    is_shortened: bool
    final_url: Optional[str] = None
    domain_reputation: Optional[DomainReputation] = None
    is_phishing: bool = False
    phishing_confidence: float = 0.0
    virustotal_score: Optional[int] = None


class SocialEngineeringIndicators(BaseModel):
    """Social engineering tactics detected"""
    urgency_pressure: bool = False
    emotional_manipulation: bool = False
    isolation_tactics: bool = False
    authority_impersonation: bool = False
    unrealistic_promises: bool = False
    confidence_score: float = Field(ge=0.0, le=1.0)


class AIAssessment(BaseModel):
    """AI-generated analysis"""
    summary: str
    recommendation: str
    reasoning: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str


class RecruiterProfile(BaseModel):
    """Recruiter reputation tracking"""
    email: Optional[str] = None
    domain: Optional[str] = None
    historical_risk_score: int = Field(ge=0, le=100)
    total_analyses: int = 0
    scam_reports: int = 0
    legitimate_confirmations: int = 0
    first_seen: datetime
    last_seen: datetime


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    # Identification
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Scoring
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Detection Results
    signals: List[Signal] = Field(default_factory=list)
    link_analyses: List[LinkAnalysis] = Field(default_factory=list)
    social_engineering: Optional[SocialEngineeringIndicators] = None
    recruiter_profile: Optional[RecruiterProfile] = None
    
    # AI Analysis
    ai_assessment: Optional[AIAssessment] = None
    
    # Recommendations
    recommendation: str
    action_items: List[str] = Field(default_factory=list)
    
    # Metadata
    engine_version: str
    ruleset_version: str
    processing_time_ms: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "risk_score": 75,
                "risk_level": "high",
                "confidence": 0.92,
                "signals": [
                    {
                        "category": "financial",
                        "message": "Requests payment via cryptocurrency",
                        "severity": "critical",
                        "confidence": 0.98
                    }
                ],
                "recommendation": "Do not engage. High risk of financial scam.",
                "engine_version": "2.0.0"
            }
        }


# ==================== DATABASE MODELS ====================

class AnalysisRecord(BaseModel):
    """Database record for analysis"""
    id: str
    user_id: Optional[str]
    text_hash: str  # SHA256 of analyzed text
    result: AnalysisResult
    created_at: datetime
    user_tier: UserTier
    feedback_provided: bool = False


class DomainRecord(BaseModel):
    """Trusted/flagged domain database entry"""
    domain: str
    status: str  # trusted, flagged, unknown
    trust_score: int
    report_count: int
    verified: bool
    verification_source: Optional[str]
    created_at: datetime
    updated_at: datetime


class ScamReport(BaseModel):
    """Community scam report"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    message_text: str
    recruiter_email: Optional[str]
    company_name: Optional[str]
    domain: Optional[str]
    evidence_urls: List[str]
    description: str
    reported_by: Optional[str]
    status: str = "pending"  # pending, verified, false_positive
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None


# ==================== STATS MODELS ====================

class UsageStats(BaseModel):
    """User usage statistics"""
    user_id: str
    tier: UserTier
    analyses_today: int = 0
    analyses_total: int = 0
    last_analysis: Optional[datetime] = None
    daily_limit: int
    
    def can_analyze(self) -> bool:
        """Check if user can perform analysis"""
        return self.analyses_today < self.daily_limit


class SystemStats(BaseModel):
    """System-wide statistics"""
    total_analyses: int
    analyses_24h: int
    average_risk_score: float
    high_risk_percentage: float
    average_processing_time_ms: float
    cache_hit_rate: float
    top_risk_signals: Dict[str, int]
