# https://webdevlab03-team15.streamlit.app/
# API Key (Alpha Vantage): 2GLDYP292HNQFQUP

import streamlit as st

st.set_page_config(
    page_title="Money Moves: Stock Data Explorer",
    page_icon="💸",
    layout="wide"
)

# Header part
with st.container():
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.title("Web Development Lab03")
        st.header("💸 Money Moves: Stock Data Explorer")

        st.subheader("CS 1301 • Team 15 • Section D")
        st.write(
            """
            **Team Members**  
            • Kaiya Evans  
            • Jenna Tran  
            """
        )

    with right_col:
        st.image("Images/intro_pic.jpg", use_container_width=True)

st.markdown("---")

# intro
with st.container():
    st.subheader("Welcome! 👋")
    st.write(
        """
        Welcome to our Streamlit Web Development Lab03 app!  
        Use the sidebar on the left to navigate between pages and explore real stock data,
        analysis tools, and personalized insights.
        """
    )

st.markdown("")

# pages overview part
with st.container():
    st.subheader("App Pages Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 1️⃣ Home Page  
            Introduces the project, its purpose, and how to navigate the app.
            
            ### 2️⃣ Stock Market Dashboard  
            Displays real-time market data and interactive visualizations  
            of selected stocks.
            """
        )

    with col2:
        st.markdown(
            """
            ### 3️⃣ Stock Analysis  
            Analyzes historical performance metrics and trends to evaluate  
            investment potential.
            
            ### 4️⃣ Personal Stock Advisory  
            Offers personalized insights and portfolio suggestions based  
