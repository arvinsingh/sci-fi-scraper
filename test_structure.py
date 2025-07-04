#!/usr/bin/env python3
"""
Simple test to verify the modular structure works
"""

import sys
from pathlib import Path

# add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        from src.models import TechEntry
        from src.config import ScraperConfig
        from src.api_client import MediaWikiAPI
        from src.classifier import ContentClassifier
        from src.utils import CheckpointManager, DataExporter
        from src.scraper import WikipediaScraper
        from src.cli import run_scraper
        
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components"""
    try:
        from src.models import TechEntry
        from src.config import ScraperConfig
        from src.classifier import ContentClassifier
        from src.api_client import MediaWikiAPI
        
        # test TechEntry
        entry = TechEntry(
            name="Test Device",
            description="A test sci-fi device",
            url="https://example.com",
            category="Test Category",
            tech_type="device"
        )
        assert entry.name == "Test Device"
        assert entry.content_length == len(entry.description)
        print("✓ TechEntry works correctly")
        
        # test Config
        config = ScraperConfig()
        assert hasattr(config, 'TECH_CLASSIFIERS')
        assert 'weapon' in config.TECH_CLASSIFIERS
        print("✓ ScraperConfig works correctly")
        
        # test Classifier
        classifier = ContentClassifier()
        is_sci_fi, tech_type, confidence = classifier.is_sci_fi_technology(
            "Lightsaber", 
            "A lightsaber is a fictional energy sword featured in the Star Wars universe.",
            ["Category:Star Wars weapons"]
        )
        assert is_sci_fi == True
        assert tech_type == "weapon"
        print("✓ ContentClassifier works correctly")
        
        # test API Client (without making actual requests)
        api = MediaWikiAPI()
        assert api.base_url == "https://en.wikipedia.org/w/api.php"
        print("✓ MediaWikiAPI initialized correctly")
        
        print("✓ All basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing modular sci-fi scraper structure...")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_basic_functionality():
        success = False
    
    print("=" * 50)
    if success:
        print("✓ All tests passed! The modular structure is working correctly.")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
