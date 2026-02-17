# Jiji.co.ke scraper for multiple property categories

import pandas as pd
import re
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class JijiScraper(BaseScraper):
    # Enhanced scraper for Jiji.co.ke with multiple categories

    def __init__(self, delay: int = 2):
        super().__init__(delay=delay)
        self.categories = [
            'https://jiji.co.ke/nairobi/houses-apartments-for-sale',
            'https://jiji.co.ke/nairobi/land-and-plots-for-sale',
        ]

    def scrape_all_categories(self, max_pages_per_category: int = 15) -> List[Dict]:
        """Scrape multiple categories from Jiji"""
        all_listings = []
        
        for category_url in self.categories:
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping category: {category_url}")
            logger.info(f"{'='*60}")
            
            self.base_url = category_url
            category_listings = self.scrape_listings(max_pages_per_category)
            all_listings.extend(category_listings)
            
            logger.info(f"Collected {len(category_listings)} listings from this category")
        
        # Remove duplicates based on URL
        unique_listings = {listing['url']: listing for listing in all_listings}
        return list(unique_listings.values())

    def scrape_listings(self, max_pages: int = 15) -> List[Dict]:
        # Scrape multiple pages from a single category
        all_listings = []

        for page in range(1, max_pages + 1):
            logger.info(f"Scraping page {page}/{max_pages}")

            if page == 1:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}?page={page}"

            html = self.fetch_page(page_url)

            if not html:
                logger.warning(f"Failed to fetch page {page}, stopping pagination")
                break

            soup = BeautifulSoup(html, 'lxml')
            listing_elements = soup.find_all('a', href=re.compile(r'/(houses-apartments-for-sale|land-and-plots-for-sale)/'))

            if len(listing_elements) == 0:
                logger.warning(f"No listings found on page {page}, stopping")
                break

            logger.info(f"Found {len(listing_elements)} potential listings on page {page}")

            for element in listing_elements:
                listing = self.parse_listing(element)
                if listing and listing['price_kes'] > 0:
                    all_listings.append(listing)

        # Remove duplicates within this category
        unique_listings = {listing['url']: listing for listing in all_listings}
        return list(unique_listings.values())

    def parse_listing(self, element) -> Optional[Dict]:
        # Parse individual Jiji listing
        try:
            text = element.get_text(strip=True)
            url = element.get('href', '')
            if not url.startswith('http'):
                url = 'https://jiji.co.ke' + url

            # Extract price
            price_match = re.search(r'KSh\s*([\d,]+)', text)
            if not price_match:
                return None
            price_kes = float(price_match.group(1).replace(',', ''))

            # Extract bedrooms
            bedrooms_match = re.search(r'(\d+)bdrm', text)
            bedrooms = int(bedrooms_match.group(1)) if bedrooms_match else 0

            # Extract property type
            property_types = ['Apartment', 'House', 'Villa', 'Maisonette', 'Townhouse', 
                            'Bungalow', 'Mansion', 'Land', 'Plot']
            property_type = ''
            for ptype in property_types:
                if ptype in text:
                    property_type = ptype
                    break
            
            if not property_type:
                property_type = 'Other'

            # Extract size
            size_match = re.search(r'(\d+)\s*sqm', text)
            size_sqft = 0.0
            if size_match:
                size_sqm = float(size_match.group(1))
                size_sqft = size_sqm * 10.764

            # Extract location
            nairobi_locations = [
                'Kilimani', 'Westlands', 'Lavington', 'Riverside Drive', 'Nairobi Central',
                'Kahawa', 'Upperhill', 'Kasarani', 'Utawala', 'Kileleshwa', 'Karen',
                'Runda', 'Parklands', 'South B', 'South C', 'Langata', 'Embakasi',
                'Donholm', 'Ruaka', 'Ngong', 'Kitisuru', 'Muthaiga', 'Spring Valley',
                'Ridgeways', 'Gigiri', 'Syokimau', 'Mlolongo', 'Athi River'
            ]
            
            location = ''
            for loc in nairobi_locations:
                if loc in text:
                    location = loc
                    break
            
            if not location:
                location = 'Nairobi'

            # Estimate bathrooms
            bathrooms = max(1, bedrooms - 1) if bedrooms > 0 else 1

            # Extract amenities
            amenities = []
            amenity_keywords = ['pool', 'gym', 'parking', 'security', 'garden', 
                              'lift', 'laundry', 'balcony', 'terrace']
            text_lower = text.lower()
            for amenity in amenity_keywords:
                if amenity in text_lower:
                    amenities.append(amenity.capitalize())

            listing = {
                'location': location,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'size_sqft': round(size_sqft, 2),
                'amenities': ', '.join(amenities) if amenities else '',
                'price_kes': price_kes,
                'listing_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'jiji.co.ke',
                'url': url
            }

            return listing

        except Exception as e:
            logger.error(f"Error parsing listing: {str(e)}")
            return None

    def save_to_csv(self, listings: List[Dict], filepath: str = 'data/raw_listings.csv'):
        """Save listings to CSV"""
        df = pd.DataFrame(listings)
        if 'url' in df.columns:
            df = df.drop('url', axis=1)
        
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(listings)} listings to {filepath}")
        return df


def main():
    # Main scraping workflow for Jiji.co.ke
    
    scraper = JijiScraper(delay=2)

    print("Starting enhanced Jiji.co.ke scraper (multiple categories)...")
    listings = scraper.scrape_all_categories(max_pages_per_category=15)

    if listings:
        df = scraper.save_to_csv(listings)
        print(f"\nCollected {len(listings)} unique listings from Jiji.co.ke")
        print(f"\nDataset Preview:")
        print(df.head(10))
        print(f"\nDataset Info:")
        print(df.info())
        print(f"\nPrice Statistics (KES):")
        print(df['price_kes'].describe())
    else:
        print("No listings collected!")


if __name__ == "__main__":
    main()