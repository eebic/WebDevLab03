# https://webdevlab03-team15.streamlit.app/
# API Key (Alpha Vantage): 2GLDYP292HNQFQUP

import streamlit as st

st.set_page_config(
    page_title="MONEY MOVES: Stock Data Explorer",
    page_icon="💸",
    layout="wide" 
)

# header section
with st.container():
    left, spacer, right = st.columns([1, 0.05, 1])

    with left:
        st.image("Images/intro_pic.jpg", use_container_width=True)

    with right:
        st.markdown("""
            <style>
                .custom-title {
                    color: #00A36C !important;
                    font-size: 3rem !important;
                    font-weight: 700 !important;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 class='custom-title'>MONEY MOVES</h1>", unsafe_allow_html=True)
        st.subheader("Stock Data Explorer")
        st.write("**CS 1301 — Team 15, Section D**")
        st.write("Team Members: **Kaiya Evans** & **Jenna Tran**")

st.markdown("---")

# introduction section
with st.container():
    st.markdown("<h3><u>Welcome! 👋</u></h3>", unsafe_allow_html=True)
    st.write(
        """
        Welcome to our Streamlit Web Development Lab03 app!  
        Use the sidebar on the left to navigate between pages and explore real stock data,
        analysis tools, and personalized insights.
        """
    )

st.markdown("")

# overview of pages section
with st.container():
    st.markdown("<h3><u>App Pages Overview</u></h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 1️⃣ Home Page  
            Introduces the project, its purpose, and how to navigate the app.
            
            ### 3️⃣ Stock Analysis  
            Analyzes ticker price action and trends to identify Smart Money Concepts' patterns.
            """
        )

    with col2:
        st.markdown(
            """
            ### 2️⃣ Stock Market Dashboard  
            Displays real-time market data and interactive visualizations  
            of selected stocks.
            
            ### 4️⃣ Personal Stock Advisory  
            Offers personalized insights and portfolio suggestions based  
            on user preferences and data.
            """
        )

st.markmarkdown = ("")
