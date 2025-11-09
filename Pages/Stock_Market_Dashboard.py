import streamlit as st
import requests
import pandas as pd
import altair as alt

st.title("📈 Stock Market Dashboard")

st.write(
    """
This dashboard shows real stock market data using the **Alpha Vantage API**.  
Enter a stock ticker and choose how many recent 60-minute points you want to see.
You can view either the stock’s price trend or its trading volume.
    """
)

st.markdown("---")

#User inputs
symbol = st.text_input("Enter a stock symbol (ex. AAPL, TSLA, MSFT)", "AAPL").upper()
num_points = st.slider("Number of recent 60-minute points", min_value = 10, max_value = 100, value = 40, help = "Each point represents one hour of trading data.")

