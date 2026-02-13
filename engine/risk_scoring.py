"""
TrustHire Risk Scoring Engine
Calculates weighted risk scores from detected signals
"""

from typing import List, Optional, Tuple
from models.schemas import Signal, Severity, LinkAnalysis, SocialEngineeringIndicators


class RiskScoringEngine:
    """
    Multi-factor risk scoring system
    
    Combines:
    - Pattern-based signals (weighted by severity)
    - Link analysis results
    - Social engineering indicators
    - Contextual factors
    """
    
    # Base weights for signal severity
    SEVERITY_WEIGHTS = {
        Severity.INFO: 1,
        Severity.LOW: 5,
        Severity.MEDIUM: 15,
        Severity.HIGH: 30,
        Severity.CRITICAL: 50,
    }
    
    def calculate(
        self,
        signals: List[Signal],
        link_analyses: Optional[List[LinkAnalysis]] = None,
        social_engineering: Optional[SocialEngineeringIndicators] = None,
    ) -> Tuple[int, float]:
        """
        Calculate risk score and confidence
        
        Returns:
            (risk_score, confidence) tuple
            - risk_score: 0-100 integer
            - confidence: 0.0-1.0 float
        """
        if not signals and not link_analyses:
            return 0, 1.0
        
        # Base score from signals
        signal_score = self._score_signals(signals)
        
        # Link analysis score
        link_score = self._score_links(link_analyses) if link_analyses else 0
        
        # Social engineering score
        se_score = self._score_social_engineering(social_engineering) if social_engineering else 0
        
        # Combine scores with weights
        total_score = (
            signal_score * 0.60 +  # Pattern signals: 60%
            link_score * 0.25 +     # Link analysis: 25%
            se_score * 0.15         # Social engineering: 15%
        )
        
        # Clamp to 0-100
        final_score = min(max(int(total_score), 0), 100)
        
        # Calculate confidence based on signal count and agreement
        confidence = self._calculate_confidence(signals, link_analyses, social_engineering)
        
        return final_score, confidence
    
    def _score_signals(self, signals: List[Signal]) -> float:
        """Score from pattern-based signals"""
        if not signals:
            return 0.0
        
        # Weight each signal by severity and confidence
        weighted_sum = sum(
            self.SEVERITY_WEIGHTS[s.severity] * s.confidence
            for s in signals
        )
        
        # Normalize to 0-100 scale (assuming max ~5 critical signals = 250 points)
        normalized = min(weighted_sum / 2.5, 100)
        
        return normalized
    
    def _score_links(self, link_analyses: List[LinkAnalysis]) -> float:
        """Score from link analysis"""
        if not link_analyses:
            return 0.0
        
        score = 0.0
        
        for link in link_analyses:
            # Shortened URL
            if link.is_shortened:
                score += 15
            
            # Phishing detected
            if link.is_phishing:
                score += 40 * link.phishing_confidence
            
            # Domain reputation
            if link.domain_reputation:
                # Low trust score = high risk
                domain_risk = (100 - link.domain_reputation.trust_score) / 2
                score += domain_risk
            
            # VirusTotal detections
            if link.virustotal_score and link.virustotal_score > 0:
                score += min(link.virustotal_score * 10, 50)
        
        # Average across links, max 100
        return min(score / len(link_analyses), 100)
    
    def _score_social_engineering(self, se: SocialEngineeringIndicators) -> float:
        """Score from social engineering indicators"""
        if not se:
            return 0.0
        
        # Count active tactics
        tactics_score = sum([
            se.urgency_pressure * 20,
            se.emotional_manipulation * 15,
            se.isolation_tactics * 25,
            se.authority_impersonation * 20,
            se.unrealistic_promises * 20,
        ])
        
        # Apply confidence multiplier
        return min(tactics_score * se.confidence_score, 100)
    
    def _calculate_confidence(
        self,
        signals: List[Signal],
        link_analyses: Optional[List[LinkAnalysis]],
        social_engineering: Optional[SocialEngineeringIndicators],
    ) -> float:
        """
        Calculate confidence in the risk assessment
        
        Higher confidence when:
        - Multiple strong signals
        - Signals agree on risk level
        - Multiple analysis layers concur
        """
        # Start with base confidence
        confidence = 0.5
        
        # More signals = higher confidence (up to a point)
        if signals:
            signal_count = len(signals)
            confidence += min(signal_count / 10, 0.25)  # Max +0.25
            
            # Average signal confidence
            avg_signal_conf = sum(s.confidence for s in signals) / signal_count
            confidence += avg_signal_conf * 0.15  # Max +0.15
        
        # Link analysis adds confidence
        if link_analyses:
            confidence += 0.1
        
        # Social engineering detection adds confidence
        if social_engineering and social_engineering.confidence_score > 0.5:
            confidence += 0.1
        
        # Clamp to valid range
        return min(max(confidence, 0.0), 1.0)
