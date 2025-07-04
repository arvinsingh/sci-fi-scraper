"""
Main Wikipedia scraper class
"""

import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set
from pathlib import Path

from .api_client import MediaWikiAPI
from .classifier import ContentClassifier
from .models import TechEntry
from .utils import CheckpointManager, DataExporter
from .config import ScraperConfig

logger = logging.getLogger(__name__)


class WikipediaScraper:
    """Main Wikipedia scraper for sci-fi technology"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints", max_workers: int = 4, 
                 max_depth: int = 5, max_subcats: int = 5, max_pages: int = 5000):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.max_workers = max_workers
        
        # Initialize components
        self.api = MediaWikiAPI()
        self.classifier = ContentClassifier()
        self.checkpoint_manager = CheckpointManager(checkpoint_dir)
        self.data_exporter = DataExporter(checkpoint_dir)
        
        # Thread-safe data structures
        self.lock = threading.Lock()
        self.visited_pages: Set[str] = set()
        self.visited_categories: Set[str] = set()
        self.scraped_entries: List[TechEntry] = []
        self.failed_pages: List[str] = []
        
        # Configuration for recursive processing
        self.max_category_depth = max_depth
        self.max_subcategories_per_category = max_subcats
        self.max_pages_per_category = max_pages
        
        # Load existing checkpoint
        self.load_checkpoint()
        logger.info(f"Scraper initialized with MediaWiki API. Loaded {len(self.scraped_entries)} existing entries")
    
    def load_checkpoint(self):
        """Load previous scraping state"""
        checkpoint_data = self.checkpoint_manager.load_checkpoint()
        if checkpoint_data:
            self.visited_pages = set(checkpoint_data.get('visited_pages', []))
            self.visited_categories = set(checkpoint_data.get('visited_categories', []))
            self.failed_pages = checkpoint_data.get('failed_pages', [])
            
            # Reconstruct TechEntry objects
            entries_data = checkpoint_data.get('scraped_entries', [])
            self.scraped_entries = [TechEntry(**entry) for entry in entries_data]
    
    def save_checkpoint(self):
        """Save current scraping state"""
        self.checkpoint_manager.save_checkpoint(
            self.visited_pages, self.visited_categories, 
            self.scraped_entries, self.failed_pages
        )
    
    def process_page(self, page_title: str, category: str) -> List[TechEntry]:
        """Process a single page and extract technology entries"""
        # Check if already processed
        with self.lock:
            if page_title in self.visited_pages:
                return []
            self.visited_pages.add(page_title)
        
        logger.debug(f"Processing page: {page_title}")
        
        try:
            # Get page content via API
            page_data = self.api.get_page_content(page_title)
            if not page_data:
                logger.warning(f"No content found for {page_title}")
                return []
            
            title = page_data['title']
            content = page_data['extract']
            url = page_data['url']
            categories = page_data.get('categories', [])
            
            # Skip if content is too short
            if len(content) < ScraperConfig.MIN_CONTENT_LENGTH:
                logger.debug(f"Content too short for {title}: {len(content)} chars")
                return []
            
            # Check for exclusions
            if self.classifier.is_excluded_content(title, content):
                logger.debug(f"Excluded content: {title}")
                return []
            
            # Classify as sci-fi technology
            is_sci_fi_tech, tech_type, confidence = self.classifier.is_sci_fi_technology(
                title, content, categories
            )
            
            if not is_sci_fi_tech:
                logger.debug(f"Not sci-fi technology: {title}")
                return []
            
            if confidence < ScraperConfig.MIN_CONFIDENCE_SCORE:
                logger.debug(f"Low confidence ({confidence:.2f}): {title}")
                return []
            
            # Create entry
            entry = TechEntry(
                name=title,
                description=content,
                url=url,
                category=category,
                tech_type=tech_type
            )
            
            logger.info(f"Extracted entry from {title} (confidence: {confidence:.2f})")
            return [entry]
            
        except Exception as e:
            logger.error(f"Error processing {page_title}: {e}")
            with self.lock:
                self.failed_pages.append(page_title)
            return []
    
    def scrape_category(self, category_name: str, max_pages: int = 500, current_depth: int = 0) -> int:
        """Scrape all pages in a category with depth limits and cycle detection"""
        
        # Normalize category name
        normalized_category = category_name.replace('Category:', '')
        
        # Check depth limit
        if current_depth > self.max_category_depth:
            logger.info(f"Skipping category {category_name} - depth limit reached ({current_depth})")
            return 0
        
        # Check for cycles
        category_depth_key = f"{normalized_category}_{current_depth}"
        with self.lock:
            if category_depth_key in self.visited_categories:
                logger.debug(f"Skipping category {category_name} at depth {current_depth} - already visited")
                return 0
            self.visited_categories.add(category_depth_key)
            
            # Add the simple category name to prevent infinite recursion
            if current_depth > 0 and normalized_category in self.visited_categories:
                logger.debug(f"Skipping category {category_name} - visited at different depth")
                return 0
        
        logger.info(f"Scraping category: {category_name} (depth: {current_depth})")
        
        # Get all members of the category
        members = self.api.get_category_members(normalized_category, limit=min(max_pages, self.max_pages_per_category))
        
        if not members:
            logger.warning(f"No members found in category: {category_name}")
            return 0
        
        # Separate pages from subcategories
        pages = [m for m in members if m.get('ns', 0) == 0]  # main namespace
        subcategories = [m for m in members if m.get('ns', 0) == 14]  # category namespace
        
        subcategories = subcategories[:self.max_subcategories_per_category]
        
        logger.info(f"Found {len(pages)} pages and {len(subcategories)} subcategories in {category_name}")
        
        # Process pages in parallel
        entries_found = 0
        
        if pages:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_page = {
                    executor.submit(self.process_page, page['title'], category_name): page['title']
                    for page in pages
                }
                
                for future in as_completed(future_to_page):
                    page_title = future_to_page[future]
                    try:
                        entries = future.result()
                        if entries:
                            with self.lock:
                                self.scraped_entries.extend(entries)
                                entries_found += len(entries)
                            
                            # Save checkpoint periodically
                            if entries_found % 10 == 0:
                                self.save_checkpoint()
                                
                    except Exception as e:
                        logger.error(f"Error processing {page_title}: {e}")
        
        # Process subcategories only if haven't reached max depth
        if current_depth < self.max_category_depth:
            logger.info(f"Processing {len(subcategories)} subcategories for {category_name}")
            for i, subcat in enumerate(subcategories):
                # Additional filtering to avoid processing irrelevant subcategories
                subcat_name = subcat['title']
                if self.classifier.is_relevant_subcategory(subcat_name):
                    logger.info(f"Processing subcategory {i+1}/{len(subcategories)}: {subcat_name}")
                    try:
                        subcat_entries = self.scrape_category(
                            subcat_name, 
                            max_pages=min(300, self.max_pages_per_category // 2),
                            current_depth=current_depth + 1
                        )
                        entries_found += subcat_entries
                        
                        # Delay between subcategories
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error processing subcategory {subcat_name}: {e}")
                else:
                    logger.debug(f"Skipping irrelevant subcategory: {subcat_name}")
        else:
            logger.info(f"Max depth reached, not processing {len(subcategories)} subcategories")
        
        logger.info(f"Found {entries_found} entries in category {category_name} (depth: {current_depth})")
        return entries_found
    
    def scrape_all(self, start_categories: List[str] = None, max_entries: int = 5000):
        """Main scraping method with improved control flow"""
        if start_categories is None:
            start_categories = ScraperConfig.DEFAULT_CATEGORIES
        
        logger.info(f"Starting scraping with {len(start_categories)} categories")
        logger.info(f"Configuration: max_depth={self.max_category_depth}, max_subcats={self.max_subcategories_per_category}, max_pages_per_cat={self.max_pages_per_category}")
        
        try:
            for i, category in enumerate(start_categories):
                if len(self.scraped_entries) >= max_entries:
                    logger.info(f"Reached max entries limit ({max_entries}), stopping")
                    break
                
                logger.info(f"Processing category {i+1}/{len(start_categories)}: {category}")
                
                try:
                    entries_found = self.scrape_category(category, current_depth=0)
                    
                    logger.info(f"Completed category {category}: found {entries_found} entries")
                    logger.info(f"Total progress: {len(self.scraped_entries)}/{max_entries} entries")
                    
                    self.save_checkpoint()
                    
                    time.sleep(2)  # Be polite to Wikipedia
                    
                except Exception as e:
                    logger.error(f"Error processing category {category}: {e}")
        
        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user")
        except Exception as e:
            logger.error(f"Scraping error: {e}")
        finally:
            self.save_checkpoint()
            self.export_data()
            
            logger.info(f"Scraping completed: {len(self.scraped_entries)} total entries")
            logger.info(f"Categories visited: {len(self.visited_categories)}")
            logger.info(f"Pages processed: {len(self.visited_pages)}")
            logger.info(f"Failed pages: {len(self.failed_pages)}")
    
    def export_data(self):
        """Export scraped data to various formats"""
        self.data_exporter.export_data(
            self.scraped_entries, self.visited_categories, 
            self.visited_pages, self.failed_pages
        )
    
    def generate_statistics(self) -> dict:
        """Generate comprehensive scraping statistics"""
        return self.data_exporter.generate_statistics(
            self.scraped_entries, self.visited_categories, 
            self.visited_pages, self.failed_pages
        )
    
    def test_classification(self, test_pages: List[str]) -> None:
        """Test the classification on specific pages for debugging"""
        print("Testing classification on sample pages:")
        print("-" * 50)
        
        for page_title in test_pages:
            try:
                page_data = self.api.get_page_content(page_title)
                if page_data:
                    title = page_data['title']
                    content = page_data['extract']
                    categories = page_data.get('categories', [])
                    
                    # Test exclusion
                    excluded = self.classifier.is_excluded_content(title, content)
                    
                    # Test classification
                    is_sci_fi_tech, tech_type, confidence = self.classifier.is_sci_fi_technology(
                        title, content, categories
                    )
                    
                    print(f"Page: {title}")
                    print(f"  Content length: {len(content)}")
                    print(f"  Excluded: {excluded}")
                    print(f"  Sci-fi tech: {is_sci_fi_tech}")
                    print(f"  Tech type: {tech_type}")
                    print(f"  Confidence: {confidence:.3f}")
                    print(f"  Categories: {categories[:3]}...")  # show first 3 categories
                    print()
                else:
                    print(f"Could not fetch: {page_title}")
                    
            except Exception as e:
                print(f"Error testing {page_title}: {e}")
