"""
Configuration settings for the scraper
"""

from typing import Dict, List


class ScraperConfig:
    """Configuration settings for the scraper"""
    
    # default scraping parameters
    DEFAULT_MAX_ENTRIES = 15000
    DEFAULT_MAX_WORKERS = 4
    DEFAULT_MAX_DEPTH = 5
    DEFAULT_MAX_SUBCATS = 5
    DEFAULT_MAX_PAGES = 5000
    DEFAULT_CHECKPOINT_DIR = "checkpoints"
    
    # default categories to scrape
    DEFAULT_CATEGORIES = [
        'Fictional technology', 
        'Science fiction weapons', 
        'Fictional spacecraft', 
        'Fictional vehicles', 
        'Fictional robots'
    ]
    
    # technology classification patterns
    TECH_CLASSIFIERS = {
        'weapon': {
            'keywords': ['weapon', 'gun', 'rifle', 'blaster', 'phaser', 'cannon', 'sword', 'blade', 'bomb', 'missile', 'torpedo', 'laser', 'plasma', 'disruptor', 'armament', 'firearm'],
            'context': ['fires', 'shoots', 'armed', 'combat', 'warfare', 'damage', 'destructive', 'explosive', 'penetrate', 'kill'],
            'weight': 3
        },
        'vehicle': {
            'keywords': ['ship', 'vessel', 'craft', 'fighter', 'cruiser', 'transport', 'shuttle', 'carrier', 'destroyer', 'frigate', 'corvette', 'dreadnought', 'starship', 'spacecraft'],
            'context': ['travels', 'flies', 'navigates', 'crew', 'passengers', 'pilot', 'engine', 'hull', 'bridge', 'propulsion'],
            'weight': 3
        },
        'device': {
            'keywords': ['device', 'gadget', 'tool', 'scanner', 'communicator', 'computer', 'console', 'terminal', 'apparatus', 'instrument', 'detector', 'analyzer'],
            'context': ['operates', 'functions', 'displays', 'processes', 'controls', 'interface', 'screen', 'data', 'information'],
            'weight': 2
        },
        'robot': {
            'keywords': ['droid', 'robot', 'android', 'cyborg', 'automaton', 'mech', 'mecha', 'synthetic', 'artificial'],
            'context': ['autonomous', 'programmed', 'intelligence', 'sentient', 'mechanical', 'ai', 'artificial'],
            'weight': 3
        },
        'system': {
            'keywords': ['system', 'technology', 'drive', 'engine', 'reactor', 'generator', 'shield', 'defense', 'network', 'grid'],
            'context': ['powered', 'generates', 'operates', 'mechanism', 'process', 'function', 'capability'],
            'weight': 2
        },
        'equipment': {
            'keywords': ['armor', 'suit', 'equipment', 'gear', 'machinery', 'hardware', 'component', 'apparatus'],
            'context': ['worn', 'equipped', 'protective', 'enhanced', 'designed', 'constructed'],
            'weight': 2
        }
    }
    
    # sci-fi context indicators
    SCI_FI_INDICATORS = {
        'strong': ['fictional', 'science fiction', 'sci-fi', 'futuristic', 'space', 'alien', 'time travel', 'cyberpunk'],
        'franchises': ['star trek', 'star wars', 'battlestar galactica', 'stargate', 'doctor who', 'firefly', 'babylon 5', 'mass effect', 'halo', 'dune'],
        'tech_context': ['spaceship', 'energy weapon', 'force field', 'hyperdrive', 'warp drive', 'cloaking device', 'transporter']
    }
    
    # content exclusion patterns
    EXCLUSION_PATTERNS = {
        'list_pages': r'\b(list|index|category|timeline|chronology|history) of\b',
        'person_patterns': [
            r'\b(he|she|they) (is|was|were|are)\b',
            r'\b(born|died|birth|death)\b',
            r'\b(actor|actress|character|person|individual)\b',
            r'\b(portrayed|played|voiced) by\b',
            r'\b(biography|biographical)\b'
        ],
        'plot_patterns': [
            r'\bin the (short|story|plot|episode|film|movie|book|novel|comic|television)\b',
            r'\b(appears|featured|introduced) in\b',
            r'\b(storyline|narrative|plot)\b'
        ]
    }
    
    # category relevance patterns
    CATEGORY_PATTERNS = {
        'skip_patterns': [
            'disambiguation', 'redirect', 'stub', 'cleanup', 'maintenance',
            'wikipedia', 'template', 'user', 'talk', 'project', 'portal',
            'navigation', 'infobox'
        ],
        'biographical_patterns': [
            'biography', 'people', 'characters', 'cast', 'crew', 
            'actors', 'directors', 'writers', 'producers'
        ],
        'media_patterns': [
            'episodes', 'seasons', 'series', 'films', 'movies', 'books', 'novels', 'comics'
        ],
        'tech_patterns': [
            'technology', 'weapon', 'device', 'equipment', 'vehicle',
            'spacecraft', 'starship', 'robot', 'android', 'cyborg',
            'computer', 'system', 'machinery', 'apparatus', 'tool',
            'gadget', 'invention', 'engineering', 'science', 'fictional',
            'armor', 'military', 'space', 'future', 'alien', 'laser',
            'energy', 'power', 'transport', 'communication', 'medical'
        ]
    }
    
    # quality thresholds
    MIN_CONTENT_LENGTH = 200
    MIN_CONFIDENCE_SCORE = 0.25
    MIN_TRAINING_CONTENT_LENGTH = 100
