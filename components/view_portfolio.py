import streamlit as st
import pandas as pd
import time

from utils.data_processing import get_unique_tickers
from utils.portfolio import calculate_holdings_fifo, get_current_prices, calculate_portfolio_value
from utils.visualization import create_portfolio_allocation_chart, format_currency, format_percentage

def render_view_portfolio():
    """
    Render the View Portfolio tab UI.
    """
    st.header("Portfolio Overview")
    
    # Check if transactions exist
    if 'transactions' not in st.session_state or st.session_state.transactions is None or st.session_state.transactions.empty:
        st.info("No transactions found. Please add transactions in the 'Input Transactions' tab.")
        return
    
    # Calculate current holdings using FIFO method
    holdings_df = calculate_holdings_fifo(st.session_state.transactions)
    
    # If no holdings, show message
    if holdings_df.empty:
        st.info("No current holdings found. You may have sold all positions.")
        return
    
    # Get tickers and fetch current prices
    tickers = holdings_df['ticker'].tolist()
    
    with st.spinner("Fetching current stock prices..."):
        current_prices = get_current_prices(tickers)
    
    # Handle case where prices couldn't be fetched
    if not current_prices:
        st.error("Could not fetch current prices. Please check your internet connection and try again.")
        return
    
    # Calculate portfolio value and metrics
    holdings_with_value = calculate_portfolio_value(holdings_df, current_prices)
    
    # Check if value calculation was successful
    if holdings_with_value.empty or 'current_value' not in holdings_with_value.columns:
        st.error("Could not calculate portfolio value. Please try again.")
        return
    
    # Display total portfolio value
    total_value = holdings_with_value['current_value'].sum()
    st.metric("Total Portfolio Value", format_currency(total_value))
    
    # Create columns for layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Display holdings table
        st.subheader("Current Holdings")
        
        # Format the dataframe for display
        display_df = holdings_with_value.copy()
        display_df['ticker'] = display_df['ticker'].astype(str)
        display_df['quantity'] = display_df['quantity'].round(4)
        display_df['avg_cost_basis'] = display_df['avg_cost_basis'].round(2)
        display_df['current_price'] = display_df['current_price'].round(2)
        display_df['current_value'] = display_df['current_value'].round(2)
        display_df['unrealized_pl'] = display_df['unrealized_pl'].round(2)
        display_df['unrealized_pl_percent'] = display_df['unrealized_pl_percent'].round(2)
        
        # Show the dataframe with formatted columns
        st.dataframe(
            display_df,
            column_config={
                "ticker": st.column_config.TextColumn("Ticker"),
                "quantity": st.column_config.NumberColumn("Quantity", format="%.4f"),
                "avg_cost_basis": st.column_config.NumberColumn("Avg Cost Basis", format="$%.2f"),
                "current_price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                "current_value": st.column_config.NumberColumn("Current Value", format="$%.2f"),
                "unrealized_pl": st.column_config.NumberColumn("Unrealized P/L ($)", format="$%.2f"),
                "unrealized_pl_percent": st.column_config.NumberColumn("Unrealized P/L (%)", format="%.2f%%"),
            },
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        # Display allocation chart
        st.subheader("Portfolio Allocation")
        allocation_chart = create_portfolio_allocation_chart(holdings_with_value)
        st.plotly_chart(allocation_chart, use_container_width=True)
    
    # Add a refresh button
    if st.button("Refresh Prices"):
        st.rerun()