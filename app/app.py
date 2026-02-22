"""
Nairobi House Price Predictor — Day 5 Pricing App + Day 6 Dashboard
Streamlit app using trained model and results from notebooks (Day 4).
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")


# Configuration & styling
st.set_page_config(
    page_title="Nairobi House Price Predictor",
    #page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    .stMetric { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1rem; border-radius: 0.5rem; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    div[data-testid="stSidebar"] * { color: #eee !important; }
    div[data-testid="stSidebar"] .stCaption { color: #aaa !important; }
</style>
""", unsafe_allow_html=True)

# Approximate coordinates for Nairobi neighborhoods (for map)
LOCATION_COORDS = {
    "Donholm": (-1.3050, 36.8750),
    "Embakasi": (-1.3200, 36.8900),
    "Karen": (-1.3209, 36.6849),
    "Kasarani": (-1.2180, 36.8950),
    "Kileleshwa": (-1.2950, 36.7820),
    "Kilimani": (-1.2850, 36.7867),
    "Kitisuru": (-1.2750, 36.7650),
    "Langata": (-1.3500, 36.7500),
    "Lavington": (-1.2880, 36.7780),
    "Muthaiga": (-1.2650, 36.8100),
    "Nairobi CBD": (-1.2921, 36.7820),
    "Nairobi Other": (-1.2921, 36.7820),
    "Ngong": (-1.3650, 36.6680),
    "Parklands": (-1.2680, 36.8180),
    "Ridgeways": (-1.3400, 36.7600),
    "Runda": (-1.2280, 36.8200),
    "South B": (-1.3180, 36.8350),
    "South C": (-1.3250, 36.8280),
    "Syokimau": (-1.3980, 36.9180),
    "Upperhill": (-1.2980, 36.8050),
    "Utawala": (-1.3580, 36.8950),
    "Westlands": (-1.2669, 36.8117),
}

# Load artifacts
@st.cache_resource
def load_artifacts():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base, "data", "model.pkl")
    try:
        with open(model_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error(f"Model not found at `{model_path}`. Run Day 4 script first.")
        return None


@st.cache_data
def load_location_stats():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df_path = os.path.join(base, "data", "clean_listings.csv")
    try:
        df = pd.read_csv(df_path)
        return df.groupby("location")["price_kes"].median().sort_values(ascending=False)
    except FileNotFoundError:
        return None


@st.cache_data
def load_model_comparison():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "data", "model_comparison.csv")
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return None


@st.cache_data
def load_listings_count():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "data", "clean_listings.csv")
    try:
        return len(pd.read_csv(path))
    except FileNotFoundError:
        return 0


