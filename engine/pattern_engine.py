"""
TrustHire Advanced Pattern Detection Engine
Multi-layered rule-based scam detection with confidence scoring
"""

import re
from typing import List, Tuple, Pattern
from dataclasses import dataclass

from models.schemas import Signal, Severity, SignalCategory
from config import settings


@dataclass
class PatternRule:
    """Pattern detection rule"""
    pattern: Pattern
    category: SignalCategory
    message: str
    severity: Severity
    confidence: float = 0.9
    evidence_extractor: callable = None


class AdvancedPatternEngine:
    """
    Production-grade pattern detection with:
    - Multi-category rules
    - Confidence scoring
    - Evidence extraction
    - Contextual analysis
    - Combo detection
    """
    
    VERSION = settings.RULESET_VERSION
    
    def __init__(self):
        self.rules = self._initialize_rules()
        self.combo_rules = self._initialize_combo_rules()
    
    # ==================== RULE DEFINITIONS ====================
    
    def _initialize_rules(self) -> List[PatternRule]:
        """Initialize all detection rules"""
        return [
            # ---------- FINANCIAL SIGNALS ----------
            PatternRule(
                pattern=re.compile(
                    r"\b(pay|payment|transfer|send\s+money|wire|pix|paypal|venmo|cashapp|zelle)\b.*?\$?\d+",
                    re.I
                ),
                category=SignalCategory.FINANCIAL,
                message="Requests monetary payment",
                severity=Severity.CRITICAL,
                confidence=0.95,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(bitcoin|btc|crypto|ethereum|eth|usdt|blockchain|wallet\s+address)\b",
                    re.I
                ),
                category=SignalCategory.FINANCIAL,
                message="Mentions cryptocurrency payment",
                severity=Severity.CRITICAL,
                confidence=0.98,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(processing\s+fee|registration\s+fee|training\s+fee|starter\s+kit|equipment\s+cost)\b",
                    re.I
                ),
                category=SignalCategory.FINANCIAL,
                message="Mentions upfront fees",
                severity=Severity.HIGH,
                confidence=0.92,
            ),
            
            # ---------- URGENCY PRESSURE ----------
            PatternRule(
                pattern=re.compile(
                    r"\b(urgent|immediately|right\s+now|asap|today\s+only|limited\s+time|act\s+fast|hurry)\b",
                    re.I
                ),
                category=SignalCategory.URGENCY,
                message="Creates artificial urgency",
                severity=Severity.MEDIUM,
                confidence=0.85,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(respond\s+within|deadline\s+(today|tonight)|expires?\s+(today|soon)|last\s+chance)\b",
                    re.I
                ),
                category=SignalCategory.URGENCY,
                message="Imposes strict time pressure",
                severity=Severity.HIGH,
                confidence=0.90,
            ),
            
            # ---------- PERSONAL DATA REQUESTS ----------
            PatternRule(
                pattern=re.compile(
                    r"\b(ssn|social\s+security|cpf|tax\s+id|passport\s+number|driver.?s?\s+license)\b",
                    re.I
                ),
                category=SignalCategory.PERSONAL_DATA,
                message="Requests sensitive government ID",
                severity=Severity.CRITICAL,
                confidence=0.98,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(password|login\s+credentials|account\s+access|security\s+code|pin\s+number)\b",
                    re.I
                ),
                category=SignalCategory.PERSONAL_DATA,
                message="Requests login credentials",
                severity=Severity.CRITICAL,
                confidence=0.99,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(bank\s+account|routing\s+number|credit\s+card|debit\s+card|card\s+number|cvv)\b",
                    re.I
                ),
                category=SignalCategory.PERSONAL_DATA,
                message="Requests financial account details",
                severity=Severity.CRITICAL,
                confidence=0.99,
            ),
            
            # ---------- UNREALISTIC PROMISES ----------
            PatternRule(
                pattern=re.compile(
                    r"\b(guaranteed\s+(job|income|salary)|no\s+experience\s+(needed|required)|easy\s+money)\b",
                    re.I
                ),
                category=SignalCategory.UNREALISTIC_PROMISE,
                message="Makes unrealistic job guarantees",
                severity=Severity.HIGH,
                confidence=0.88,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\$\d{1,3},?\d{3,}\+?\s*(per|a|\/)\s*(day|week|hour|month).*\bwork\s+from\s+home\b",
                    re.I
                ),
                category=SignalCategory.UNREALISTIC_PROMISE,
                message="Promises unusually high salary for remote work",
                severity=Severity.HIGH,
                confidence=0.85,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(become\s+rich|financial\s+freedom|life-?changing\s+opportunity|quit\s+your\s+job)\b",
                    re.I
                ),
                category=SignalCategory.UNREALISTIC_PROMISE,
                message="Uses get-rich-quick language",
                severity=Severity.MEDIUM,
                confidence=0.80,
            ),
            
            # ---------- OFF-PLATFORM COMMUNICATION ----------
            PatternRule(
                pattern=re.compile(
                    r"\b(whatsapp|telegram|signal|discord|wickr|kik)\b",
                    re.I
                ),
                category=SignalCategory.OFF_PLATFORM,
                message="Requests communication via messaging app",
                severity=Severity.MEDIUM,
                confidence=0.87,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(contact\s+me\s+at|reach\s+me\s+on|message\s+me\s+on)\s+[a-z]+@(?!gmail|yahoo|outlook|hotmail)",
                    re.I
                ),
                category=SignalCategory.OFF_PLATFORM,
                message="Provides non-professional contact method",
                severity=Severity.LOW,
                confidence=0.75,
            ),
            
            # ---------- SUSPICIOUS LINKS ----------
            PatternRule(
                pattern=re.compile(
                    r"https?://[^\s]+\.(xyz|top|click|gq|ml|tk|cf|ga|work|online|site)\b",
                    re.I
                ),
                category=SignalCategory.SUSPICIOUS_LINK,
                message="Contains link with suspicious domain extension",
                severity=Severity.HIGH,
                confidence=0.92,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"https?://(bit\.ly|tinyurl|short\.io|rb\.gy|cutt\.ly|t\.co)/",
                    re.I
                ),
                category=SignalCategory.SUSPICIOUS_LINK,
                message="Uses URL shortener (hides destination)",
                severity=Severity.MEDIUM,
                confidence=0.70,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"https?://[^\s]*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
                ),
                category=SignalCategory.SUSPICIOUS_LINK,
                message="Link uses IP address instead of domain",
                severity=Severity.HIGH,
                confidence=0.88,
            ),
            
            # ---------- PHISHING INDICATORS ----------
            PatternRule(
                pattern=re.compile(
                    r"\b(verify\s+your\s+account|confirm\s+your\s+(identity|email)|update\s+your\s+information)\b",
                    re.I
                ),
                category=SignalCategory.PHISHING,
                message="Classic phishing verification request",
                severity=Severity.CRITICAL,
                confidence=0.90,
            ),
            
            PatternRule(
                pattern=re.compile(
                    r"\b(click\s+(here|this\s+link|below)|download\s+attachment|open\s+the\s+file)\b",
                    re.I
                ),
                category=SignalCategory.PHISHING,
                message="Suspicious call-to-action",
                severity=Severity.MEDIUM,
                confidence=0.75,
            ),
            
            # ---------- ENCODING/OBFUSCATION ----------
            PatternRule(
                pattern=re.compile(
                    r"[A-Za-z0-9+/]{40,}={0,2}"
                ),
                category=SignalCategory.PHISHING,
                message="Suspicious encoded payload detected",
                severity=Severity.CRITICAL,
                confidence=0.95,
            ),
        ]
    
    def _initialize_combo_rules(self) -> List[Tuple[List[SignalCategory], str, Severity]]:
        """Initialize combination rules (patterns that appear together)"""
        return [
            (
                [SignalCategory.URGENCY, SignalCategory.FINANCIAL],
                "Urgency combined with payment request - high scam indicator",
                Severity.CRITICAL,
            ),
            (
                [SignalCategory.PHISHING, SignalCategory.SUSPICIOUS_LINK],
                "Phishing language with suspicious link",
                Severity.CRITICAL,
            ),
            (
                [SignalCategory.UNREALISTIC_PROMISE, SignalCategory.FINANCIAL],
                "Unrealistic promises requiring upfront payment",
                Severity.CRITICAL,
            ),
            (
                [SignalCategory.OFF_PLATFORM, SignalCategory.URGENCY],
                "Urgency to move conversation off platform",
                Severity.HIGH,
            ),
            (
                [SignalCategory.PERSONAL_DATA, SignalCategory.URGENCY],
                "Urgent request for sensitive information",
                Severity.CRITICAL,
            ),
        ]
    
    # ==================== DETECTION ====================
    
    def scan(self, text: str) -> List[Signal]:
        """
        Scan text for all patterns
        
        Returns:
            List of detected signals with confidence scores
        """
        signals = []
        
        # Run pattern matching
        for rule in self.rules:
            match = rule.pattern.search(text)
            if match:
                evidence = match.group(0) if len(match.group(0)) < 100 else match.group(0)[:100] + "..."
                
                signals.append(
                    Signal(
                        category=rule.category,
                        message=rule.message,
                        severity=rule.severity,
                        confidence=rule.confidence,
                        evidence=evidence,
                    )
                )
        
        # Detect combinations
        combo_signals = self._detect_combos(signals, text)
        signals.extend(combo_signals)
        
        # Detect social engineering patterns
        se_signals = self._detect_social_engineering(text)
        signals.extend(se_signals)
        
        return signals
    
    def _detect_combos(self, signals: List[Signal], text: str) -> List[Signal]:
        """Detect dangerous signal combinations"""
        found_categories = {s.category for s in signals}
        combo_signals = []
        
        for required_cats, message, severity in self.combo_rules:
            if all(cat in found_categories for cat in required_cats):
                combo_signals.append(
                    Signal(
                        category=SignalCategory.SOCIAL_ENGINEERING,
                        message=message,
                        severity=severity,
                        confidence=0.95,
                    )
                )
        
        return combo_signals
    
    def _detect_social_engineering(self, text: str) -> List[Signal]:
        """Detect advanced social engineering tactics"""
        signals = []
        lower_text = text.lower()
        
        # Isolation tactics
        isolation_patterns = [
            "don't tell anyone",
            "keep this confidential",
            "this is between us",
            "don't share this",
            "private opportunity",
        ]
        if any(p in lower_text for p in isolation_patterns):
            signals.append(
                Signal(
                    category=SignalCategory.SOCIAL_ENGINEERING,
                    message="Uses isolation tactics (secrecy)",
                    severity=Severity.HIGH,
                    confidence=0.88,
                )
            )
        
        # Authority impersonation
        authority_patterns = [
            "from corporate",
            "head office",
            "ceo personally selected",
            "executive team",
            "management approved",
        ]
        if any(p in lower_text for p in authority_patterns):
            signals.append(
                Signal(
                    category=SignalCategory.SOCIAL_ENGINEERING,
                    message="Claims authority/insider status",
                    severity=Severity.MEDIUM,
                    confidence=0.75,
                )
            )
        
        # Emotional manipulation
        emotional_patterns = [
            "you've been chosen",
            "lucky to be selected",
            "special candidate",
            "perfect fit",
            "dream opportunity",
        ]
        if any(p in lower_text for p in emotional_patterns):
            signals.append(
                Signal(
                    category=SignalCategory.SOCIAL_ENGINEERING,
                    message="Uses emotional manipulation/flattery",
                    severity=Severity.LOW,
                    confidence=0.70,
                )
            )
        
        return signals
    
    # ==================== UTILITIES ====================
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from text"""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.findall(text)
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        return email_pattern.findall(text)
    
    def extract_domains(self, text: str) -> List[str]:
        """Extract domain names from URLs and emails"""
        domains = []
        
        # From URLs
        urls = self.extract_urls(text)
        for url in urls:
            match = re.search(r'://([^/]+)', url)
            if match:
                domains.append(match.group(1))
        
        # From emails
        emails = self.extract_emails(text)
        for email in emails:
            domain = email.split('@')[1]
            domains.append(domain)
        
        return list(set(domains))
