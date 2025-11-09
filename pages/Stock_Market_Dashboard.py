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

api_key = "ATBPU1SAP8PL9AN6"
function = "TIME_SERIES_INTRADAY"
interval = "60min"
    
url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}"
response = requests.get(url)
data = response.json()
#query? string helps tell the API exactly what data you want
# separate each parameter with &. Each parameter will have a key and a value

#3 required parameters for Stock Market API:
    #function(type of data,TIME_SEIRES_INTRADAY)
    #symbol
    #interval
