"""
Command line interface for the scraper
"""

import argparse
import logging
from typing import List

from .config import ScraperConfig
from .scraper import WikipediaScraper


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Sci-fi Technology Wikipedia Scraper')
    
    parser.add_argument('--max-entries', type=int, default=ScraperConfig.DEFAULT_MAX_ENTRIES,
                        help=f'Maximum number of entries to scrape (default: {ScraperConfig.DEFAULT_MAX_ENTRIES})')
    parser.add_argument('--max-workers', type=int, default=ScraperConfig.DEFAULT_MAX_WORKERS,
                        help=f'Number of worker threads (default: {ScraperConfig.DEFAULT_MAX_WORKERS})')
    parser.add_argument('--max-depth', type=int, default=ScraperConfig.DEFAULT_MAX_DEPTH,
                        help=f'Maximum category depth (default: {ScraperConfig.DEFAULT_MAX_DEPTH})')
    parser.add_argument('--max-subcats', type=int, default=ScraperConfig.DEFAULT_MAX_SUBCATS,
                        help=f'Maximum subcategories per category (default: {ScraperConfig.DEFAULT_MAX_SUBCATS})')
    parser.add_argument('--max-pages', type=int, default=ScraperConfig.DEFAULT_MAX_PAGES,
                        help=f'Maximum pages per category (default: {ScraperConfig.DEFAULT_MAX_PAGES})')
    parser.add_argument('--checkpoint-dir', type=str, default=ScraperConfig.DEFAULT_CHECKPOINT_DIR,
                        help=f'Directory for checkpoints (default: {ScraperConfig.DEFAULT_CHECKPOINT_DIR})')
    parser.add_argument('--categories', nargs='+', default=ScraperConfig.DEFAULT_CATEGORIES,
                        help=f'Categories to scrape (default: {ScraperConfig.DEFAULT_CATEGORIES})')
    parser.add_argument('--test-pages', nargs='+', 
                        help='Test classification on specific pages')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        default='INFO', help='Logging level (default: INFO)')
    
    return parser.parse_args()


def run_scraper():
    """Main execution function"""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    scraper = WikipediaScraper(
        checkpoint_dir=args.checkpoint_dir,
        max_workers=args.max_workers,
        max_depth=args.max_depth,
        max_subcats=args.max_subcats,
        max_pages=args.max_pages
    )
    
    # Test classification if requested
    if args.test_pages:
        scraper.test_classification(args.test_pages)
        return
    
    print(f"Starting scraper with configuration:")
    print(f"- Max entries: {args.max_entries}")
    print(f"- Max category depth: {args.max_depth}")
    print(f"- Max subcategories per category: {args.max_subcats}")
    print(f"- Max pages per category: {args.max_pages}")
    print(f"- Worker threads: {args.max_workers}")
    print(f"- Categories: {args.categories}")
    print()
    
    scraper.scrape_all(
        start_categories=args.categories,
        max_entries=args.max_entries
    )
    
    print(f"Scraping completed! Found {len(scraper.scraped_entries)} entries")
    print(f"Check the '{args.checkpoint_dir}' directory for exported data")
    
    stats = scraper.generate_statistics()
    print(f"\nDetailed Statistics:")
    print(f"Total entries: {stats.get('total_entries', 0)}")
    print(f"Tech types: {stats.get('tech_types', {})}")
    
    processing_stats = stats.get('processing_stats', {})
    print(f"\nProcessing Statistics:")
    print(f"Categories visited: {processing_stats.get('visited_categories', 0)}")
    print(f"Pages processed: {processing_stats.get('processed_pages', 0)}")
    print(f"Failed pages: {processing_stats.get('failed_pages', 0)}")
    print(f"Success rate: {processing_stats.get('success_rate', 0):.1f}%")
