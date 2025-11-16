# Gemini API key: AIzaSyAESi3Zed0GIx4IgSzrynI5zTdxrDRWsiE
# put in "Secrets" of streamlit page for webdevlab03-team15

import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

#takes gemini api key from "Secrets" in streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-pro")

#takes gemini api key from "Secrets" in streamlit
ALPHA_API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
FUNCTION = "TIME_SERIES_INTRADAY"
INTERVAL = "60min"

#gets stock data from Alpha Vant
def fetch_stock_data(symbol: str, num_points: int):
    url = (
        f"https://www.alphavantage.co/query?"
        f"function={FUNCTION}&symbol={symbol}&interval={INTERVAL}&apikey={ALPHA_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    ts_key = "Time Series (60min)"
    if ts_key not in data:
        return None

    ts = data[ts_key]
    df = pd.DataFrame(ts).T
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().tail(num_points)
    return df


# summarizes data from Dataframe, similar to Page 1 (Stock_Market_Dashboard)
def summarize_data(df: pd.DataFrame, num_points: int):
    start_price = df["close"].iloc[0]
    end_price = df["close"].iloc[-1]
    change = round(end_price - start_price, 2)
    pct_change = round((change / start_price) * 100, 2)

    high_price = df["high"].max()
    low_price = df["low"].min()
    avg_volume = int(df["volume"].mean())

    return {
        "num_points": num_points,
        "start_price": start_price,
        "end_price": end_price,
        "change": change,
        "pct_change": pct_change,
        "high_price": high_price,
        "low_price": low_price,
        "avg_volume": avg_volume,
    }

# Calls Gemini with SMC (smart money concepts) prompt
def generate_smc_report(symbol: str, summary: dict, style: str) -> str:
    prompt = f"""
You are a price action trader who uses Smart Money Concepts (SMC).

Using ONLY the numeric data below for {symbol}, write a {style} analysis
that explains what is happening in terms of SMC ideas such as:
- Market structure (higher highs / higher lows, lower highs / lower lows)
- Bullish vs bearish trend
- Liquidity grabs / stop hunts (in a general sense, not exact levels)
- Areas where institutions might accumulate or distribute
- Premium vs discount zones relative to the recent range

Recent intraday data (last {summary["num_points"]} 60-minute candles):
- Starting close price: ${summary["start_price"]:.2f}
- Ending close price: ${summary["end_price"]:.2f}
- Price change: ${summary["change"]:.2f}
- Percent change: {summary["pct_change"]:.2f}%
- Highest price: ${summary["high_price"]:.2f}
- Lowest price: ${summary["low_price"]:.2f}
- Average trading volume: {summary["avg_volume"]}

Instructions:
- Explain whether the structure looks more bullish, bearish, or ranging.
- Comment on whether price seems to be moving toward liquidity or away from it.
- Use SMC language (structure, liquidity, premium/discount, smart money) but keep it understandable.
- Do NOT invent extra precise numbers or levels not provided above.
"""

    response = gemini_model.generate_content(prompt)
    return response.text

#page interface
st.title("💸 Money Moves: Smart Money Concepts")
st.write(
    """
This page uses **Google Gemini** and **Alpha Vantage** data to analyze ticker price action  
and describe possible **Smart Money Concepts (SMC)** patterns (market structure, liquidity, trend).
"""
)

symbol = st.text_input("Stock symbol (e.g., AAPL, TSLA, MSFT)", "AAPL").upper()

num_points = st.slider(
    "Number of recent 60-minute candles to analyze",
    min_value=10,
    max_value=80,
    value=24,
    help="Each point is one 60-minute candle of intraday price action.",
)

style = st.selectbox(
    "Choose analysis style",
    [
        "Beginner-friendly SMC explanation",
        "Trader-style breakdown",
        "Concise professional summary",
    ],
)

show_table = st.checkbox("Show raw OHLCV data", value=True)

st.markdown("---")

if st.button("🔍 Run SMC Analysis"):
    with st.spinner("Fetching data and generating Smart Money Concepts analysis..."):
        df = fetch_stock_data(symbol, num_points)

        if df is None:
            st.error(
                "Could not fetch data for that symbol. "
                "Try a different ticker or wait a minute for the API rate limit to reset."
            )
        else:
            summary = summarize_data(df, num_points)

            if show_table:
                st.subheader("📊 Raw OHLCV Data (Most Recent First)")
                st.dataframe(df)

            st.subheader("📌 Numeric Summary (Price Action Snapshot)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Start Close", f"${summary['start_price']:.2f}")
                st.metric("End Close", f"${summary['end_price']:.2f}")
            with col2:
                st.metric("Change", f"${summary['change']:.2f}")
                st.metric("Percent Change", f"{summary['pct_change']:.2f}%")
            with col3:
                st.metric("Highest", f"${summary['high_price']:.2f}")
                st.metric("Lowest", f"${summary['low_price']:.2f}")
                st.metric("Avg Volume", f"{summary['avg_volume']:,}")

            try:
                st.markdown("---")
                st.subheader("🤖 Gemini Smart Money Concepts Report")

                report = generate_smc_report(symbol, summary, style)
                st.write(report)

            except Exception as e:
                st.error(
                    "There was an error while generating the SMC report from Gemini. "
                    "Please check your Gemini API key or try again later."
                )
                st.caption(str(e))
