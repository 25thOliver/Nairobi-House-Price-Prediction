# Base scraper with common functionality

import time
import logging
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from fake_useragent import fake_useragent

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