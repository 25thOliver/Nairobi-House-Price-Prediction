# Basic property scraper for Nairobi listings

import pandas as pandas
import re
from typing import List, dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class PropertyScraper(BaseScraper):
    # Scraper for Nairobi property listings

    def __init__(self, base_url: str, delay: int = 2):
        super().__init__(delay=delay)
        self.base_url = base_url