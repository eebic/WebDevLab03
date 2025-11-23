import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai
import yfinance as yf
from datetime import datetime, timedelta

# takes the api keys
#genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
#gemini_model = genai.GenerativeModel("models/gemini-flash-latest")

#ALPHA_API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
#FUNCTION_DAILY = "TIME_SERIES_DAILY"
#INTERVAL = "60min" 

# -----------------------------
# CONFIGURE GEMINI
# -----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("models/gemini-flash-latest")

# -----------------------------
# APP TITLE
# -----------------------------
st.title("📈 Stock Advisor Chatbot")
st.write("Ask questions, analyze price action, and receive buy/sell strategy suggestions.")


# -----------------------------
# SIDEBAR INPUTS
# -----------------------------
st.sidebar.header("Stock Selection")

ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, NVDA, TSLA):", "AAPL")

days = st.sidebar.slider("How many days of price history?", 30, 720, 180)

fetch_data = st.sidebar.button("Load Stock Data")


# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stock_data" not in st.session_state:
    st.session_state.stock_data = None


# -----------------------------
# FETCH PRICE DATA
# -----------------------------
if fetch_data:
    try:
        end = datetime.today()
        start = end - timedelta(days=days)

        data = yf.download(ticker, start=start, end=end)

        if data.empty:
            st.error("❌ Could not retrieve data for that ticker.")
        else:
            st.session_state.stock_data = data
            st.success(f"Loaded {len(data)} days of price data for {ticker}.")
            st.line_chart(data['Close'])

    except Exception as e:
        st.error(f"Error fetching stock data: {e}")


# -----------------------------
# DISPLAY CHAT MESSAGES
# -----------------------------
st.subheader("💬 Chat with the Stock Advisor")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -----------------------------
# USER CHAT INPUT
# -----------------------------
user_input = st.chat_input("Ask something about the stock...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Build system context with stock data
    stock_summary = "No stock data loaded."

    if st.session_state.stock_data is not None:
        last_close = round(st.session_state.stock_data["Close"].iloc[-1], 2)
        price_change = round(st.session_state.stock_data["Close"].pct_change().iloc[-1] * 100, 2)
        high_52 = round(st.session_state.stock_data["High"].max(), 2)
        low_52 = round(st.session_state.stock_data["Low"].min(), 2)

        stock_summary = (
            f"Current price: ${last_close}. "
            f"Daily change: {price_change}%. "
            f"52-week range: ${low_52} – ${high_52}. "
            f"Recent trend: {st.session_state.stock_data['Close'].tail(7).tolist()}."
        )

    # Prepare full prompt for Gemini
    prompt = f"""
    You are a real-time stock advisor chatbot.

    Here is the latest price action for {ticker}:
    {stock_summary}

    Based on the user's question, analyze the market behavior and give actionable insights.
    Use technical logic such as momentum, trend direction, support, and resistance.
    DO NOT give financial advice disclaimers. Focus on data-driven guidance.

    User question:
    {user_input}
    """

    # -----------------------------
    # LLM CALL WITH ERROR HANDLING
    # -----------------------------
    try:
        response = model.generate_content(prompt)
        bot_msg = response.text

    except Exception as e:
        bot_msg = f"⚠️ I hit an error while generating the response: `{e}`. Please try again."

    # Save & display assistant message
    st.session_state.messages.append({"role": "assistant", "content": bot_msg})

    with st.chat_message("assistant"):
        st.write(bot_msg)
