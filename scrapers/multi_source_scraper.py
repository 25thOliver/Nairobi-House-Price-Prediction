# Multi-source scraper aggregator for combining data from multiple websites

import pandas as pd
from typing import List, Dict
import logging
from .jiji_scraper import JijiScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiSourceScraper:
    # Aggregate listings from multiple property websites
    
    def __init__(self, delay: int = 2):
        self.delay = delay
        self.all_listings = []
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape from all available sources"""
        
        # Source 1: Jiji.co.ke (multiple categories)
        print("\n" + "="*70)
        print("SOURCE 1: JIJI.CO.KE")
        print("="*70)
        jiji_scraper = JijiScraper(delay=self.delay)
        jiji_listings = jiji_scraper.scrape_all_categories(max_pages_per_category=20)
        self.all_listings.extend(jiji_listings)
        print(f"Jiji.co.ke: {len(jiji_listings)} listings")
        
        # More sources here
        # Source 2: BuyRentKenya (if accessible)
        # Source 3: Property24 (if accessible)
        
        return self.all_listings
    
    def remove_duplicates(self, listings: List[Dict]) -> List[Dict]:
        # Remove duplicate listings based on price, location, and bedrooms
        seen = set()
        unique_listings = []
        
        for listing in listings:
            # Create a unique key
            key = (
                listing['price_kes'],
                listing['location'],
                listing['bedrooms'],
                listing['property_type']
            )
            
            if key not in seen:
                seen.add(key)
                unique_listings.append(listing)
        
        return unique_listings
    
    def save_combined_data(self, filepath: str = 'data/raw_listings.csv'):
        # Save all collected listings to CSV
        
        # Remove duplicates
        unique_listings = self.remove_duplicates(self.all_listings)
        
        # Convert to DataFrame
        df = pd.DataFrame(unique_listings)
        
        # Remove URL column if exists
        if 'url' in df.columns:
            df = df.drop('url', axis=1)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        print(f"\n{'='*70}")
        print(f"FINAL RESULTS")
        print(f"{'='*70}")
        print(f"Total listings collected: {len(self.all_listings)}")
        print(f"Unique listings after deduplication: {len(unique_listings)}")
        print(f"Saved to: {filepath}")
        
        return df


def main():
    # Main execution for multi-source scraping
    
    print("\nMULTI-SOURCE NAIROBI PROPERTY SCRAPER")
    print("="*70)
    print("Target: 500-800 listings")
    print("="*70)
    
    scraper = MultiSourceScraper(delay=2)
    
    # Scrape all sources
    all_listings = scraper.scrape_all_sources()
    
    # Save combined data
    df = scraper.save_combined_data()
    
    # Display summary
    print(f"\nDATASET SUMMARY")
    print(f"{'='*70}")
    print(df.info())
    print(f"\nPrice Statistics (KES):")
    print(df['price_kes'].describe())
    print(f"\nTop 10 Locations:")
    print(df['location'].value_counts().head(10))
    print(f"\nProperty Types:")
    print(df['property_type'].value_counts())
    
    print(f"\nDay 1 Complete! Dataset ready for Day 2 cleaning.")


if __name__ == "__main__":
    main()