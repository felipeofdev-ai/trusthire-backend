"""
Resume Optimization Models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class ResumeOptimizationRequest(BaseModel):
    resume_text: str = Field(..., min_length=100, max_length=10000)
    job_description: Optional[str] = Field(None, max_length=5000)
    target_ats: Optional[str] = None
    industry: Optional[str] = None
    language: str = "en"


class KeywordAnalysis(BaseModel):
    match_rate: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    industry_keywords_matched: List[str] = []
    industry_keywords_missing: List[str] = []
    total_job_keywords: int
    total_matched: int


class ResumeOptimizationResponse(BaseModel):
    ats_score: int
    compatibility: Dict[str, Any] = {}
    keywords: KeywordAnalysis
    suggestions: List[str]
    optimized_sections: Dict[str, str]
    format_issues: List[str]
    missing_sections: List[str]
    report: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
