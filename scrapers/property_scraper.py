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

    def scrape_listings(self, max_pages: int = 10) -> List[Dict]:
        # Scrape multiple pages of listings
        all_listings = []

        for page in range(1, max_pages + 1):
            logger.info(f"Scraping page {page}/{max_pages}")

            page_url = f"{self.base_url}?page={page}"
            html = self.fetch_page(page_url)

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            # TODO: I'll be updating this selector based on the actual website
            listing_elements = soup.find_all('div', class_='property-listing')

            for element in listing_elements:
                listing = self.parse_listing(element)
                if listing:
                    all_listings.append(listing)

            logger.info(f"Found {len(listing_elements)} listings on page {page}")

        return all_listings

            