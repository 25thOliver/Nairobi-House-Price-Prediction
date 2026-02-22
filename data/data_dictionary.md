# Data Dictionary - Nairobi House Price Prediction

## Dataset: `raw_listings.csv`

### Overview
This dataset contains **628 unique property listings** scraped from BuyRentKenya.com for houses, apartments, and land for sale in Nairobi, Kenya.

**Collection Date:** February 17, 2026  
**Source:** https://www.buyrentkenya.com/houses-for-rent
**Categories:** Houses & Apartments for Sale + Land & Plots for Sale  
**Collection Method:** Multi-source web scraping using BeautifulSoup4 and Requests  
**Total Scraped:** 705 listings  
**After Deduplication:** 628 unique listings

---

## Column Definitions

| Column Name | Data Type | Description | Example Values | Notes |
|-------------|-----------|-------------|----------------|-------|
| `location` | String | Neighborhood/area in Nairobi | "Westlands", "Karen", "Kilimani", "Nairobi" | 177 entries are generic "Nairobi" |
| `property_type` | String | Type of property | "Apartment", "House", "Plot", "Land", "Maisonette", "Villa", "Mansion", "Bungalow", "Townhouse", "Other" | 161 entries classified as "Other" |
| `bedrooms` | Integer | Number of bedrooms | 0, 1, 2, 3, 4, 5+ | 0 for land/plots |
| `bathrooms` | Integer | Number of bathrooms | 1, 2, 3, 4+ | Estimated as max(1, bedrooms - 1) |
| `size_sqft` | Float | Property size in square feet | 0.0, 968.76, 5995.55 | Converted from sqm (1 sqm = 10.764 sqft); 0.0 means missing |
| `amenities` | String | Comma-separated amenities | "Parking, Security", "Pool, Gym, Parking" | Extracted via keyword matching |
| `price_kes` | Float | Listing price in Kenyan Shillings | 370000.0, 130000000.0, 15500000000.0 | **Target variable** |
| `listing_date` | String | Date property was scraped | "2026-02-17" | Format: YYYY-MM-DD |
| `source` | String | Website source | "buyrentkenya.com" | For tracking data provenance |

---

## Data Statistics

### Price Distribution (KES)
- **Count:** 628 listings
- **Mean:** 506,534,800 KES (~506.5M)
- **Median:** 130,000,000 KES (130M)
- **Min:** 370,000 KES (370K)
- **Max:** 15,500,000,000 KES (15.5B)
- **Std Dev:** 1,528,454,000 KES
- **25th Percentile:** 45M KES
- **75th Percentile:** 372.5M KES

### Location Distribution (Top 10)
1. Nairobi (Generic) - 177 listings (28.2%)
2. Nairobi Central - 61 listings (9.7%)
3. Westlands - 60 listings (9.6%)
4. Kasarani - 40 listings (6.4%)
5. Kilimani - 39 listings (6.2%)
6. Kileleshwa - 33 listings (5.3%)
7. Kahawa - 32 listings (5.1%)
8. Utawala - 31 listings (4.9%)
9. Lavington - 30 listings (4.8%)
10. Karen - 22 listings (3.5%)

### Property Type Distribution
- Apartment: 180 (28.7%)
- Other: 161 (25.6%) ⚠️ Needs classification
- Plot: 108 (17.2%)
- Maisonette: 55 (8.8%)
- House: 35 (5.6%)
- Land: 26 (4.1%)
- Mansion: 21 (3.3%)
- Villa: 17 (2.7%)
- Bungalow: 13 (2.1%)
- Townhouse: 12 (1.9%)

---

## Data Quality Assessment

### Completeness
| Column | Non-Null | Missing | Completeness |
|--------|----------|---------|--------------|
| location | 628 | 0 | 100% ✅ |
| property_type | 628 | 0 | 100% ✅ |
| bedrooms | 628 | 0 | 100% ✅ |
| bathrooms | 628 | 0 | 100% ✅ |
| size_sqft | 628 | ~200 (0.0 values) | ~68% ⚠️ |
| amenities | 628 | ~300 (empty strings) | ~52% ⚠️ |
| price_kes | 628 | 0 | 100% ✅ |
| listing_date | 628 | 0 | 100% ✅ |
| source | 628 | 0 | 100% ✅ |

### Known Issues (Day 2 Cleaning Tasks)
1. **Generic Locations:** 177 listings have "Nairobi" as location (needs refinement)
2. **Unclassified Types:** 161 listings marked as "Other" property type
3. **Missing Sizes:** Many properties have 0.0 sqft (size not provided)
4. **Estimated Bathrooms:** All bathroom counts are estimates, not actual
5. **Limited Amenities:** Only keyword-based extraction (incomplete)
6. **Price Outliers:** Max price of 15.5B KES seems unrealistic
7. **Duplicates Removed:** 77 duplicates were removed during collection

---

## Feature Engineering Plans (Day 2)

### Derived Features
1. **`price_per_sqft`** = `price_kes` / `size_sqft` (where size > 0)
2. **`amenity_score`** = Count of amenities (0-9 scale)
3. **`has_pool`**, **`has_gym`**, **`has_parking`**, **`has_security`** = Boolean flags
4. **`is_land`** = Boolean (True if property_type in ['Land', 'Plot'])
5. **`location_category`** = Group locations into zones (CBD, Suburbs, etc.)

### Cleaning Tasks
- [ ] Refine generic "Nairobi" locations
- [ ] Classify "Other" property types
- [ ] Handle missing size values (imputation or removal)
- [ ] Validate and cap price outliers
- [ ] Standardize location names
- [ ] Enhance amenity extraction
- [ ] Create location-based features (distance to CBD, etc.)

---

## Usage Example

```python
import pandas as pd

# Load raw data
df = pd.read_csv('data/raw_listings.csv')

# Basic exploration
print(f"Dataset shape: {df.shape}")
print(f"\nColumn types:\n{df.dtypes}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nPrice statistics:\n{df['price_kes'].describe()}")

# Location analysis
print(f"\nTop locations:\n{df['location'].value_counts().head(10)}")

# Property type analysis
print(f"\nProperty types:\n{df['property_type'].value_counts()}")
```

---

## Data Provenance

### Scraping Details
- **Scraper:** Dedicated BuyRentKenya module
- **Pages Scraped:** 30 total (20 houses/apartments + 10 land/plots)
- **Rate Limiting:** 2-second delay between requests
- **Retry Logic:** 3 attempts with exponential backoff
- **Deduplication:** Based on (price, location, bedrooms, property_type)
- **Duplicates Removed:** 77 (10.9% of total scraped)

### Ethical Considerations
- ✅ Respectful scraping with delays
- ✅ Public data only (no authentication required)
- ✅ No personal information collected
- ✅ Data used for educational purposes only

---

**Last Updated:** 2026-02-17  
**Version:** 1.0  
**Status:** Raw data collected, ready for Day 2 cleaning  
**Next Steps:** Data cleaning, feature engineering, and EDA
