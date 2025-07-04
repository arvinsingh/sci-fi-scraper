"""
Content classification utilities
"""

import re
import logging
from typing import List, Tuple
from .config import ScraperConfig

logger = logging.getLogger(__name__)


class ContentClassifier:
    """Classifier for determining sci-fi technology content"""
    
    def __init__(self):
        self.tech_classifiers = ScraperConfig.TECH_CLASSIFIERS
        self.sci_fi_indicators = ScraperConfig.SCI_FI_INDICATORS
        self.exclusion_patterns = ScraperConfig.EXCLUSION_PATTERNS
        self.category_patterns = ScraperConfig.CATEGORY_PATTERNS
    
    def is_sci_fi_technology(self, title: str, content: str, categories: List[str]) -> Tuple[bool, str, float]:
        """Enhanced sci-fi technology classification with confidence scoring"""
        text = f"{title} {content}".lower()
        
        # check categories for sci-fi indicators
        category_text = ' '.join(categories).lower()
        sci_fi_score = 0
        
        # strong indicators (high weight)
        for indicator in self.sci_fi_indicators['strong']:
            if indicator in text or indicator in category_text:
                sci_fi_score += 3
        
        # franchise indicators (very high weight)
        for franchise in self.sci_fi_indicators['franchises']:
            if franchise in text or franchise in category_text:
                sci_fi_score += 4
        
        # tech context indicators (medium weight)
        for tech in self.sci_fi_indicators['tech_context']:
            if tech in text:
                sci_fi_score += 2
        
        # technology classification
        best_type = 'technology'
        best_score = 0
        
        for tech_type, classifier in self.tech_classifiers.items():
            type_score = 0
            
            # keyword matching
            keyword_matches = sum(1 for keyword in classifier['keywords'] if keyword in text)
            type_score += keyword_matches * classifier['weight']
            
            # context matching
            context_matches = sum(1 for context in classifier['context'] if context in text)
            type_score += context_matches * 2
            
            # bonus for having both keywords and context
            if keyword_matches > 0 and context_matches > 0:
                type_score += 3
            
            if type_score > best_score:
                best_score = type_score
                best_type = tech_type
        
        # Final scoring
        is_sci_fi = sci_fi_score >= 2
        is_tech = best_score >= 2
        
        confidence = min(1.0, (sci_fi_score + best_score) / 8.0)
        
        logger.debug(f"Classification for '{title}': sci-fi={is_sci_fi} ({sci_fi_score}), tech={is_tech} ({best_score}), type={best_type}, confidence={confidence:.2f}")
        
        return is_sci_fi and is_tech, best_type, confidence
    
    def is_excluded_content(self, title: str, content: str) -> bool:
        """Check if content should be excluded"""
        text = f"{title} {content}".lower()
        
        # list/index pages
        if re.search(self.exclusion_patterns['list_pages'], text):
            return True
        
        # person/character pages
        for pattern in self.exclusion_patterns['person_patterns']:
            if re.search(pattern, text):
                return True
        
        # plot/story focused content
        plot_matches = sum(1 for pattern in self.exclusion_patterns['plot_patterns'] 
                          if re.search(pattern, text))
        if plot_matches > 2:
            return True
        
        return False
    
    def is_relevant_subcategory(self, category_name: str) -> bool:
        """Check if a subcategory is relevant to sci-fi technology"""
        category_lower = category_name.lower()
        
        # skip administrative and meta categories
        if any(pattern in category_lower for pattern in self.category_patterns['skip_patterns']):
            return False
        
        # skip purely biographical/character categories
        if any(pattern in category_lower for pattern in self.category_patterns['biographical_patterns']):
            tech_terms = ['technology', 'weapon', 'device', 'equipment', 'vehicle', 'robot']
            if not any(term in category_lower for term in tech_terms):
                return False
        
        # skip pure media categories unless they might contain tech
        if any(pattern in category_lower for pattern in self.category_patterns['media_patterns']):
            tech_terms = ['technology', 'weapon', 'device', 'equipment', 'vehicle', 'robot', 'fictional']
            if not any(term in category_lower for term in tech_terms):
                return False
        
        # include technology-related categories
        has_tech_term = any(pattern in category_lower for pattern in self.category_patterns['tech_patterns'])
        is_fictional = 'fictional' in category_lower or 'science fiction' in category_lower
        
        return has_tech_term or is_fictional
