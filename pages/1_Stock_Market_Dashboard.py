import streamlit as st
import requests
import pandas as pd
import altair as alt

st.title("📈 Stock Market Dashboard")

st.write(
    """
This dashboard shows real stock market data using the **Alpha Vantage API**.  

Enter a stock ticker and choose how many recent 60-minute candlesticks/points you want to see.
You can view either the stock’s price trend or its trading volume.
    """
)

st.markdown("---")

# User inputs
symbol = st.text_input("Enter a stock symbol (ex. AAPL, TSLA, MSFT)", "AAPL").upper()
num_points = st.slider(
    "Number of recent 60-minute points",
    min_value=10,
    max_value=80,
    value=24,
    help="Each point represents one hour of trading data."
)

api_key = "2GLDYP292HNQFQUP"
function = "TIME_SERIES_INTRADAY"
interval = "60min"

# simple cache so we don't spam the API with the same request over and over
@st.cache_data(ttl=300)  # cache for 5 minutes, 300 seconds
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# button-only fetch to not overwork the API and cause issues/run errors
clicked = st.button("Load data")

# ppl keep forgetting to do this
st.caption("🔄 After changing the inputs above, click **Load data** again to refresh the chart.")

if clicked:
    url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}"

    # use cached fetch instead of calling the API directly every time
    data = fetch_data(url)

    # Note: .query? helps tell the API exactly what data you want
    # separate each parameter with &. Each parameter will have a key and a value

    # 3 required parameters for Stock Market API:
    # function(type of data,TIME_SERIES_INTRADAY)
    # symbol
    # interval

    if "Time Series (60min)" in data:
        ts = data["Time Series (60min)"]

        # builds dataFrame
        df = pd.DataFrame(ts).T
        df.columns = ["open", "high", "low", "close", "volume"]
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index().tail(num_points)

        # line chart
        line = (
            alt.Chart(df.reset_index())
            .mark_line(color="black")
            .encode(
                x=alt.X("index:T", title="Time"),
                y=alt.Y("close:Q", title="Closing Price ($)"),
                tooltip=["index:T", "open", "high", "low", "close"]
                # when you hover over a point, it'll show open, high, low, close. pretty cool stuff
            )
            .properties(height=400, title=f"{symbol} Price Action (Last {num_points} Candlesticks)")
            .interactive()
        )

        st.altair_chart(line, use_container_width=True)

        #shows dataFrame
        with st.expander("View Data"):
            st.dataframe(df)

    else:
        st.error("⚠️ Could not fetch data. Try again in a minute or check your API key (rate limit = 5 calls/min).")
        # our API is very slow, so this shows up kinda frequently. Sorry lol

else:
    st.info("Enter a symbol and click **Load data** to fetch stock market data.")
