import streamlit as st
import pandas as pd

from components.input_transactions import render_input_transactions
from components.view_portfolio import render_view_portfolio
from components.portfolio_performance import render_portfolio_performance

# Configure the app
st.set_page_config(
    page_title="Stock Portfolio Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """
    Main function to run the Streamlit app.
    """
    # Add header with app title
    st.title("📈 Stock Portfolio Tracker")
    
    # Create tabs for the main sections
    tabs = st.tabs([
        "Input Transactions", 
        "View Portfolio", 
        "Portfolio Performance"
    ])
    
    # Render each tab's content
    with tabs[0]:
        render_input_transactions()
        
    with tabs[1]:
        render_view_portfolio()
        
    with tabs[2]:
        render_portfolio_performance()
    
    # Add footer
    st.markdown("---")
    st.caption("Stock Portfolio Tracker using Streamlit and yfinance")

if __name__ == "__main__":
    main()