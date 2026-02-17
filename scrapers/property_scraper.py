# Basic property scraper for Nairobi listings

import pandas as pd
import re
from typing import List, Dict, Optional
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


    def parse_listing(self, element) -> Optional[Dict]:
        # Parse indivdual listing: customized based on website structure
        try:
            # TODO: Customize these selectors
            listing = {
                'location': '',
                'property_type': '',
                'bedrooms': 0,
                'bathrooms': 0,
                'size_sqft': 0.0,
                'amenities': '',
                'price_kes': 0.0,
                'listing_date': datetime.now().strftime('%Y-%m-%d'),
                'source': self.base_url
            }

            return listing if listing['price_kes'] > 0 else None

        except Exception as e:
            logger.error(f"Error parsing listing: {str(e)}")
            return None

    
    def save_to_csv(slef, listings: List[Dict], filepath: str = 'data/raw_listings.csv'):
        # Save listing to CSV
        df = pd.DataFrame(listings)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(listings)} listings to {filepath}")
        return df

    def main():
        # Main scraping workflow

        scraper = PropertyScraper('https://www.property24.co.ke', delay=2)

        # Collect listings
        listings  = scraper.scrape_listings(max_pages=5)

        # Save to CSV
        if listings:
            df = scraper.save_to_csv(listings)
            print(f"\nCollected {len(listings)} listings")
            print(f"\nPreview:\n{df.head()}")
        else:
            print("No listings collected. Update the scraper selectors")
    

    if __name__ == "__main__":
        main()
