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


        
