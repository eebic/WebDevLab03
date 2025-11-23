import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

# takes the api keys
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("models/gemini-flash-latest")

ALPHA_API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
FUNCTION_DAILY = "TIME_SERIES_DAILY"
INTERVAL = "60min" 


# gathers and summarizes stock data
def fetch_daily_data(symbol: str, days: int = 30):
    """
    Fetch recent daily OHLCV data for a ticker.
    Uses Alpha Vantage TIME_SERIES_DAILY.
    """
    url = (
        f"https://www.alphavantage.co/query?"
        f"function={FUNCTION_DAILY}&symbol={symbol}&apikey={ALPHA_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        return None

    ts = data["Time Series (Daily)"]
    df = pd.DataFrame(ts).T
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().tail(days)
    return df


def summarize_daily(df: pd.DataFrame):
    """
    Build a compact summary dict from daily data.
    """
    start = df["close"].iloc[0]
    end = df["close"].iloc[-1]
    chg = round(end - start, 2)
    pct = round((chg / start) * 100, 2)
    hi = df["high"].max()
    lo = df["low"].min()
    avg_vol = int(df["volume"].mean())

    return {
        "start": start,
        "end": end,
        "chg": chg,
        "pct": pct,
        "hi": hi,
        "lo": lo,
        "avg_vol": avg_vol,
        "days": len(df),
    }


# builds an llm response for the chatbot
def gemini_advice(
    symbol: str,
    summary: dict,
    risk_profile: str,
    horizon: str,
    question: str,
    chat_history,
):
    """
    Call Gemini to generate a conversational answer based on:
    - stock data summary
    - user risk profile + time horizon
    - the ongoing conversation
    """
    # turn the last few turns into text to give the model some "memory" aka stored data
    history_text = ""
    for turn in chat_history[-6:]:
        role = "User" if turn["role"] == "user" else "Assistant"
        history_text += f"{role}: {turn['content']}\n"

    prompt = f"""
You are a friendly stock education assistant named MoneyMovesBot.
You help beginner investors understand risk, trends, and general ideas.
You are NOT a licensed financial advisor and must NOT give direct trading commands.
Always include a short disclaimer like "This is not financial advice."

User profile:
- Ticker: {symbol}
- Risk profile: {risk_profile}
- Time horizon: {horizon}

Recent daily performance for {symbol} (last {summary['days']} trading days):
- Starting close: ${summary['start']:.2f}
- Most recent close: ${summary['end']:.2f}
- Net change: ${summary['chg']:.2f} ({summary['pct']:.2f}%)
- Highest price in this window: ${summary['hi']:.2f}
- Lowest price in this window: ${summary['lo']:.2f}
- Average daily volume: {summary['avg_vol']:,}

Conversation so far:
{history_text}

The user has now asked:
"{question}"

Task:
- Explain what the recent price action might mean in simple terms.
- Relate your explanation to the risk profile and time horizon.
- Offer 3–5 bullet points of things they could *think about* or *research*,
  not explicit buy/sell/hold instructions.
- Keep the tone supportive, clear, and concise.
- End with a brief reminder that this is not personalized financial advice.
"""

    response = gemini_model.generate_content(prompt)
    return response.text



st.title("💬 Money Moves: Personal Stock Advisor (Phase 4)")

st.write(
"""
Chat with an AI **stock education & advisory assistant** powered by  
real market data from **Alpha Vantage** and **Google Gemini**.

> ⚠️ This tool is for learning and general information only.  
> It does **not** provide personalized financial, legal, or investment advice.
"""
)

# --- Sidebar-style controls for the "context" of the advice ---
st.markdown("### 📋 Advisor Settings")

symbol = st.text_input("Stock symbol", "AAPL").upper()

risk_profile = st.selectbox(
    "Your risk profile",
    ["Conservative", "Moderate", "Aggressive"],
)

horizon = st.selectbox(
    "Time horizon",
    ["Short-term (0–6 months)", "Medium-term (6–24 months)", "Long-term (2+ years)"],
)

days_window = st.slider(
    "How many recent trading days should the advisor look at?",
    min_value=10,
    max_value=120,
    value=30,
)

st.markdown("---")

# --- Chat state initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user"/"assistant", "content": str}

# --- Show conversation so far ---
st.subheader("🧠 Conversation")

if not st.session_state.chat_history:
    st.caption("No messages yet. Ask a question about your chosen stock to get started!")
else:
    for turn in st.session_state.chat_history:
        if turn["role"] == "user":
            st.markdown(f"**You:** {turn['content']}")
        else:
            st.markdown(f"**Advisor:** {turn['content']}")

st.markdown("---")

# --- User input for new message ---
user_msg = st.text_input(
    "Ask the advisor a question about this stock (examples: trend, risk, long-term outlook):",
    "",
)

send_clicked = st.button("Send")

if send_clicked and user_msg.strip():
    # Add user's message to history
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    # Fetch and summarize data for the current ticker
    df = fetch_daily_data(symbol, days_window)

    if df is None:
        error_msg = (
            "I couldn't fetch recent data for that symbol. "
            "Try another ticker or wait for the API rate limit to reset."
        )
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    else:
        summary = summarize_daily(df)

        # Try to call Gemini safely
        try:
            reply = gemini_advice(
                symbol=symbol,
                summary=summary,
                risk_profile=risk_profile,
                horizon=horizon,
                question=user_msg,
                chat_history=st.session_state.chat_history,
            )
        except Exception as e:
            reply = (
                "I ran into a problem while contacting the Gemini API. "
                "Please try again in a moment."
            )
            # Optional: surface the actual error in the app for debugging
            st.error(f"Gemini API error: {e}")

        # Add assistant reply to history
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Force a rerun so the new messages show up in the conversation section
    st.experimental_rerun()
