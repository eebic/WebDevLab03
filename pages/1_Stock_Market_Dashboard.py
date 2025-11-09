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
num_points = st.slider("Number of recent 60-minute points", min_value = 10, max_value = 80, value = 24, help = "Each point represents one hour of trading data.")

api_key = "ATBPU1SAP8PL9AN6"
function = "TIME_SERIES_INTRADAY"
interval = "60min"
    
url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}"
response = requests.get(url)
data = response.json()
#Note: .query? helps tell the API exactly what data you want
# separate each parameter with &. Each parameter will have a key and a value

#3 required parameters for Stock Market API:
    #function(type of data,TIME_SEIRES_INTRADAY)
    #symbol
    #interval

if "Time Series (60min)" in data:
    ts = data["Time Series (60min)"]
    df = pd.DataFrame(ts).T
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().tail(num_points)

    #Line chart
    line = (
        alt.Chart(df.reset_index())
        .mark_line(color="black")
        .encode(
            x=alt.X("index:T", title="Time"),
            y=alt.Y("close:Q", title="Closing Price ($)"),
            tooltip=["index:T", "open", "high", "low", "close"]
        )
        .properties(height=400, title=f"{symbol} Price Action (Last {num_points} Candlesticks)")
        .interactive()
    )

    st.altair_chart(line, use_container_width=True)

    #Displays data
    with st.expander("View Data"):
        st.dataframe(df)

else:
    st.error("⚠️ Could not fetch data. Try again in a minute or check your API key (rate limit = 5 calls/min).")
    # Our API is very slow, so this shows up kinda frequently. Sorry lol
