import streamlit as st
import requests
import pandas as pd
import altair as alt

st.title("📈 Stock Market Dashboard")

st.write(
    """
Use this dashboard to explore recent **daily stock data** from a public
stock market API (Alpha Vantage). Enter a ticker symbol, choose how many days of history
you want, and select which metric to focus on.
    """
)

st.markdown("---")
