"""
MediaWiki API client for Wikipedia scraping
"""

import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MediaWikiAPI:
    """Client for interacting with MediaWiki API"""
    
    def __init__(self, base_url: str = "https://en.wikipedia.org/w/api.php"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SciFiTechScraper/1.0 (https://github.com/arvinsingh/sci-fi-scraper)'
        })
        
    def get_category_members(self, category: str, limit: int = 500) -> List[Dict]:
        """Get all members of a category using MediaWiki API"""
        members = []
        continue_token = None
        
        while True:
            params = {
                'action': 'query',
                'list': 'categorymembers',
                'cmtitle': f'Category:{category}',
                'cmlimit': min(limit, 500),
                'format': 'json',
                'cmtype': 'page|subcat'
            }
            
            if continue_token:
                params.update(continue_token)
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'query' in data and 'categorymembers' in data['query']:
                    members.extend(data['query']['categorymembers'])
                
                if 'continue' not in data:
                    break
                    
                continue_token = data['continue']
                time.sleep(0.1)  # rate limiting
                
            except Exception as e:
                logger.error(f"Error getting category members for {category}: {e}")
                break
        
        return members
    
    def get_page_content(self, title: str) -> Optional[Dict]:
        """
        Get page content using MediaWiki API
        Returns a dictionary with title, extract, URL, and categories
        """
        params = {
            'action': 'query',
            'prop': 'extracts|categories|info',
            'exintro': False,
            'explaintext': True,
            'exsectionformat': 'plain',
            'titles': title,
            'format': 'json',
            'inprop': 'url'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'query' in data and 'pages' in data['query']:
                pages = data['query']['pages']
                page_id = next(iter(pages.keys()))
                
                if page_id != '-1':  # Page exists
                    page_data = pages[page_id]
                    return {
                        'title': page_data.get('title', ''),
                        'extract': page_data.get('extract', ''),
                        'url': page_data.get('fullurl', ''),
                        'categories': [cat['title'] for cat in page_data.get('categories', [])]
                    }
            
        except Exception as e:
            logger.error(f"Error getting page content for {title}: {e}")
        
        return None
