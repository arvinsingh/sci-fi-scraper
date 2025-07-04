"""
Checkpoint and data export utilities
"""

import json
import pickle
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import asdict

from .models import TechEntry

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages saving and loading of scraping checkpoints"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def save_checkpoint(self, visited_pages: Set[str], visited_categories: Set[str], 
                       scraped_entries: List[TechEntry], failed_pages: List[str]):
        """Save current scraping state"""
        checkpoint_data = {
            'visited_pages': list(visited_pages),
            'visited_categories': list(visited_categories),
            'scraped_entries': [asdict(entry) for entry in scraped_entries],
            'failed_pages': failed_pages,
            'timestamp': datetime.now().isoformat()
        }
        
        checkpoint_file = self.checkpoint_dir / "scraping_checkpoint.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        # pickle for faster loading
        pickle_file = self.checkpoint_dir / "scraping_checkpoint.pkl"
        with open(pickle_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        logger.info(f"Checkpoint saved: {len(scraped_entries)} entries, {len(visited_categories)} categories visited")
    
    def load_checkpoint(self) -> Dict:
        """Load previous scraping state"""
        pickle_file = self.checkpoint_dir / "scraping_checkpoint.pkl"
        json_file = self.checkpoint_dir / "scraping_checkpoint.json"
        
        try:
            if pickle_file.exists():
                with open(pickle_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)
            elif json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
            else:
                return {}
            
            logger.info(f"Checkpoint loaded: {len(checkpoint_data.get('scraped_entries', []))} entries")
            return checkpoint_data
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return {}


class DataExporter:
    """Handles exporting scraped data to various formats"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def export_data(self, scraped_entries: List[TechEntry], 
                   visited_categories: Set[str], visited_pages: Set[str], 
                   failed_pages: List[str]):
        """Export scraped data to various formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # export to JSON
        json_file = self.checkpoint_dir / f"fictional_tech_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(entry) for entry in scraped_entries], 
                     f, indent=2, ensure_ascii=False)
        
        # export to JSONL
        jsonl_file = self.checkpoint_dir / f"fictional_tech_data_{timestamp}.jsonl"
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for entry in scraped_entries:
                f.write(json.dumps(asdict(entry), ensure_ascii=False) + '\n')
        
        # export training format
        training_file = self.checkpoint_dir / f"training_data_{timestamp}.jsonl"
        with open(training_file, 'w', encoding='utf-8') as f:
            for entry in scraped_entries:
                if len(entry.description) >= 100:
                    training_example = entry.to_training_example()
                    f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
        
        # export statistics
        stats = self.generate_statistics(scraped_entries, visited_categories, 
                                       visited_pages, failed_pages)
        stats_file = self.checkpoint_dir / f"scraping_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data exported to {self.checkpoint_dir}")
        logger.info(f"Total entries: {len(scraped_entries)}")
    
    def generate_statistics(self, scraped_entries: List[TechEntry], 
                          visited_categories: Set[str], visited_pages: Set[str], 
                          failed_pages: List[str]) -> Dict:
        """Generate comprehensive scraping statistics"""
        if not scraped_entries:
            return {}
        
        categories = {}
        tech_types = {}
        description_lengths = []
        
        for entry in scraped_entries:
            categories[entry.category] = categories.get(entry.category, 0) + 1
            tech_types[entry.tech_type] = tech_types.get(entry.tech_type, 0) + 1
            description_lengths.append(len(entry.description))
        
        return {
            "total_entries": len(scraped_entries),
            "categories": categories,
            "tech_types": tech_types,
            "description_stats": {
                "min_length": min(description_lengths) if description_lengths else 0,
                "max_length": max(description_lengths) if description_lengths else 0,
                "avg_length": sum(description_lengths) / len(description_lengths) if description_lengths else 0
            },
            "quality_entries": len([e for e in scraped_entries if len(e.description) >= 100]),
            "processing_stats": {
                "failed_pages": len(failed_pages),
                "processed_pages": len(visited_pages),
                "visited_categories": len(visited_categories),
                "success_rate": (len(visited_pages) - len(failed_pages)) / max(len(visited_pages), 1) * 100
            }
        }
