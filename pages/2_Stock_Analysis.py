# Gemini API key: AIzaSyAESi3Zed0GIx4IgSzrynI5zTdxrDRWsiE
# put in "Secrets" of streamlit page for webdevlab03-team15

import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai
import datetime as dt

gemini_key = st.secrets["GEMINI_API_KEY"]