@st.cache_data
def load_dashboard_data():
    """Load full clean listings for Day 6 dashboard."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "data", "clean_listings.csv")
    try:
        df = pd.read_csv(path)
        if "listing_date" in df.columns:
            df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")
        if "month" in df.columns:
            df["month"] = pd.to_numeric(df["month"], errors="coerce")
        return df
    except FileNotFoundError:
        return None


def get_top_drivers_from_model(artifact):
    """Derive top 5 price drivers from trained model feature importances."""
    model = artifact["model"]
    feature_cols = artifact["feature_cols"]
    if not hasattr(model, "feature_importances_"):
        return []
    imp = model.feature_importances_
    order = np.argsort(imp)[::-1]
    return [(feature_cols[i], imp[i]) for i in order[:5]]


def format_price(median_kes):
    """Format price for display (rental = thousands, sale = millions)."""
    if median_kes >= 1e6:
        return f"KES {median_kes/1e6:.1f}M"
    if median_kes >= 1e3:
        return f"KES {median_kes/1e3:.0f}K"
    return f"KES {median_kes:,.0f}"


artifact = load_artifacts()
location_medians = load_location_stats()
comparison_df = load_model_comparison()

if artifact is None:
    st.stop()

model = artifact["model"]
scaler = artifact.get("scaler")
use_scaler = artifact.get("use_scaler", False)
le_location = artifact["le_location"]
le_type = artifact["le_type"]
feature_cols = artifact["feature_cols"]
model_name = artifact.get("model_name", "Model")

# MAE and metrics from notebook results (model_comparison.csv)
if comparison_df is not None and len(comparison_df) > 0:
    best_row = comparison_df.loc[comparison_df["R2"].idxmax()]
    MAE = float(best_row["MAE"])
    best_model_display = best_row["Model"]
    best_r2 = float(best_row["R2"])
else:
    MAE = 131_812  # fallback
    best_model_display = model_name
    best_r2 = 0.23
n_listings = load_listings_count()

top_drivers = get_top_drivers_from_model(artifact)

# Sidebar
with st.sidebar:
    st.title("Nairobi Valuer")
    st.caption("Powered by ML • LTLab Fellowship")
    st.divider()

    nav = st.radio(
        "Navigate",
        ["Predict Price", "Market Insights", "Dashboard", "Nairobi Map"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(f"**Model:** {best_model_display}")
    st.caption(f"**Data:** {n_listings} listings (BuyRentKenya)")
    st.caption(f"**R²:** {best_r2:.2f} | **MAE:** KES {MAE:,.0f}")

# Main: Predict Price
if nav == "Predict Price":
    st.title("Nairobi House Price Predictor")
    st.markdown(f"Get an instant property valuation based on our trained model and **{n_listings} real listings** from Nairobi.")
    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("Location & Size")
        locations = sorted(le_location.classes_.tolist())
        default_loc = locations.index("Kilimani") if "Kilimani" in locations else 0
        location = st.selectbox("Location", locations, index=default_loc)
        size_sqft = st.number_input("Size (sqft)", min_value=100.0, max_value=50000.0, value=1500.0, step=100.0)

    with col2:
        st.subheader("Property Type & Rooms")
        property_types = le_type.classes_.tolist()
        property_type = st.selectbox("Property Type", property_types)
        is_land = 1 if property_type in ("Land", "Plot") else 0

        if is_land:
            bedrooms = 0
            bathrooms = 0
            st.info("Land/Plot: bedrooms & bathrooms set to 0.")
        else:
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=3, step=1)
            bathrooms = st.number_input("Bathrooms", min_value=0, max_value=10, value=2, step=1)

    with col3:
        st.subheader("Amenities")
        amenities = st.multiselect(
            "Select amenities",
            ["Parking", "Swimming Pool", "Gym", "Security", "Garden"],
        )
        has_parking = 1 if "Parking" in amenities else 0
        has_pool = 1 if "Swimming Pool" in amenities else 0
        has_gym = 1 if "Gym" in amenities else 0
        has_security = 1 if "Security" in amenities else 0
        has_garden = 1 if "Garden" in amenities else 0
        amenity_score = len(amenities)

    st.divider()

    if st.button("Predict Price", type="primary", use_container_width=True):
        with st.spinner("Analyzing market data..."):
            try:
                # Encode categoricals
                loc_enc = le_location.transform([location])[0]
                type_enc = le_type.transform([property_type])[0]

                X = pd.DataFrame(
                    [
                        {
                            "bedrooms": bedrooms,
                            "bathrooms": max(1, bathrooms) if not is_land else 0,
                            "size_sqft": size_sqft,
                            "amenity_score": amenity_score,
                            "has_parking": has_parking,
                            "has_pool": has_pool,
                            "has_gym": has_gym,
                            "has_security": has_security,
                            "has_garden": has_garden,
                            "is_land": is_land,
                            "location_enc": loc_enc,
                            "property_type_enc": type_enc,
                        }
                    ],
                    columns=feature_cols,
                )

                if use_scaler and scaler is not None:
                    X = scaler.transform(X)

                pred_price = float(np.clip(model.predict(X), 0, None)[0])
                lower = max(0, pred_price - MAE)
                upper = pred_price + MAE

                st.success("Prediction complete!")
                st.metric("Estimated Price", format_price(pred_price))
                st.caption(f"**Expected range:** {format_price(lower)} – {format_price(upper)} (± MAE)")

                # Explainability
                st.subheader("What's driving this price?")
                driver_text = []
                driver_text.append(f"**Size:** {size_sqft:,.0f} sqft is the strongest price driver in our model.")
                if location_medians is not None and location in location_medians.index:
                    loc_med = location_medians.loc[location]
                    driver_text.append(f"**Location:** {location} — median {format_price(loc_med)} in our data.")
                else:
                    driver_text.append(f"**Location:** {location} — premium area.")
                driver_text.append(f"**Rooms:** {bedrooms} bed, {bathrooms} bath — more rooms typically add value.")
                driver_text.append(f"**Amenities:** {len(amenities)} selected — {', '.join(amenities) if amenities else 'None'}.")

                st.info("\n\n".join(driver_text))

            except Exception as e:
                st.error(f"Prediction failed: {e}")


# Main: Market Insights
elif nav == "Market Insights":
    st.title("Market Insights")
    st.markdown("Key findings from our EDA and model training.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 5 Price Drivers")
        if top_drivers:
            for i, (feat, imp) in enumerate(top_drivers, 1):
                label = feat.replace("_", " ").title()
                st.markdown(f"**{i}. {label}** ({imp*100:.1f}% importance)")
        else:
            st.caption("Feature importance not available for this model.")

    with col2:
        st.subheader("Location Premiums (Median Price)")
        if location_medians is not None:
            top_locs = location_medians.head(10)
            for loc, med in top_locs.items():
                st.caption(f"**{loc}:** {format_price(med)}")
        else:
            st.caption("Data not loaded.")

        st.divider()
        st.subheader("Model Performance")
        st.caption(f"**Best model:** {best_model_display}")
        st.caption(f"**R²:** {best_r2:.2f} (explains {max(0, best_r2)*100:.0f}% of price variance)")
        st.caption(f"**MAE:** {format_price(MAE)} (avg error)")
        if comparison_df is not None:
            lr = comparison_df[comparison_df["Model"].str.contains("Linear", case=False, na=False)]
            if not lr.empty:
                st.caption(f"**Baseline (Linear Reg):** R² {float(lr['R2'].iloc[0]):.2f}")

    if comparison_df is not None and len(comparison_df) > 0:
        st.divider()
        st.subheader("Model Comparison (from notebook)")
        st.dataframe(
            comparison_df[["Model", "MAE", "R2"]].rename(columns={"MAE": "MAE (KES)", "R2": "R²"}),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.subheader("Feature Importance")
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    imp_path = os.path.join(base, "data", "feature_importance_top.png")
    if os.path.exists(imp_path):
        st.image(imp_path, use_column_width=True)
    else:
        st.caption("Run Day 4 script to generate feature importance plots.")

# Main: Dashboard (Day 6)
elif nav == "Dashboard":
    st.title("Market Dashboard")
    st.markdown("Business story at a glance: location, trends, price per sqft, and amenity impact.")
    st.divider()

    df_dash = load_dashboard_data()
    if df_dash is None or len(df_dash) == 0:
        st.warning("No dashboard data. Ensure `data/clean_listings.csv` exists.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "Median price by location",
            "Monthly price trend",
            "Price per sqft comparison",
            "Amenity impact analysis",
        ])

        with tab1:
            st.subheader("Median price by location")
            loc_med = df_dash.groupby("location")["price_kes"].median().sort_values(ascending=True)
            top_n = st.slider("Number of locations to show", 5, min(30, len(loc_med)), 15, key="tab1_n")
            plot_locs = loc_med.tail(top_n)
            fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.35)))
            ax.barh(range(len(plot_locs)), plot_locs.values, color="steelblue", alpha=0.85)
            ax.set_yticks(range(len(plot_locs)))
            ax.set_yticklabels(plot_locs.index, fontsize=9)
            ax.set_xlabel("Median price (KES)")
            ax.set_title("Median listing price by location")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            with st.expander("View table"):
                st.dataframe(
                    loc_med.sort_values(ascending=False).to_frame("median_price_kes").rename_axis("location"),
                    use_container_width=True,
                    hide_index=True,
                )

        with tab2:
            st.subheader("Monthly price trend")
            if "month" in df_dash.columns and df_dash["month"].notna().any():
                monthly = df_dash.groupby("month").agg(
                    median_price=("price_kes", "median"),
                    count=("price_kes", "count"),
                ).reset_index()
                monthly = monthly.sort_values("month")
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(monthly["month"], monthly["median_price"], marker="o", color="steelblue", linewidth=2)
                ax.set_xlabel("Month")
                ax.set_ylabel("Median price (KES)")
                ax.set_title("Monthly median price trend")
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                st.caption(f"Listings per month: {monthly.set_index('month')['count'].to_dict()}")
            else:
                st.info("No month data available. Add listing_date/month to your data for trends.")
            with st.expander("View monthly aggregates"):
                if "month" in df_dash.columns:
                    agg = df_dash.groupby("month").agg(median_price_kes=("price_kes", "median"), count=("price_kes", "count")).reset_index()
                    st.dataframe(agg, use_container_width=True, hide_index=True)
                else:
                    st.caption("No month column.")

        with tab3:
            st.subheader("Price per sqft comparison")
            # Exclude land and invalid price_per_sqft for comparison
            df_sqft = df_dash[df_dash["is_land"] != 1].copy()
            df_sqft = df_sqft[df_sqft["price_per_sqft"].notna() & (df_sqft["price_per_sqft"] > 0)]
            # Cap extreme outliers for visualization (e.g. 99th percentile)
            cap = df_sqft["price_per_sqft"].quantile(0.99)
            df_sqft = df_sqft[df_sqft["price_per_sqft"] <= cap]
            compare_by = st.radio("Compare by", ["location", "property_type"], horizontal=True, key="tab3_by")
            if len(df_sqft) > 0:
                sqft_med = df_sqft.groupby(compare_by)["price_per_sqft"].median().sort_values(ascending=True)
                top_n_sqft = st.slider("Number to show", 5, min(25, len(sqft_med)), 12, key="tab3_n")
                plot_sqft = sqft_med.tail(top_n_sqft)
                fig, ax = plt.subplots(figsize=(8, max(4, len(plot_sqft) * 0.35)))
                ax.barh(range(len(plot_sqft)), plot_sqft.values, color="seagreen", alpha=0.85)
                ax.set_yticks(range(len(plot_sqft)))
                ax.set_yticklabels(plot_sqft.index, fontsize=9)
                ax.set_xlabel("Median price per sqft (KES)")
                ax.set_title(f"Price per sqft by {compare_by.replace('_', ' ')}")
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            else:
                st.caption("No valid price-per-sqft data after filtering.")
            with st.expander("View table"):
                if len(df_sqft) > 0:
                    st.dataframe(
                        df_sqft.groupby(compare_by)["price_per_sqft"].median().sort_values(ascending=False).to_frame("median_price_per_sqft_kes").rename_axis(compare_by),
                        use_container_width=True,
                        hide_index=True,
                    )

        with tab4:
            st.subheader("Amenity impact analysis")
            amenity_cols = [c for c in df_dash.columns if c.startswith("has_") and c in df_dash.columns]
            if not amenity_cols:
                st.caption("No amenity columns in data.")
            else:
                rows = []
                for col in amenity_cols:
                    name = col.replace("has_", "").replace("_", " ").title()
                    with_amenity = df_dash[df_dash[col] == 1]["price_kes"].median()
                    without_amenity = df_dash[df_dash[col] == 0]["price_kes"].median()
                    count_with = (df_dash[col] == 1).sum()
                    rows.append({
                        "amenity": name,
                        "median_price_with": with_amenity,
                        "median_price_without": without_amenity,
                        "premium_kes": with_amenity - without_amenity,
                        "listings_with": int(count_with),
                    })
                impact_df = pd.DataFrame(rows).sort_values("premium_kes", ascending=False)
                impact_df["premium_pct"] = (
                    (impact_df["median_price_with"] - impact_df["median_price_without"])
                    / impact_df["median_price_without"].replace(0, np.nan) * 100
                )
                st.dataframe(
                    impact_df.style.format({
                        "median_price_with": "{:,.0f}",
                        "median_price_without": "{:,.0f}",
                        "premium_kes": "{:,.0f}",
                        "premium_pct": "{:.1f}%",
                    }, na_rep="—"),
                    use_container_width=True,
                    hide_index=True,
                )
                # Simple bar: premium in KES
                fig, ax = plt.subplots(figsize=(8, max(4, len(impact_df) * 0.4)))
                y_pos = range(len(impact_df))
                ax.barh(y_pos, impact_df["premium_kes"], color="coral", alpha=0.85)
                ax.set_yticks(y_pos)
                ax.set_yticklabels(impact_df["amenity"], fontsize=10)
                ax.set_xlabel("Median price premium (KES) — with vs without amenity")
                ax.set_title("Amenity impact on price")
                ax.axvline(0, color="gray", linewidth=0.8)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

    st.divider()

# Main: Nairobi Map
else:
    st.title("Nairobi: Property Locations")
    st.markdown("Neighborhoods in our dataset. Click and zoom to explore.")
    st.divider()

    map_data = pd.DataFrame(
        [
            {"lat": coords[0], "lon": coords[1], "location": loc}
            for loc, coords in LOCATION_COORDS.items()
        ]
    )
    st.map(map_data, latitude="lat", longitude="lon", size=100, zoom=10)
    st.caption("Map shows approximate centers of Nairobi neighborhoods in our training data.")
