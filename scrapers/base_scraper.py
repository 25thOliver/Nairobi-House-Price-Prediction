# Base scraper with common functionality

import time
import logging
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    # Base class for property scrapers

    def __init__(self, delay: int = 2, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
        self.ua = UserAgent()
        self.session = requests.Session()

    def get_headers(self) -> Dict[str, str]:
        # Generate random headers
        return{
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }   

    def fetch_page(self, url: str) -> Optional[str]:
        # Fetch page content with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    timeout=30
                )
                response.raise_for_status()
                time.sleep(self.delay)
                return response.text
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
                time.sleep(self.delay * (attempt + 1))

        return None

    @abstractmethod
    def scrape_listings(self, max_pages: int = 10) -> List[Dict]:
        # Scrape property listings  implement in subclass
        pass