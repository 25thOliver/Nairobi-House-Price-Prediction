# Nairobi House Price Prediction

A **property valuation app** for Nairobi: get price estimates and market insights from real listings. Built in 6 days (LTLab Fellowship sprint) — scraping → cleaning → modeling → app and dashboard.

---

## Try it

- **Live app:** Deploy from this repo on [Streamlit Community Cloud](https://share.streamlit.io) (see [DEPLOY.md](DEPLOY.md)).
- **Locally:** `streamlit run app/app.py` (from the project root; requires Python, see [Run it yourself](#run-it-yourself)).

**In the app:** Predict price (location, size, rooms, amenities), explore Market Insights and a 4-tab Dashboard (median price by location, monthly trend, price per sqft, amenity impact), and view a Nairobi map.

---

## What’s in the box

| Deliverable | Description |
|-------------|--------------|
| **Data** | Listings from BuyRentKenya (scraped, cleaned, feature-engineered). |
| **Model** | Best performer: XGBoost (R² ~0.26, MAE ~125K KES). Comparison with Linear Regression and Random Forest in notebooks. |
| **App** | Streamlit: price predictor, top drivers, location premiums, model comparison. |
| **Dashboard** | Median price by location, monthly trend, price per sqft, amenity impact. |

---

## Sprint at a glance

| Day | Focus | Status |
|-----|-------|--------|
| 1 | Data collection (BuyRentKenya scraper) | ✅ |
| 2 | Cleaning & feature engineering | ✅ |
| 3 | EDA & baseline model | ✅ |
| 4 | Model improvement (RF, XGBoost) & explainability | ✅ |
| 5 | Pricing app (Streamlit) | ✅ |
| 6 | Dashboard & presentation | ✅ |

---

## Run it yourself

**Prerequisites:** Python 3.10+, and `data/model.pkl`, `data/clean_listings.csv`, `data/model_comparison.csv` in the repo (or from running the notebooks).

```bash
git clone https://github.com/25thOliver/Nairobi-House-Price-Prediction.git
cd Nairobi-House-Price-Prediction
pip install -r requirements.txt
streamlit run app/app.py
```

**With Docker (includes scraping & Jupyter):**

```bash
docker-compose up -d
docker-compose exec scraper bash
# Inside container: streamlit run app/app.py  OR  jupyter notebook ...
```

---

## Project layout

```
├── app/app.py              # Streamlit app + dashboard
├── data/                   # clean_listings.csv, model.pkl, model_comparison.csv
├── notebooks/              # 01 cleaning, 02 EDA & baseline, 03 model improvement
├── scrapers/               # BuyRentKenya scraper (base + brk)
├── requirements.txt
├── DEPLOY.md               # How to put the app online
└── STREAMLIT_CLOUD_CHECKLIST.md
```

---

## Tech stack

Python 3.11 · Pandas, NumPy · Scikit-learn, XGBoost · Matplotlib · Streamlit · Docker (optional)

---

**Oliver** — [@25thOliver](https://github.com/25thOliver) · LTLab Fellowship 2026
