"""
Content Safety Service for Responsible AI
Implements Azure Content Safety and custom filtering
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio
from enum import Enum

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import (
    TextCategory,
    AnalyzeTextOptions,
    AnalyzeTextResult
)
from azure.core.credentials import AzureKeyCredential
import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Content safety levels"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


@dataclass
class SafetyAnalysis:
    """Result of content safety analysis"""
    is_safe: bool
    safety_level: SafetyLevel
    reason: Optional[str] = None
    categories: Dict[str, float] = None
    confidence: float = 0.0
    filtered_content: Optional[str] = None


class ContentSafetyService:
    """
    Enterprise-grade content safety service
    Combines Azure Content Safety with custom governance rules
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self._blocked_terms = self._load_blocked_terms()
        self._department_policies = self._load_department_policies()
        
    async def __aenter__(self):
        """Initialize content safety client"""
        try:
            if self.settings.azure_content_safety_endpoint and self.settings.azure_content_safety_key:
                self._client = ContentSafetyClient(
                    endpoint=self.settings.azure_content_safety_endpoint,
                    credential=AzureKeyCredential(self.settings.azure_content_safety_key)
                )
                logger.info("Azure Content Safety client initialized")
            else:
                logger.warning("Azure Content Safety not configured, using local filtering only")
        except Exception as e:
            logger.error(f"Failed to initialize Content Safety client: {str(e)}")
            self._client = None
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self._client:
            # Azure SDK clients don't typically need explicit cleanup
            pass
    
    def _load_blocked_terms(self) -> List[str]:
        """Load blocked terms from configuration"""
        # In production, load from secure configuration or Azure Key Vault
        return [
            # PII patterns
            "social security number",
            "credit card",
            "bank account",
            "password",
            "confidential",
            "trade secret",
            # Inappropriate content
            "explicit content",
            "violent content",
            "hate speech",
            # Add more terms as needed
        ]
    
    def _load_department_policies(self) -> Dict[str, Dict]:
        """Load department-specific content policies"""
        return {
            "hr": {
                "allow_pii": False,
                "strict_filtering": True,
                "blocked_categories": ["harassment", "discrimination"]
            },
            "legal": {
                "allow_pii": True,  # Legal may need PII for cases
                "strict_filtering": True,
                "blocked_categories": ["violence", "self_harm"]
            },
            "engineering": {
                "allow_pii": False,
                "strict_filtering": False,
                "blocked_categories": []
            },
            "default": {
                "allow_pii": False,
                "strict_filtering": True,
                "blocked_categories": ["harassment", "violence", "self_harm"]
            }
        }
    
    async def analyze_text(self, text: str, department: Optional[str] = None) -> SafetyAnalysis:
        """
        Analyze text for content safety
        Combines Azure Content Safety with custom filtering
        """
        try:
            # Get department policy
            policy = self._department_policies.get(department, self._department_policies["default"])
            
            # Step 1: Check for blocked terms
            blocked_term_result = self._check_blocked_terms(text)
            if not blocked_term_result.is_safe:
                return blocked_term_result
            
            # Step 2: Azure Content Safety analysis (if available)
            azure_result = await self._analyze_with_azure(text) if self._client else None
            
            # Step 3: Custom PII detection
            pii_result = self._detect_pii(text, policy["allow_pii"])
            if not pii_result.is_safe:
                return pii_result
            
            # Step 4: Combine results
            return self._combine_safety_results(
                blocked_term_result,
                azure_result,
                pii_result,
                policy
            )
            
        except Exception as e:
            logger.error(f"Content safety analysis failed: {str(e)}")
            # Fail safe - block content if analysis fails
            return SafetyAnalysis(
                is_safe=False,
                safety_level=SafetyLevel.BLOCKED,
                reason=f"Analysis failed: {str(e)}"
            )
    
    def _check_blocked_terms(self, text: str) -> SafetyAnalysis:
        """Check for blocked terms in text"""
        text_lower = text.lower()
        
        for term in self._blocked_terms:
            if term in text_lower:
                return SafetyAnalysis(
                    is_safe=False,
                    safety_level=SafetyLevel.BLOCKED,
                    reason=f"Blocked term detected: {term}",
                    confidence=1.0
                )
        
        return SafetyAnalysis(
            is_safe=True,
            safety_level=SafetyLevel.SAFE,
            confidence=0.9
        )
    
    async def _analyze_with_azure(self, text: str) -> Optional[SafetyAnalysis]:
        """Analyze text using Azure Content Safety"""
        try:
            request = AnalyzeTextOptions(text=text)
            response = self._client.analyze_text(request)
            
            # Convert Azure response to safety analysis
            max_severity = 0
            categories = {}
            
            for result in response.categories_analysis:
                category_name = result.category.name.lower()
                severity = result.severity
                categories[category_name] = severity
                max_severity = max(max_severity, severity)
            
            # Determine safety level based on severity
            if max_severity >= 6:
                safety_level = SafetyLevel.BLOCKED
                is_safe = False
            elif max_severity >= 4:
                safety_level = SafetyLevel.HIGH_RISK
                is_safe = False
            elif max_severity >= 2:
                safety_level = SafetyLevel.MEDIUM_RISK
                is_safe = True  # Allow but flag
            else:
                safety_level = SafetyLevel.SAFE
                is_safe = True
            
            return SafetyAnalysis(
                is_safe=is_safe,
                safety_level=safety_level,
                categories=categories,
                confidence=0.8,
                reason=f"Azure Content Safety: {safety_level.value}"
            )
            
        except Exception as e:
            logger.error(f"Azure Content Safety analysis failed: {str(e)}")
            return None
    
    def _detect_pii(self, text: str, allow_pii: bool) -> SafetyAnalysis:
        """Detect and filter PII (Personally Identifiable Information)"""
        if allow_pii:
            return SafetyAnalysis(
                is_safe=True,
                safety_level=SafetyLevel.SAFE,
                confidence=0.9
            )
        
        # Simple PII patterns (in production, use Azure Text Analytics or regex library)
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
        }
        
        import re
        detected_pii = []
        
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_pii.append(pii_type)
        
        if detected_pii:
            return SafetyAnalysis(
                is_safe=False,
                safety_level=SafetyLevel.BLOCKED,
                reason=f"PII detected: {', '.join(detected_pii)}",
                confidence=0.9
            )
        
        return SafetyAnalysis(
            is_safe=True,
            safety_level=SafetyLevel.SAFE,
            confidence=0.9
        )
    
    def _combine_safety_results(
        self,
        blocked_result: SafetyAnalysis,
        azure_result: Optional[SafetyAnalysis],
        pii_result: SafetyAnalysis,
        policy: Dict
    ) -> SafetyAnalysis:
        """Combine multiple safety analysis results"""
        
        # If any result is blocked, block the content
        if not blocked_result.is_safe or not pii_result.is_safe:
            return SafetyAnalysis(
                is_safe=False,
                safety_level=SafetyLevel.BLOCKED,
                reason=blocked_result.reason or pii_result.reason,
                confidence=1.0
            )
        
        # If Azure analysis is available and indicates high risk
        if azure_result and not azure_result.is_safe:
            if policy["strict_filtering"]:
                return azure_result
            else:
                # Non-strict mode: allow but flag
                return SafetyAnalysis(
                    is_safe=True,
                    safety_level=SafetyLevel.MEDIUM_RISK,
                    reason=f"Flagged by Azure: {azure_result.reason}",
                    confidence=azure_result.confidence
                )
        
        # All checks passed
        return SafetyAnalysis(
            is_safe=True,
            safety_level=SafetyLevel.SAFE,
            confidence=0.9,
            reason="Content passed all safety checks"
        )
    
    async def filter_content(self, content: str, department: Optional[str] = None) -> str:
        """Filter unsafe content from text"""
        analysis = await self.analyze_text(content, department)
        
        if analysis.is_safe:
            return content
        
        # Apply content filtering
        filtered_content = content
        
        # Replace blocked terms with asterisks
        for term in self._blocked_terms:
            if term.lower() in filtered_content.lower():
                # Find and replace the term (case-insensitive)
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                filtered_content = pattern.sub('*' * len(term), filtered_content)
        
        return filtered_content
    
    async def get_safety_report(self, text: str, department: Optional[str] = None) -> Dict:
        """Get detailed safety analysis report"""
        analysis = await self.analyze_text(text, department)
        
        return {
            "is_safe": analysis.is_safe,
            "safety_level": analysis.safety_level.value,
            "reason": analysis.reason,
            "confidence": analysis.confidence,
            "categories": analysis.categories or {},
            "department_policy": self._department_policies.get(department, self._department_policies["default"]),
            "timestamp": asyncio.get_event_loop().time()
        }
