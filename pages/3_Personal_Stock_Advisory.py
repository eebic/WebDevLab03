import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

# takes the api keys
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("models/gemini-flash-latest")

ALPHA_API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
FUNCTION_DAILY = "TIME_SERIES_DAILY"
INTERVAL = "60min" 

