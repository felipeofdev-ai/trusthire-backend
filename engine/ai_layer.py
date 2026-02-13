"""
TrustHire AI Analysis Layer
Claude-powered contextual analysis and reasoning
"""

import os
import json
import asyncio
from typing import Optional, List

import anthropic
from models.schemas import AIAssessment, Signal, RiskLevel
from config import settings
from utils.logger import get_logger

logger = get_logger("ai_layer")


class AIAnalysisLayer:
    """
    AI-powered analysis using Claude
    
    Provides:
    - Contextual understanding
    - Natural language recommendations
    - Reasoning explanations
    - Confidence assessment
    """
    
    SYSTEM_PROMPT = """You are a scam detection expert analyzing job recruitment messages.

Your role is to:
1. Synthesize the detected risk signals into clear insights
2. Provide actionable recommendations
3. Explain your reasoning concisely
4. Assess confidence in your analysis

Return ONLY valid JSON with this exact structure:
{
  "summary": "Brief overview of the analysis (2-3 sentences)",
  "recommendation": "Clear action recommendation",
  "reasoning": "Explain key factors in your assessment",
  "confidence": 0.85
}

Be direct, professional, and user-focused."""
    
    def __init__(self):
        api_key = settings.ANTHROPIC_API_KEY
        self.client = anthropic.AsyncAnthropic(api_key=api_key) if api_key else None
        self.model = settings.AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.timeout = settings.AI_TIMEOUT
        self.temperature = settings.AI_TEMPERATURE
    
    async def assess(
        self,
        text: str,
        signals: List[Signal],
        risk_score: int,
        risk_level: RiskLevel,
    ) -> Optional[AIAssessment]:
        """
        Generate AI-powered assessment
        
        Args:
            text: Original message text
            signals: Detected risk signals
            risk_score: Calculated risk score
            risk_level: Risk classification
            
        Returns:
            AIAssessment or None if unavailable
        """
        if not self.client:
            logger.warning("AI layer not available (no API key)")
            return None
        
        # Prepare context
        user_message = self._build_prompt(text, signals, risk_score, risk_level)
        
        try:
            # Call Claude API with timeout
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_message}],
                ),
                timeout=self.timeout,
            )
            
            # Parse response
            content = response.content[0].text
            parsed = self._parse_response(content)
            
            if not parsed:
                logger.error("Failed to parse AI response")
                return None
            
            return AIAssessment(
                summary=parsed["summary"],
                recommendation=parsed["recommendation"],
                reasoning=parsed.get("reasoning"),
                confidence=float(parsed.get("confidence", 0.8)),
                model_version=self.model,
            )
            
        except asyncio.TimeoutError:
            logger.error("AI assessment timeout")
            return None
        except Exception as e:
            logger.error(f"AI assessment failed: {e}")
            return None
    
    def _build_prompt(
        self,
        text: str,
        signals: List[Signal],
        risk_score: int,
        risk_level: RiskLevel,
    ) -> str:
        """Build the AI prompt with context"""
        # Sanitize and truncate text
        safe_text = self._sanitize_text(text)[:2000]
        
        # Format signals
        signal_list = "\n".join(
            f"- {s.message} ({s.severity.value}, confidence: {s.confidence:.2f})"
            for s in signals
        ) if signals else "None detected"
        
        return f"""Analyze this recruitment message:

Risk Assessment:
- Score: {risk_score}/100
- Level: {risk_level.value}
- Signals detected: {len(signals)}

Detected Signals:
{signal_list}

Original Message:
{safe_text}

Provide your analysis."""
    
    def _sanitize_text(self, text: str) -> str:
        """Remove potential prompt injection attempts"""
        # Remove curly braces that could break JSON
        sanitized = text.replace("{", "").replace("}", "")
        # Remove angle brackets
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized
    
    def _parse_response(self, content: str) -> Optional[dict]:
        """Parse and validate AI response"""
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            parsed = json.loads(content)
            
            # Validate required fields
            required = ["summary", "recommendation"]
            if not all(k in parsed for k in required):
                return None
            
            # Ensure confidence is valid
            if "confidence" in parsed:
                confidence = float(parsed["confidence"])
                if not (0.0 <= confidence <= 1.0):
                    parsed["confidence"] = 0.8
            
            return parsed
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            return None
