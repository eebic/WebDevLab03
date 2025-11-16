# put in "Secrets" of streamlit page for webdevlab03-team15

import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

# ----------------------------------------
# Configure Gemini (v1beta compatible)
# ----------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ✔ Absolutely required: ONLY model available in v1beta
gemini_model = genai.GenerativeModel("models/gemini-pro")

ALPHA_API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
FUNCTION = "TIME_SERIES_INTRADAY"
INTERVAL = "60min"


# ----------------------------------------
# Fetch Alpha Vantage Data
# ----------------------------------------
def fetch_stock_data(symbol: str, num_points: int):
    url = (
        f"https://www.alphavantage.co/query?"
        f"function={FUNCTION}&symbol={symbol}&interval={INTERVAL}&apikey={ALPHA_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "Time Series (60min)" not in data:
        return None

    ts = data["Time Series (60min)"]
    df = pd.DataFrame(ts).T
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    return df.sort_index().tail(num_points)


# ----------------------------------------
# Summaries for Gemini
# ----------------------------------------
def summarize(df, n):
    start = df["close"].iloc[0]
    end = df["close"].iloc[-1]
    chg = round(end - start, 2)
    pct = round((chg / start) * 100, 2)
    hi = df["high"].max()
    lo = df["low"].min()
    vol = int(df["volume"].mean())

    return {
        "n": n,
        "start": start,
        "end": end,
        "chg": chg,
        "pct": pct,
        "hi": hi,
        "lo": lo,
        "vol": vol,
    }


# ----------------------------------------
# Gemini SMC Analyzer
# ----------------------------------------
def generate_smc(symbol: str, summary: dict, style: str):
    prompt = f"""
You are an expert Smart Money Concepts (SMC) trader.

Analyze recent price action for {symbol} using ONLY the data below:

• Last {summary['n']} 60-minute candles  
• Starting close: ${summary['start']:.2f}  
• Ending close: ${summary['end']:.2f}  
• Change: ${summary['chg']:.2f} ({summary['pct']:.2f}%)  
• High: ${summary['hi']:.2f}  
• Low: ${summary['lo']:.2f}  
• Average volume: {summary['vol']}

Discuss SMC ideas like:
- Market Structure (HH/HL vs LH/LL)
- Liquidity grabs
- Premium/discount zones
- Accumulation or distribution
- Smart Money manipulation
- Bias (bullish/bearish/range)

Write a {style} SMC report.
"""

    response = gemini_model.generate_content(prompt)
    return response.text


# ----------------------------------------
# Streamlit UI
# ----------------------------------------
st.title("📊 Smart Money Concepts — AI Stock Analysis (Phase 3)")

symbol = st.text_input("Stock Symbol", "AAPL").upper()
num_points = st.slider("Number of recent candles", 10, 80, 24)
style = st.selectbox(
    "Choose analysis style",
    ["Beginner-friendly explanation", "Trader breakdown", "Professional summary"],
)
show_data = st.checkbox("Show OHLC Data", True)

if st.button("Generate Analysis"):
    df = fetch_stock_data(symbol, num_points)

    if df is None:
        st.error("Error fetching data. Check symbol or API rate limit.")
    else:
        summary = summarize(df, num_points)

        if show_data:
            st.subheader("📈 OHLC Data")
            st.dataframe(df)

        st.subheader("📌 Price Summary")
        st.write(summary)

        try:
            st.subheader("🤖 Gemini SMC Report")
            st.write(generate_smc(symbol, summary, style))
        except Exception as e:
            st.error("Gemini API Error — try again.")
            st.caption(str(e))
