import math
import numpy as np
import pickle
import streamlit as st
import base64
import joblib
import requests
import os

st.set_page_config(page_title='IPL Score Predictor 2024', layout="centered")

MODEL_URL = "https://huggingface.co/sankarans2001/IPL-Score-Predictor/blob/main/rfr_model.pkl"
MODEL_PATH = "rfr_model.pkl"

@st.cache_resource
def load_model():
    # Download model if not already present
    if not os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "wb") as f:
            f.write(requests.get(MODEL_URL).content)
    return joblib.load(MODEL_PATH)

# Load and cache model
model = load_model()

def get_base64_of_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

img_base64 = get_base64_of_image("background.png")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-attachment: fixed;
        background-size: cover;
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    .stAlert {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border-radius: 10px;
        padding: 15px;
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        z-index: 100;
    }
    </style>

    <div class="footer">
        Created by Sankaran S
    </div>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align: center; color: white;'>🏏 IPL Score Predictor 2024</h1>", unsafe_allow_html=True)

with st.expander("ℹ️ What is this app?"):
    st.info("""
    This app predicts the final score of an ongoing IPL match based on:
    - Current batting and bowling team
    - Runs, wickets, and overs
    - Performance in the last 5 overs

    📌 Tip: Works best after 5 overs are completed!
    """)

# List of Teams
teams = [
    'Chennai Super Kings', 'Delhi Daredevils', 'Kings XI Punjab',
    'Kolkata Knight Riders', 'Mumbai Indians', 'Rajasthan Royals',
    'Royal Challengers Bangalore', 'Sunrisers Hyderabad'
]

def encode_team(team):
    return [1 if team == t else 0 for t in teams]

# Form layout
with st.form("prediction_form"):
    st.subheader("Match Information")

    batting_team = st.selectbox('🏏 Select Batting Team:', teams)
    bowling_team = st.selectbox('🎯 Select Bowling Team:', teams)

    col1, col2 = st.columns(2)
    with col1:
        overs = st.number_input(
            '⏱️ Overs Completed (e.g., 10.3 for 10 overs 3 balls):',
            min_value=5.0, max_value=19.5, step=0.1
        )
    with col2:
        runs = st.number_input('🏃 Total Runs Scored:', min_value=0, max_value=300, step=1)

    wickets = st.slider('💥 Wickets Fallen:', 0, 10)

    col3, col4 = st.columns(2)
    with col3:
        runs_in_prev_5 = st.number_input('🔥 Runs in Last 5 Overs:', min_value=0, max_value=100, step=1)
    with col4:
        wickets_in_prev_5 = st.number_input('⚡ Wickets in Last 5 Overs:', min_value=0, max_value=10, step=1)

    
    submit = st.form_submit_button("🎯 Predict Final Score")

# Prediction logic
if submit:
    if overs - math.floor(overs) > 0.5:
        st.error("⚠️ Invalid overs input. One over has only 6 balls (e.g., 10.3 is valid, 10.7 is not).")

    elif batting_team == bowling_team:
        st.error("❌ Please select different teams for batting and bowling.")

    elif wickets_in_prev_5 > wickets:
        st.error("⚠️ Wickets in the last 5 overs cannot be more than total wickets fallen in the match.")

    elif runs_in_prev_5 > runs:
        st.error("⚠️ Runs in the last 5 overs cannot be more than total runs scored in the match.")

    else:
        prediction_array = []
        prediction_array += encode_team(batting_team)
        prediction_array += encode_team(bowling_team)
        prediction_array += [runs, wickets, overs, runs_in_prev_5, wickets_in_prev_5]

        prediction_array = np.array([prediction_array])
        predicted_score = int(round(model.predict(prediction_array)[0]))

        st.success(f"🏁 **Predicted Final Score:** Between **{predicted_score - 5}** and **{predicted_score + 5}** runs")

