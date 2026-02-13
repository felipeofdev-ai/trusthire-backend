"""
Tests for TrustHire Analyzer
"""

import pytest
from core.analyzer import TrustHireAnalyzer
from models import RiskLevel


@pytest.mark.asyncio
async def test_critical_scam_detection():
    """Test detection of obvious scam"""
    analyzer = TrustHireAnalyzer()
    
    scam_message = """
    URGENT! You've been selected for a high-paying remote job!
    Send $500 via Bitcoin to secure your position.
    Contact me immediately on Telegram: @scammer123
    Click here to verify: http://fake-job.xyz/verify
    """
    
    result = await analyzer.analyze(scam_message, include_ai=False, include_links=False)
    
    assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert result.risk_score > 70
    assert len(result.signals) >= 3
    assert any("payment" in s.message.lower() or "bitcoin" in s.message.lower() for s in result.signals)
    assert any("urgent" in s.message.lower() for s in result.signals)


@pytest.mark.asyncio
async def test_legitimate_message():
    """Test that legitimate messages score low"""
    analyzer = TrustHireAnalyzer()
    
    legit_message = """
    Hi! We're hiring a Senior Python Developer at Google.
    
    Requirements:
    - 5+ years Python experience
    - FastAPI knowledge
    - Remote work available
    
    Salary: $150k-$200k
    
    Apply at careers.google.com
    """
    
    result = await analyzer.analyze(legit_message, include_ai=False, include_links=False)
    
    assert result.risk_level in [RiskLevel.SAFE, RiskLevel.LOW]
    assert result.risk_score < 40


@pytest.mark.asyncio
async def test_personal_data_request():
    """Test detection of sensitive data requests"""
    analyzer = TrustHireAnalyzer()
    
    message = """
    Please provide your SSN and bank account details
    for background check and direct deposit setup.
    """
    
    result = await analyzer.analyze(message, include_ai=False, include_links=False)
    
    assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert any("personal" in s.message.lower() or "sensitive" in s.message.lower() for s in result.signals)


@pytest.mark.asyncio
async def test_empty_text():
    """Test that empty text raises ValueError"""
    analyzer = TrustHireAnalyzer()
    
    with pytest.raises(ValueError):
        await analyzer.analyze("")
    
    with pytest.raises(ValueError):
        await analyzer.analyze("   ")


@pytest.mark.asyncio
async def test_confidence_score():
    """Test that confidence scores are valid"""
    analyzer = TrustHireAnalyzer()
    
    result = await analyzer.analyze("Test message", include_ai=False, include_links=False)
    
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.confidence, float)


@pytest.mark.asyncio
async def test_engine_version():
    """Test that engine version is included"""
    analyzer = TrustHireAnalyzer()
    
    result = await analyzer.analyze("Test message", include_ai=False, include_links=False)
    
    assert result.engine_version is not None
    assert result.ruleset_version is not None
