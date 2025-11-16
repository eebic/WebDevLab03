# Gemini API key: AIzaSyAESi3Zed0GIx4IgSzrynI5zTdxrDRWsiE
# put in "Secrets" of streamlit page for webdevlab03-team15

import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

#grab api keys from "Secrets" in streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

#3rd model of gemini to try lol
gemini_model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

ALPHA_API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
FUNCTION = "TIME_SERIES_INTRADAY"
INTERVAL = "60min"


#grabs stock data from alpha vantage
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


#creates basis for gemini prompt
def summarize(df, num_points):
    start = df["close"].iloc[0]
    end = df["close"].iloc[-1]
    change = round(end - start, 2)
    pct = round((change / start) * 100, 2)
    high = df["high"].max()
    low = df["low"].min()
    vol = int(df["volume"].mean())

    return {
        "num_points": num_points,
        "start": start,
        "end": end,
        "change": change,
        "pct": pct,
        "high": high,
        "low": low,
        "vol": vol,
    }


#gemini smart money concept analysis
def generate_smc_report(symbol: str, summary: dict, style: str):
    prompt = f"""
You are an expert Smart Money Concepts (SMC) price action trader.

Analyze the recent intraday structure for the stock {symbol} using ONLY the data below.
Connect the price behavior to SMC ideas such as:
- Market Structure (higher highs / lower lows)
- Liquidity hunts & stop runs
- Premium vs Discount zones
- Accumulation vs Distribution
- Institutional activity (Smart Money)
- Trend bias (bullish / bearish / ranging)

Recent {summary['num_points']} intraday 60-minute candles:
- Starting close: ${summary['start']:.2f}
- Ending close: ${summary['end']:.2f}
- Net change: ${summary['change']:.2f}
- Percent change: {summary['pct']:.2f}%
- High of range: ${summary['high']:.2f}
- Low of range: ${summary['low']:.2f}
- Average volume: {summary['vol']}

Write a {style} SMC report.
Do NOT invent any extra numeric values.
Only use the data provided.
"""

    response = gemini_model.generate_content(prompt)
    return response.text


#page interface
st.title("📊 Smart Money Concepts — AI Stock Analysis (Phase 3)")
st.write(
    """
This tool uses **Google Gemini** + real **Alpha Vantage intraday data**  
to generate a Smart Money Concepts (SMC) analysis of a chosen stock.
"""
)

#inputs
symbol = st.text_input("Stock Symbol", "AAPL").upper()

num_points = st.slider(
    "Number of recent 60-minute candles to analyze:",
    10, 80, 24
)

style = st.selectbox(
    "Choose SMC Report Style",
    [
        "Beginner-friendly explanation",
        "Trader-style breakdown",
        "Concise professional summary",
    ]
)

show_data = st.checkbox("Show OHLC data", value=True)

st.markdown("---")

# control button so it doesnt overwork the APIs
if st.button("🔍 Generate SMC Analysis"):
    with st.spinner("Analyzing price action using Smart Money Concepts..."):
        df = fetch_stock_data(symbol, num_points)

        if df is None:
            st.error("⚠️ Error fetching data. Check symbol or API rate limit.")
        else:
            summary = summarize(df, num_points)

            if show_data:
                st.subheader("📈 Recent OHLC Data")
                st.dataframe(df)

            #number summary
            st.subheader("📌 Price Action Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Start Close", f"${summary['start']:.2f}")
                st.metric("End Close", f"${summary['end']:.2f}")
            with col2:
                st.metric("Change", f"${summary['change']:.2f}")
                st.metric("Percent Change", f"{summary['pct']:.2f}%")
            with col3:
                st.metric("High", f"${summary['high']:.2f}")
                st.metric("Low", f"${summary['low']:.2f}")
                st.metric("Avg Volume", f"{summary['vol']:,}")

            #gemini output
            try:
                st.subheader("🤖 Gemini SMC Report")
                report = generate_smc_report(symbol, summary, style)
                st.write(report)
            except Exception as e:
                st.error("Gemini API Error — try again.")
                st.caption(str(e))

