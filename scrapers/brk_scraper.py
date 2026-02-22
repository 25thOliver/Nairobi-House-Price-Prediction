"""BuyRentKenya Property Web Scraper"""

import re
import csv
import logging
import traceback
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class BRKScraper(BaseScraper):
    """Scraper for BuyRentKenya properties"""

    def __init__(self, delay: int = 2, max_retries: int = 3):
        super().__init__(delay=delay, max_retries=max_retries)
        self.base_url = "https://www.buyrentkenya.com/houses-for-rent"
        
    def _parse_price(self, text: str) -> Optional[float]:
        """Extract price from text like 'KSh 40,000 / month'"""
        if not text:
            return None
        try:
            # Look for digits and commas
            match = re.search(r'([\d,]+)', text)
            if match:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
            return None
        except Exception as e:
            logger.debug(f"Failed to parse price from '{text}': {str(e)}")
            return None

    def _parse_size(self, size_text: str) -> float:
        """Extract size from text like '158 m²' and convert to sqft"""
        if not size_text:
            return 0.0
        try:
            match = re.search(r'([\d,]+(?:.\d+)?)', size_text)
            if match:
                # Value is in sqm, convert to sqft (1 sqm = 10.7639 sqft)
                size_sqm = float(match.group(1).replace(',', ''))
                return round(size_sqm * 10.7639, 2)
            return 0.0
        except Exception:
            return 0.0

    def scrape_listings(self, max_pages: int = 10) -> List[Dict]:
        """Scrape properties up to max_pages"""
        all_listings = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"Scraping BuyRentKenya page {page}/{max_pages}")
            
            # BRK uses ?page=2
            url = f"{self.base_url}?page={page}" if page > 1 else self.base_url
            
            html = self.fetch_page(url)
            if not html:
                logger.warning(f"Failed to fetch page {page}, stopping.")
                break
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find listing cards
            listing_cards = soup.find_all('div', class_=lambda c: c and 'listing-card' in c.lower())
            
            if not listing_cards:
                logger.info(f"No listings found on page {page}, ending pagination.")
                break
                
            for card in listing_cards:
                # Fallback dictionary
                listing_data = {
                    'title': 'Unknown',
                    'location': 'Nairobi',
                    'price_kes': 0,
                    'bedrooms': 0,
                    'bathrooms': 0,
                    'size_sqft': 0.0,
                    'property_type': 'House',
                    'source': 'BuyRentKenya'
                }
                
                try:
                    # BRK makes it easy: details are heavily structured in links/spans
                    text_parts = [t.strip() for t in card.get_text(separator='|').split('|') if t.strip()]
                    full_text = ' '.join(text_parts)
                    
                    # Usually price has KSh
                    price_tags = [t for t in text_parts if 'KSh' in t]
                    if price_tags:
                        price = self._parse_price(price_tags[0])
                        if price:
                            listing_data['price_kes'] = price

                    # Bedrooms (e.g. "3 Bedrooms" or "3 Bed")
                    bed_match = re.search(r'(\d+)\s*(Bed|Bedroom)', full_text, re.IGNORECASE)
                    if bed_match:
                        listing_data['bedrooms'] = int(bed_match.group(1))

                    # Bathrooms (e.g. "2 Bathrooms" or "2 Bath")
                    bath_match = re.search(r'(\d+)\s*(Bath|Bathroom)', full_text, re.IGNORECASE)
                    if bath_match:
                        listing_data['bathrooms'] = int(bath_match.group(1))

                    # Size (e.g. "158 m²")
                    size_match = re.search(r'([\d,]+)\s*m²', full_text, re.IGNORECASE)
                    if size_match:
                        listing_data['size_sqft'] = self._parse_size(size_match.group(0))

                    # Try to find a location by checking for the common pattern: "Title | Location | Bedrooms"
                    # We can iterate through text parts backwards to find something before Bedrooms
                    try:
                        bedrooms_index = next(i for i, part in enumerate(text_parts) if 'Bedroom' in part and len(part) < 20)
                        if bedrooms_index > 0:
                            loc_candidate = text_parts[bedrooms_index - 1]
                            if loc_candidate and len(loc_candidate) < 50:
                                listing_data['location'] = loc_candidate
                    except StopIteration:
                        pass
                        
                    # Basic property type inference based on text
                    l_text = full_text.lower()
                    if 'townhouse' in l_text:
                        listing_data['property_type'] = 'Townhouse'
                    elif 'villa' in l_text:
                        listing_data['property_type'] = 'Villa'
                    elif 'bungalow' in l_text:
                        listing_data['property_type'] = 'Bungalow'
                    elif 'apartment' in l_text:
                        listing_data['property_type'] = 'Apartment'
                    elif 'house' in l_text:
                        listing_data['property_type'] = 'House'

                    if listing_data['price_kes'] > 0:
                        all_listings.append(listing_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing listing card: {e}")
                    traceback.print_exc()
                    continue
                    
        return all_listings

if __name__ == "__main__":
    import os
    from datetime import datetime
    
    # Ensure data directory exists
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.dirname(os.path.abspath(__file__)).replace('scrapers', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    csv_path = os.path.join(data_dir, 'raw_listings.csv')
    
    scraper = BRKScraper(delay=1)
    # Scrape ~30 pages to get a solid sample size (~700 listings)
    results = scraper.scrape_listings(max_pages=30)
    print(f"Scraped {len(results)} listings.")
    
    if results:
        # Save to CSV
        fieldnames = ['location', 'property_type', 'bedrooms', 'bathrooms', 'size_sqft', 'amenities', 'price_kes', 'listing_date', 'source']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            today = datetime.now().strftime('%Y-%m-%d')
            for r in results:
                # Fill missing fields required by the dictionary
                r['amenities'] = ''  # We aren't scraping amenities explicitly yet
                r['listing_date'] = today
                writer.writerow(r)
                
        print(f"Data saved to {csv_path}")
