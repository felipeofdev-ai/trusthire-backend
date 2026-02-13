"""
TrustHire Link Analysis Service
Analyzes URLs for phishing, malware, and domain reputation
"""

import re
import asyncio
import httpx
from typing import List, Optional
from urllib.parse import urlparse

from models.schemas import LinkAnalysis, DomainReputation
from config import settings
from utils.logger import get_logger

logger = get_logger("link_analyzer")


class LinkAnalysisService:
    """
    Analyzes URLs for safety:
    - URL shortener expansion
    - Domain reputation checking
    - Phishing detection
    - External threat intelligence integration
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(5.0)
        self.shorteners = {
            'bit.ly', 'tinyurl.com', 'short.io', 'rb.gy',
            'cutt.ly', 't.co', 'ow.ly', 'is.gd',
        }
        self.suspicious_tlds = {
            '.xyz', '.top', '.click', '.gq', '.ml',
            '.tk', '.cf', '.ga', '.work', '.online',
        }
    
    async def analyze_links(self, urls: List[str]) -> List[LinkAnalysis]:
        """
        Analyze multiple URLs concurrently
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            List of LinkAnalysis results
        """
        if not urls:
            return []
        
        tasks = [self._analyze_single_url(url) for url in urls[:10]]  # Limit to 10
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        analyses = []
        for result in results:
            if isinstance(result, LinkAnalysis):
                analyses.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Link analysis failed: {result}")
        
        return analyses
    
    async def _analyze_single_url(self, url: str) -> LinkAnalysis:
        """Analyze a single URL"""
        try:
            # Parse URL
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check if shortened
            is_shortened = domain in self.shorteners
            
            # Expand if shortened
            final_url = None
            if is_shortened:
                final_url = await self._expand_url(url)
                if final_url:
                    parsed = urlparse(final_url)
                    domain = parsed.netloc.lower()
            
            # Check domain reputation
            domain_rep = await self._check_domain_reputation(domain)
            
            # Phishing detection
            is_phishing, phishing_confidence = self._detect_phishing_patterns(url, parsed)
            
            # VirusTotal check (if API key provided)
            vt_score = None
            if settings.VIRUSTOTAL_API_KEY:
                vt_score = await self._check_virustotal(url)
            
            return LinkAnalysis(
                url=url,
                is_shortened=is_shortened,
                final_url=final_url,
                domain_reputation=domain_rep,
                is_phishing=is_phishing,
                phishing_confidence=phishing_confidence,
                virustotal_score=vt_score,
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze URL {url}: {e}")
            # Return minimal analysis
            return LinkAnalysis(
                url=url,
                is_shortened=False,
                is_phishing=False,
                phishing_confidence=0.0,
            )
    
    async def _expand_url(self, short_url: str) -> Optional[str]:
        """Expand shortened URL to final destination"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.head(short_url)
                return str(response.url)
        except Exception as e:
            logger.debug(f"Failed to expand URL {short_url}: {e}")
            return None
    
    async def _check_domain_reputation(self, domain: str) -> Optional[DomainReputation]:
        """
        Check domain reputation from database/cache
        
        In production, this would query:
        - Internal database of flagged domains
        - Cached threat intelligence feeds
        - Community reports
        """
        # TODO: Implement database lookup
        # For now, do basic heuristic checks
        
        is_trusted = self._is_known_trusted_domain(domain)
        trust_score = 80 if is_trusted else 50
        
        # Lower score for suspicious TLDs
        if any(domain.endswith(tld) for tld in self.suspicious_tlds):
            trust_score = 20
        
        return DomainReputation(
            domain=domain,
            is_trusted=is_trusted,
            trust_score=trust_score,
            verified=is_trusted,
        )
    
    def _is_known_trusted_domain(self, domain: str) -> bool:
        """Check if domain is from known trusted company"""
        trusted_domains = {
            # Tech companies
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'meta.com', 'facebook.com', 'instagram.com', 'linkedin.com',
            
            # Job boards
            'indeed.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com',
            'lever.co', 'greenhouse.io', 'workday.com',
            
            # Email providers
            'gmail.com', 'outlook.com', 'yahoo.com', 'protonmail.com',
        }
        
        # Check exact match or subdomain
        for trusted in trusted_domains:
            if domain == trusted or domain.endswith('.' + trusted):
                return True
        
        return False
    
    def _detect_phishing_patterns(self, url: str, parsed) -> tuple[bool, float]:
        """
        Detect phishing indicators in URL structure
        
        Returns:
            (is_phishing, confidence)
        """
        confidence = 0.0
        indicators = []
        
        # Check for IP address instead of domain
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parsed.netloc):
            indicators.append("Uses IP address")
            confidence += 0.3
        
        # Check for excessive subdomains
        if parsed.netloc.count('.') > 3:
            indicators.append("Excessive subdomains")
            confidence += 0.2
        
        # Check for typosquatting (e.g., paypa1.com instead of paypal.com)
        common_brands = ['google', 'microsoft', 'amazon', 'paypal', 'apple', 'linkedin']
        for brand in common_brands:
            if brand in parsed.netloc.lower() and not self._is_known_trusted_domain(parsed.netloc):
                indicators.append(f"Possible {brand} typosquatting")
                confidence += 0.4
        
        # Check for misleading path
        if '@' in url:
            indicators.append("Contains @ symbol (URL obfuscation)")
            confidence += 0.3
        
        # Check for suspicious keywords in path
        suspicious_keywords = ['verify', 'secure', 'account', 'login', 'signin', 'update']
        path_lower = parsed.path.lower()
        if any(keyword in path_lower for keyword in suspicious_keywords):
            indicators.append("Suspicious keywords in path")
            confidence += 0.15
        
        is_phishing = confidence >= 0.5
        
        if indicators:
            logger.debug(f"Phishing indicators for {url}: {indicators}")
        
        return is_phishing, min(confidence, 1.0)
    
    async def _check_virustotal(self, url: str) -> Optional[int]:
        """
        Check URL against VirusTotal
        
        Returns:
            Number of detections (0 = clean)
        """
        if not settings.VIRUSTOTAL_API_KEY:
            return None
        
        try:
            # Simplified - in production use proper VirusTotal API client
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    'x-apikey': settings.VIRUSTOTAL_API_KEY
                }
                # This is a simplified example
                # Real implementation would use VT API v3
                logger.debug(f"VirusTotal check for {url} (API integration needed)")
                return None
        except Exception as e:
            logger.error(f"VirusTotal API error: {e}")
            return None


# Singleton instance
_link_service = None

def get_link_service() -> LinkAnalysisService:
    """Get singleton instance of link analysis service"""
    global _link_service
    if _link_service is None:
        _link_service = LinkAnalysisService()
    return _link_service
