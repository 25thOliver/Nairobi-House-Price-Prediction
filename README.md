# Nairobi House Price Prediction

A prop-tech MVP built in a 6-day intensive sprint — from raw data to a deployed pricing app.
Built as part of the **LTLab Fellowship 6-Day Intensive Sprint**.

---

## Sprint Progress

| Day | Focus | Status |
|-----|-------|--------|
| **Day 1** | Data Collection & Structuring | ✅ Complete |
| **Day 2** | Data Cleaning & Feature Engineering | ✅ Complete |
| **Day 3** | EDA & Baseline Model | Pending |
| **Day 4** | Model Improvement & Explainability | Pending |
| **Day 5** | Pricing App Deployment | Pending |
| **Day 6** | Dashboard & Presentation | Pending |

---

## Project Structure

```
NairobiHousePred/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── data/
│   ├── raw_listings.csv        # 628 scraped listings
│   ├── clean_listings.csv      # Cleaned & feature-engineered dataset
│   ├── data_dictionary.md      # Column definitions & statistics
│   └── eda_visuals.png         # EDA charts
├── scrapers/
│   ├── base_scraper.py         # Base class with retry logic
│   ├── jiji_scraper.py         # Jiji.co.ke multi-category scraper
│   └── multi_source_scraper.py # Aggregator (extensible to more sites)
└── notebooks/
    └── 01_data_cleaning.ipynb  # Cleaning & feature engineering
```

---

## Quick Start

```bash
# Clone & build
git clone https://github.com/25thOliver/Nairobi-House-Price-Prediction.git
cd NairobiHousePred
docker-compose build && docker-compose up -d

# Enter container
docker-compose exec scraper bash

# Collect data (Day 1)
python -m scrapers.multi_source_scraper

# Launch Jupyter (Day 2)
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''
# Open: http://localhost:8888
```

---

## Day 1 — Data Collection

**Source:** Jiji.co.ke (Houses & Apartments + Land & Plots)

| Metric | Value |
|--------|-------|
| Total scraped | 705 listings |
| After deduplication | **628 unique listings** |
| Price range | 370K – 15.5B KES |
| Median price | 130M KES |
| Locations | 25+ Nairobi neighborhoods |
| Property types | 10 types |

**Scraping Architecture:**
- `base_scraper.py` — HTTP handling, retry logic (3 attempts), user-agent rotation, 2s rate limiting
- `jiji_scraper.py` — Multi-category scraping, regex extraction, URL-based deduplication
- `multi_source_scraper.py` — Aggregates sources, removes duplicates by (price, location, bedrooms, type)

---

## Day 2 — Data Cleaning & Feature Engineering

**Notebook:** `notebooks/01_data_cleaning.ipynb`

**Cleaning steps:**
- Removed duplicates
- Replaced missing `size_sqft` (0.0 → NaN → median imputation per property type)
- Standardized location names (e.g. `Nairobi Central` → `Nairobi CBD`)
- Reclassified `Other` property types using bedrooms & size heuristics
- Removed price outliers using IQR method (5th–95th percentile)

**New features created:**

| Feature | Description |
|---------|-------------|
| `price_per_sqft` | Price ÷ size |
| `amenity_score` | Count of amenities (0–9) |
| `month` | Extracted from listing date |
| `has_parking`, `has_pool`, `has_gym`, `has_security`, `has_garden` | Boolean amenity flags |
| `is_land` | True if Plot or Land |

**Output:** `data/clean_listings.csv` + `data/eda_visuals.png`

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.11 |
| Scraping | BeautifulSoup4, Requests |
| Data | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Notebooks | Jupyter |
| Container | Docker, Docker Compose |
| Version Control | Git, GitHub |

---

## Author

**Oliver** — LTLab Fellowship, Cohort 2026
GitHub: [@25thOliver](https://github.com/25thOliver)