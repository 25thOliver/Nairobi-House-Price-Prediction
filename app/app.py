"""
Nairobi House Price Predictor — Day 5 Pricing App
Streamlit app using trained Random Forest model from Day 4.
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import warnings

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

# Top 5 price drivers from Day 4
TOP_DRIVERS = [
    ("Size (sqft)", "size_sqft", "Larger properties command higher prices. Our model weights this as the #1 driver."),
    ("Bedrooms", "bedrooms", "More bedrooms add significant value, especially in family-oriented areas."),
    ("Bathrooms", "bathrooms", "En-suite and additional bathrooms increase valuation."),
    ("Location", "location_enc", "Premium areas (Karen, Muthaiga, Lavington) have higher median prices."),
    ("Property Type", "property_type_enc", "Houses, villas, and mansions typically outperform apartments."),
]

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


artifact = load_artifacts()
location_medians = load_location_stats()

if artifact is None:
    st.stop()

model = artifact["model"]
scaler = artifact.get("scaler")
use_scaler = artifact.get("use_scaler", False)
le_location = artifact["le_location"]
le_type = artifact["le_type"]
feature_cols = artifact["feature_cols"]
model_name = artifact.get("model_name", "Model")
MAE = 240_682_498  # Random Forest MAE from Day 4


# Sidebar
with st.sidebar:
    st.title("Nairobi Valuer")
    st.caption("Powered by ML • LTLab Fellowship")
    st.divider()

    nav = st.radio(
        "Navigate",
        ["Predict Price", "Market Insights", "Nairobi Map"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("**Model:** Random Forest")
    st.caption("**Data:** 600+ listings from Jiji.co.ke")
    st.caption("**R²:** ~0.36 | **MAE:** ~241M KES")

# Main: Predict Price
if nav == "Predict Price":
    st.title("Nairobi House Price Predictor")
    st.markdown("Get an instant property valuation based on our trained model and **600+ real listings** from Nairobi.")
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
                st.metric("Estimated Price", f"KES {pred_price:,.0f}")
                st.caption(f"**Expected range:** KES {lower:,.0f} – KES {upper:,.0f} (± MAE)")

                # Explainability
                st.subheader("What's driving this price?")
                driver_text = []
                driver_text.append(f"**Size:** {size_sqft:,.0f} sqft is the strongest price driver in our model.")
                if location_medians is not None and location in location_medians.index:
                    loc_med = location_medians.loc[location] / 1e6
                    driver_text.append(f"**Location:** {location} — median ~{loc_med:.0f}M KES in our data.")
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
        for i, (name, _, desc) in enumerate(TOP_DRIVERS, 1):
            st.markdown(f"**{i}. {name}**  \n{desc}")
            st.caption("")

    with col2:
        st.subheader("Location Premiums (Median Price)")
        if location_medians is not None:
            top_locs = location_medians.head(10)
            for loc, med in top_locs.items():
                st.caption(f"**{loc}:** KES {med:,.0f}M")
        else:
            st.caption("Data not loaded.")

        st.divider()
        st.subheader("Model Performance")
        st.caption("**Best model:** Random Forest")
        st.caption("**R²:** 0.36 (explains 36% of price variance)")
        st.caption("**MAE:** ~241M KES (avg error)")
        st.caption("**Baseline (Linear Reg):** R² 0.24")

    st.divider()
    st.subheader("Feature Importance")
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    imp_path = os.path.join(base, "data", "feature_importance_top.png")
    if os.path.exists(imp_path):
        st.image(imp_path, use_column_width=True)
    else:
        st.caption("Run Day 4 script to generate feature importance plots.")

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
