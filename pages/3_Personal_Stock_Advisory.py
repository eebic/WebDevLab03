import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.write("### 🔎 Available Models from Google:")
try:
    models = genai.list_models()
    for m in models:
        st.write(m.name)
except Exception as e:
    st.error(e)

