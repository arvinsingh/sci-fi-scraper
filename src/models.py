"""
Data models for the sci-fi technology scraper
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List


@dataclass
class TechEntry:
    """
    Data structure for a technology entry
    """
    name: str
    description: str
    url: str
    category: str
    subcategory: str = ""
    content_length: int = 0
    scraped_at: str = ""
    tech_type: str = ""
    
    def __post_init__(self):
        self.content_length = len(self.description)
        self.scraped_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_training_example(self) -> Dict:
        """Convert to training data format"""
        return {
            "instruction": f"Describe this {self.tech_type} from science fiction:",
            "input": self.name,
            "output": self.description,
            "metadata": {
                "source": "wikipedia",
                "category": self.category,
                "tech_type": self.tech_type,
                "url": self.url
            }
        }
