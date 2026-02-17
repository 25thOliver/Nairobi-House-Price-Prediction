# 🏠 Nairobi House Price Prediction

## Project Overview

This project predicts house prices in Nairobi, Kenya using machine learning. Built as part of the **LTLab Fellowship 6-Day Intensive Sprint**, it simulates a real startup execution cycle.

### Objectives
- Collect 300-800 Nairobi property listings via web scraping
- Build and train ML models (Linear Regression, Random Forest, XGBoost)
- Deploy a working price prediction app
- Create a market insights dashboard
- Deliver professional presentation

---

## Sprint Timeline

| Day | Focus | Status |
|-----|-------|--------|
| **Day 1** | Data Collection & Structuring | **Complete** |
| **Day 2** | Data Cleaning & Feature Engineering | ending |
| **Day 3** | EDA & Baseline Model | Pending |
| **Day 4** | Model Improvement & Explainability | Pending |
| **Day 5** | Pricing App Deployment | Pending |
| **Day 6** | Dashboard & Presentation | Pending |

---

## Project Structure

```
NairobiHousePred/
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env                        # Environment variables
├── data/
│   ├── raw_listings.csv       # Scraped data (628 listings)
│   └── data_dictionary.md     # Data documentation
└── scrapers/
    ├── __init__.py
    ├── base_scraper.py        # Base scraper class
    ├── jiji_scraper.py        # Jiji.co.ke multi-category scraper
    └── multi_source_scraper.py # Multi-source aggregator
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Setup & Run

```bash
# Clone repository
git clone https://github.com/25thOliver/Nairobi-House-Price-Prediction.git
cd NairobiHousePred

# Build and start Docker container
docker-compose build
docker-compose up -d

# Access container
docker-compose exec scraper bash

# Run multi-source scraper
python -m scrapers.multi_source_scraper
```

---

## Day 1 Results

### Data Collection Summary
- **Total Listings Scraped:** 705
- **Unique Listings (after deduplication):** 628
- **Source:** Jiji.co.ke
- **Categories:** Houses & Apartments + Land & Plots
- **Pages Scraped:** 30 pages (20 from houses, 10 from land)

### Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Records** | 628 |
| **Price Range** | 370K - 15.5B KES |
| **Mean Price** | 506.5M KES |
| **Median Price** | 130M KES |
| **Locations Covered** | 25+ Nairobi neighborhoods |
| **Property Types** | 10 types |

### Top 10 Locations
1. Nairobi (General) - 177 listings
2. Nairobi Central - 61 listings
3. Westlands - 60 listings
4. Kasarani - 40 listings
5. Kilimani - 39 listings
6. Kileleshwa - 33 listings
7. Kahawa - 32 listings
8. Utawala - 31 listings
9. Lavington - 30 listings
10. Karen - 22 listings

### Property Type Distribution
- Apartment: 180 (28.7%)
- Other: 161 (25.6%)
- Plot: 108 (17.2%)
- Maisonette: 55 (8.8%)
- House: 35 (5.6%)
- Land: 26 (4.1%)
- Mansion: 21 (3.3%)
- Villa: 17 (2.7%)
- Bungalow: 13 (2.1%)
- Townhouse: 12 (1.9%)

---

## Tech Stack

- **Language:** Python 3.11
- **Web Scraping:** BeautifulSoup4, Requests, Selenium
- **Data Processing:** Pandas, NumPy
- **Containerization:** Docker, Docker Compose
- **Version Control:** Git, GitHub

---

## Scraping Architecture

### Multi-Source Strategy
The scraper uses a modular architecture:

1. **Base Scraper** (`base_scraper.py`)
   - Common HTTP request handling
   - Retry logic with exponential backoff
   - User-agent rotation
   - Rate limiting (2-second delay)

2. **Jiji Scraper** (`jiji_scraper.py`)
   - Multi-category support
   - Regex-based data extraction
   - Automatic pagination
   - Duplicate detection via URL tracking

3. **Multi-Source Aggregator** (`multi_source_scraper.py`)
   - Combines data from multiple sources
   - Deduplication based on (price, location, bedrooms, type)
   - Extensible for additional websites

### Data Quality Features
- Automatic retry on failed requests (3 attempts)
- Duplicate removal (77 duplicates removed)
- Missing value handling
- Data type validation
- Respectful scraping with delays

---

## Day 1 Deliverables

- [x] Clean GitHub repository
- [x] Docker environment
- [x] Multi-source web scraper
- [x] Raw dataset (628 listings - **Target exceeded!**)
- [x] Data dictionary
- [x] README documentation

---