import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

# gets API keys
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("models/gemini-flash-latest")

ALPHA_API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
FUNCTION_DAILY = "TIME_SERIES_DAILY"


# fetches daily stock data
def fetch_daily_data(symbol: str, days: int = 30):
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

    return df.sort_index().tail(days)


# summary for ease of visualizations and data use
def summarize_daily(df):
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


# gemini LLM advisory response
def gemini_advice(symbol, summary, risk_profile, horizon, question, chat_history):
    # starts conversation memory text
    history_text = ""
    for turn in chat_history[-6:]:
        if turn["role"] == "user":
            history_text += f"User: {turn['content']}\n"
        else:
            history_text += f"Assistant: {turn['content']}\n"
          
    prompt = (
        "You are a friendly stock education assistant named MoneyMovesBot.\n"
        "You help beginner investors understand risk, trends, and general ideas.\n"
        "You are NOT a licensed financial advisor and must NOT give direct trading commands.\n"
        "Always include a short disclaimer such as 'This is not financial advice.'\n\n"

        f"User profile:\n"
        f"- Ticker: {symbol}\n"
        f"- Risk profile: {risk_profile}\n"
        f"- Time horizon: {horizon}\n\n"

        "Recent daily performance:\n"
        f"- Starting close: ${summary['start']:.2f}\n"
        f"- Most recent close: ${summary['end']:.2f}\n"
        f"- Net change: ${summary['chg']:.2f} ({summary['pct']:.2f}%)\n"
        f"- High: ${summary['hi']:.2f}\n"
        f"- Low: ${summary['lo']:.2f}\n"
        f"- Average daily volume: {summary['avg_vol']:,}\n"
        f"- Number of days analyzed: {summary['days']}\n\n"

        "Conversation so far:\n"
        f"{history_text}\n\n"

        "The user asks:\n"
        f"\"{question}\"\n\n"

        "Your response should:\n"
        "- Explain what the price action MAY suggest in simple terms.\n"
        "- Consider the user's risk profile and time horizon.\n"
        "- Give 3–5 bullet points of things they could think about or research.\n"
        "- Stay educational and supportive.\n"
        "- Avoid explicit buy/sell/hold instructions.\n"
        "- End with a short disclaimer.\n"
    )

    response = gemini_model.generate_content(prompt)
    return response.text


# page UI
st.title("💬 Money Moves: Personal Stock Advisor")

st.write(
    """
Chat with an AI **stock education assistant** powered by  
real market data from **Alpha Vantage** and **Google Gemini**.

⚠️ This tool is for learning only — it does **not** provide personalized financial advice.
"""
)

# stock advisor settings
st.markdown("### 📝 Advisor Settings")

symbol = st.text_input("Stock symbol", "AAPL").upper()

risk_profile = st.selectbox(
    "Your risk profile:",
    ["Conservative", "Moderate", "Aggressive"],
)

horizon = st.selectbox(
    "Your time horizon:",
    ["Short-term (0–6 months)", "Medium-term (6–24 months)", "Long-term (2+ years)"],
)

days_window = st.slider(
    "How many recent trading days should the advisor consider?",
    min_value=10,
    max_value=120,
    value=30,
)

st.markdown("---")

# conversation history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("🧠 Conversation")

if not st.session_state.chat_history:
    st.caption("Ask a question about your stock to begin!")
else:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Advisor:** {msg['content']}")

# -------- NEW: Question History section (minimal change) --------
st.markdown("---")
st.subheader("📜 Question History")

user_questions = [m["content"] for m in st.session_state.chat_history if m["role"] == "user"]

if not user_questions:
    st.caption("No questions asked yet.")
else:
    for i, q in enumerate(reversed(user_questions), start=1):
        st.markdown(f"**{i}.** {q}")

st.markdown("---")
# ---------------------------------------------------------------

# user input
user_msg = st.text_input("Ask your question:")
send_clicked = st.button("Send")

if send_clicked and user_msg.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    df = fetch_daily_data(symbol, days_window)

    if df is None:
        assistant_reply = (
            "I couldn't fetch data for that ticker. "
            "Try a different symbol or wait for Alpha Vantage to reset."
        )
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    else:
        summary = summarize_daily(df)

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
                "Hmm, I'm having trouble contacting the Gemini API right now. "
                "Please try again in a moment."
            )
            st.error(f"Gemini error: {e}")

        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    st.rerun()

