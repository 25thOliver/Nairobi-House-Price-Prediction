import streamlit as st
import pandas as pd 
import numpy as np 
import pickle 
import os 

# Configuration
st.set_page_config(page_title="Nairobi House Price Predictor", layout="centered")

# Load model & data background
@st.cache_resource
def load_artifacts():
    model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'model.pkl')

    try: 
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
    except FileNotFoundError:
        st.error("Model file not found at {model_path}.")
    return model

model = load_artifacts()

ESTIMATED_MAE =  240682498

# Header
st.title("Nairobi House Price Predictor")
st.markdown("Get an instant property valuation in Nairobi based on our machine learning model.")
st.divider()

# Input Form
st.header("Property Details")

col1, col2 = st.columns(2)

with col1:
    # Top Nairobi loactions 
    locations = [
        "Kilimani", "Kileleshwa", "Lavington", "Westlands", 
        "Syokimau", "Ruaka", "Ruiru", "Nairobi CBD", "Karen", "Muthaiga"
    ]

    location = st.selectbox("Location", sorted(locations))
    size_sqft = st.number_input("Size (in SqFt)", min_value=100.0, max_value=20000.0, value=1500.0, step=100.0)
with col2:
    bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=3, step=1)
    bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=2, step=1)
st.subheader("Amenities")


# Grouped features to match the Day 2 Data Cleaning boolean flags
amenities = st.multiselect(
    "Select available amenities:",
    ["Parking", "Swimming Pool", "Gym", "Security", "Garden"]
)
st.divider()

        
