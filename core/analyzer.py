"""
TrustHire Core Analyzer
Production-grade orchestration of all analysis engines
"""

import time
import asyncio
from typing import List, Optional
from datetime import datetime

from models.schemas import (
    AnalysisResult,
    Signal,
    RiskLevel,
    AIAssessment,
    SocialEngineeringIndicators,
)
from engine.pattern_engine import AdvancedPatternEngine
from engine.risk_scoring import RiskScoringEngine
from engine.ai_layer import AIAnalysisLayer
from services.link_analyzer import get_link_service
from config import settings
from utils.logger import get_logger
from utils.cache import get_cache_service

logger = get_logger("analyzer")


class TrustHireAnalyzer:
    """
    Main analysis orchestrator
    
    Coordinates multiple detection layers:
    1. Pattern-based detection
    2. Link/URL analysis
    3. Social engineering detection
    4. AI-powered assessment
    5. Risk scoring and classification
    """
    
    VERSION = settings.ENGINE_VERSION
    
    def __init__(self):
        self.pattern_engine = AdvancedPatternEngine()
        self.risk_engine = RiskScoringEngine()
        self.ai_layer = AIAnalysisLayer() if settings.ENABLE_AI_LAYER else None
        self.link_service = get_link_service()
        self.cache_service = get_cache_service()
    
    async def analyze(
        self,
        text: str,
        include_ai: bool = True,
        include_links: bool = True,
        user_id: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Perform comprehensive analysis
        
        Args:
            text: Message text to analyze
            include_ai: Whether to include AI analysis
            include_links: Whether to analyze embedded URLs
            user_id: Optional user identifier for tracking
            
        Returns:
            Complete analysis result with risk score and recommendations
        """
        start_time = time.time()
        
        # Input validation
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        # Truncate to max length
        text = text[:settings.MAX_TEXT_LENGTH]
        
        # Check cache
        cache_key = self._generate_cache_key(text, include_ai, include_links)
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            logger.info("analysis_cache_hit", extra={"user_id": user_id})
            return cached_result
        
        # Run detection engines concurrently
        signals, link_analyses, social_engineering = await self._run_detection_engines(
            text, include_links
        )
        
        # Calculate risk score
        risk_score, confidence = self.risk_engine.calculate(
            signals=signals,
            link_analyses=link_analyses,
            social_engineering=social_engineering,
        )
        
        # Classify risk level
        risk_level = RiskLevel.from_score(risk_score)
        
        # AI assessment (if enabled and requested)
        ai_assessment = None
        if self.ai_layer and include_ai and settings.ENABLE_AI_LAYER:
            try:
                ai_assessment = await self.ai_layer.assess(
                    text=text,
                    signals=signals,
                    risk_score=risk_score,
                    risk_level=risk_level,
                )
            except Exception as e:
                logger.error("ai_assessment_failed", exc_info=e)
                if not settings.FAIL_OPEN:
                    raise
        
        # Generate recommendation
        recommendation, action_items = self._generate_recommendation(
            risk_level=risk_level,
            signals=signals,
            ai_assessment=ai_assessment,
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Build result
        result = AnalysisResult(
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            signals=signals,
            link_analyses=link_analyses,
            social_engineering=social_engineering,
            ai_assessment=ai_assessment,
            recommendation=recommendation,
            action_items=action_items,
            engine_version=self.VERSION,
            ruleset_version=self.pattern_engine.VERSION,
            processing_time_ms=round(processing_time, 2),
        )
        
        # Cache result
        await self.cache_service.set(cache_key, result, ttl=settings.CACHE_TTL)
        
        # Log telemetry
        logger.info(
            "analysis_complete",
            extra={
                "user_id": user_id,
                "risk_score": risk_score,
                "risk_level": risk_level.value,
                "confidence": round(confidence, 2),
                "signals_count": len(signals),
                "processing_time_ms": round(processing_time, 2),
                "had_ai_assessment": ai_assessment is not None,
            },
        )
        
        return result
    
    async def _run_detection_engines(
        self,
        text: str,
        include_links: bool,
    ) -> tuple[List[Signal], List, Optional[SocialEngineeringIndicators]]:
        """Run all detection engines concurrently"""
        
        # Pattern detection (synchronous)
        signals = self.pattern_engine.scan(text)
        
        # Link analysis (async)
        link_analyses = []
        if include_links and settings.FEATURE_LINK_ANALYSIS:
            urls = self.pattern_engine.extract_urls(text)
            if urls:
                try:
                    link_analyses = await self.link_service.analyze_links(urls)
                except Exception as e:
                    logger.error("link_analysis_failed", exc_info=e)
                    if not settings.FAIL_OPEN:
                        raise
        
        # Social engineering indicators
        social_engineering = None
        if settings.FEATURE_SOCIAL_ENGINEERING:
            social_engineering = self._detect_social_engineering_indicators(signals)
        
        return signals, link_analyses, social_engineering
    
    def _detect_social_engineering_indicators(
        self,
        signals: List[Signal]
    ) -> SocialEngineeringIndicators:
        """
        Analyze signals to detect social engineering tactics
        """
        from models.schemas import SignalCategory
        
        signal_categories = {s.category for s in signals}
        
        urgency_pressure = SignalCategory.URGENCY in signal_categories
        
        emotional_manipulation = any(
            'emotional' in s.message.lower() or 'flattery' in s.message.lower()
            for s in signals
        )
        
        isolation_tactics = any(
            'isolation' in s.message.lower() or 'secrecy' in s.message.lower()
            for s in signals
        )
        
        authority_impersonation = any(
            'authority' in s.message.lower() or 'insider' in s.message.lower()
            for s in signals
        )
        
        unrealistic_promises = SignalCategory.UNREALISTIC_PROMISE in signal_categories
        
        # Calculate confidence based on detected tactics
        tactics_count = sum([
            urgency_pressure,
            emotional_manipulation,
            isolation_tactics,
            authority_impersonation,
            unrealistic_promises,
        ])
        
        confidence = min(tactics_count / 3.0, 1.0)  # Max confidence at 3+ tactics
        
        return SocialEngineeringIndicators(
            urgency_pressure=urgency_pressure,
            emotional_manipulation=emotional_manipulation,
            isolation_tactics=isolation_tactics,
            authority_impersonation=authority_impersonation,
            unrealistic_promises=unrealistic_promises,
            confidence_score=confidence,
        )
    
    def _generate_recommendation(
        self,
        risk_level: RiskLevel,
        signals: List[Signal],
        ai_assessment: Optional[AIAssessment],
    ) -> tuple[str, List[str]]:
        """
        Generate human-readable recommendation and action items
        
        Returns:
            (recommendation_text, action_items)
        """
        # Use AI recommendation if available and high confidence
        if ai_assessment and ai_assessment.confidence >= settings.MIN_CONFIDENCE_THRESHOLD:
            return ai_assessment.recommendation, self._extract_action_items(
                risk_level, signals
            )
        
        # Fallback to rule-based recommendations
        recommendations = {
            RiskLevel.SAFE: "No significant risk signals detected. This appears to be a legitimate opportunity.",
            RiskLevel.LOW: "Minor risk signals detected. Exercise normal caution when responding.",
            RiskLevel.MODERATE: "Multiple risk indicators present. Verify the company and recruiter before providing personal information.",
            RiskLevel.HIGH: "High risk of scam detected. Do not share sensitive information or make any payments.",
            RiskLevel.CRITICAL: "Critical scam indicators detected. Do not engage with this opportunity under any circumstances.",
        }
        
        recommendation = recommendations[risk_level]
        action_items = self._extract_action_items(risk_level, signals)
        
        return recommendation, action_items
    
    def _extract_action_items(
        self,
        risk_level: RiskLevel,
        signals: List[Signal],
    ) -> List[str]:
        """Extract actionable items based on detected signals"""
        from models.schemas import SignalCategory, Severity
        
        action_items = []
        
        if risk_level in [RiskLevel.SAFE, RiskLevel.LOW]:
            action_items.append("Research the company on LinkedIn and Glassdoor")
            action_items.append("Verify recruiter's identity through official channels")
            return action_items
        
        # High-severity signals
        critical_signals = [s for s in signals if s.severity == Severity.CRITICAL]
        
        if any(s.category == SignalCategory.FINANCIAL for s in critical_signals):
            action_items.append("DO NOT send money or cryptocurrency")
            action_items.append("Legitimate employers never ask for upfront payments")
        
        if any(s.category == SignalCategory.PERSONAL_DATA for s in critical_signals):
            action_items.append("DO NOT share SSN, passwords, or bank details")
            action_items.append("Report this as a phishing attempt")
        
        if any(s.category == SignalCategory.PHISHING for s in signals):
            action_items.append("Do not click any links")
            action_items.append("Verify sender through official company website")
        
        if any(s.category == SignalCategory.OFF_PLATFORM for s in signals):
            action_items.append("Communicate only through official job platform")
            action_items.append("Be suspicious of off-platform requests")
        
        if any(s.category == SignalCategory.URGENCY for s in signals):
            action_items.append("Take time to research - urgency is a manipulation tactic")
        
        # Generic high-risk actions
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            action_items.append("Report this message to the platform/authorities")
            action_items.append("Block sender and do not respond")
        
        return action_items[:6]  # Limit to 6 most relevant items
    
    def _generate_cache_key(
        self,
        text: str,
        include_ai: bool,
        include_links: bool,
    ) -> str:
        """Generate cache key for analysis"""
        import hashlib
        
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        flags = f"ai{int(include_ai)}link{int(include_links)}"
        
        return f"analysis:{text_hash}:{flags}:{self.VERSION}"


# Singleton instance
_analyzer = None

def get_analyzer() -> TrustHireAnalyzer:
    """Get singleton analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = TrustHireAnalyzer()
    return _analyzer
