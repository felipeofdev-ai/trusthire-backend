"""
Tests for Pattern Engine
"""

import pytest
from engine.pattern_engine import AdvancedPatternEngine
from models import SignalCategory, Severity


def test_financial_pattern_detection():
    """Test detection of financial requests"""
    engine = AdvancedPatternEngine()
    
    text = "Please send $500 via PayPal for processing fee"
    signals = engine.scan(text)
    
    financial_signals = [s for s in signals if s.category == SignalCategory.FINANCIAL]
    assert len(financial_signals) > 0
    assert any(s.severity == Severity.CRITICAL for s in financial_signals)


def test_cryptocurrency_detection():
    """Test detection of cryptocurrency mentions"""
    engine = AdvancedPatternEngine()
    
    text = "Send 0.05 BTC to this wallet address"
    signals = engine.scan(text)
    
    assert any(s.category == SignalCategory.FINANCIAL for s in signals)
    assert any("crypto" in s.message.lower() for s in signals)


def test_urgency_detection():
    """Test detection of urgency pressure"""
    engine = AdvancedPatternEngine()
    
    text = "URGENT! Respond immediately or lose this opportunity"
    signals = engine.scan(text)
    
    urgency_signals = [s for s in signals if s.category == SignalCategory.URGENCY]
    assert len(urgency_signals) > 0


def test_phishing_detection():
    """Test detection of phishing patterns"""
    engine = AdvancedPatternEngine()
    
    text = "Click here to verify your account"
    signals = engine.scan(text)
    
    phishing_signals = [s for s in signals if s.category == SignalCategory.PHISHING]
    assert len(phishing_signals) > 0


def test_url_extraction():
    """Test URL extraction"""
    engine = AdvancedPatternEngine()
    
    text = "Visit https://example.com and http://test.org"
    urls = engine.extract_urls(text)
    
    assert len(urls) == 2
    assert "https://example.com" in urls
    assert "http://test.org" in urls


def test_email_extraction():
    """Test email extraction"""
    engine = AdvancedPatternEngine()
    
    text = "Contact us at support@example.com or sales@test.org"
    emails = engine.extract_emails(text)
    
    assert len(emails) == 2
    assert "support@example.com" in emails
    assert "sales@test.org" in emails


def test_domain_extraction():
    """Test domain extraction from URLs and emails"""
    engine = AdvancedPatternEngine()
    
    text = "Visit https://example.com and email test@domain.org"
    domains = engine.extract_domains(text)
    
    assert "example.com" in domains
    assert "domain.org" in domains


def test_combo_detection():
    """Test detection of dangerous signal combinations"""
    engine = AdvancedPatternEngine()
    
    # Urgency + Financial = Critical combo
    text = "URGENT! Send $1000 today or lose this job opportunity!"
    signals = engine.scan(text)
    
    # Should have both individual signals + combo signal
    categories = {s.category for s in signals}
    assert SignalCategory.URGENCY in categories
    assert SignalCategory.FINANCIAL in categories
    assert SignalCategory.SOCIAL_ENGINEERING in categories  # Combo signal


def test_social_engineering_isolation():
    """Test detection of isolation tactics"""
    engine = AdvancedPatternEngine()
    
    text = "Don't tell anyone about this opportunity, it's confidential"
    signals = engine.scan(text)
    
    se_signals = [s for s in signals if s.category == SignalCategory.SOCIAL_ENGINEERING]
    assert len(se_signals) > 0
    assert any("isolation" in s.message.lower() for s in se_signals)
