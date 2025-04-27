import streamlit as st
import pandas as pd
import numpy as np

from utils.portfolio import (
    calculate_holdings_fifo, 
    get_current_prices, 
    calculate_portfolio_value, 
    calculate_portfolio_metrics
)
from utils.visualization import format_currency, format_percentage

def render_portfolio_performance():
    """
    Render the Portfolio Performance tab UI.
    """
    st.header("Portfolio Performance")
    
    # Check if transactions exist
    if 'transactions' not in st.session_state or st.session_state.transactions is None or st.session_state.transactions.empty:
        st.info("No transactions found. Please add transactions in the 'Input Transactions' tab.")
        return
    
    # Calculate current holdings using FIFO method
    holdings_df = calculate_holdings_fifo(st.session_state.transactions)
    
    # Get tickers and fetch current prices (if there are current holdings)
    current_prices = {}
    holdings_with_value = pd.DataFrame()
    
    if not holdings_df.empty:
        tickers = holdings_df['ticker'].tolist()
        
        with st.spinner("Fetching current stock prices..."):
            current_prices = get_current_prices(tickers)
        
        # Calculate portfolio value
        holdings_with_value = calculate_portfolio_value(holdings_df, current_prices)
    
    # Calculate portfolio metrics
    metrics = calculate_portfolio_metrics(st.session_state.transactions, holdings_with_value)
    
    # Display metric cards
    st.subheader("Performance Metrics")
    
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Investment", format_currency(metrics['total_investment']))
        
    with col2:
        st.metric("Total Realized Value (Sells)", format_currency(metrics['total_sells']))
        
    with col3:
        st.metric("Current Portfolio Value", format_currency(metrics['current_value']))
    
    # Create two columns for return metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Add delta formatting for total return
        delta_sign = "+" if metrics['total_return'] >= 0 else ""
        delta_value = f"{delta_sign}{format_currency(metrics['total_return'])}"
        
        st.metric(
            "Total Return", 
            format_currency(metrics['total_return']),
            delta=format_percentage(metrics['total_return_percent'])
        )
        
    with col2:
        # Display XIRR
        if metrics['xirr'] is not None:
            st.metric("XIRR (Annualized Return)", format_percentage(metrics['xirr']))
        else:
            st.metric("XIRR (Annualized Return)", "Not available")
    
    # Display transactions summary
    st.subheader("Transaction Summary")
    
    # Group transactions by type
    if not st.session_state.transactions.empty:
        buys = st.session_state.transactions[st.session_state.transactions['transaction_type'] == 'BUY']
        sells = st.session_state.transactions[st.session_state.transactions['transaction_type'] == 'SELL']
        
        total_buy_transactions = len(buys)
        total_sell_transactions = len(sells)
        
        # Create transaction summary
        summary_data = {
            'Metric': ['Total Buy Transactions', 'Total Sell Transactions', 'Average Buy Price', 'Average Sell Price'],
            'Value': [
                total_buy_transactions,
                total_sell_transactions,
                format_currency(buys['price'].mean()) if not buys.empty else "$0.00",
                format_currency(sells['price'].mean()) if not sells.empty else "$0.00"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Display buy/sell history by ticker
    if not st.session_state.transactions.empty:
        st.subheader("Transaction History by Ticker")
        
        # Group transactions by ticker and type
        ticker_summary = []
        
        for ticker in st.session_state.transactions['ticker'].unique():
            ticker_transactions = st.session_state.transactions[st.session_state.transactions['ticker'] == ticker]
            ticker_buys = ticker_transactions[ticker_transactions['transaction_type'] == 'BUY']
            ticker_sells = ticker_transactions[ticker_transactions['transaction_type'] == 'SELL']
            
            buy_quantity = ticker_buys['quantity'].sum() if not ticker_buys.empty else 0
            buy_value = (ticker_buys['quantity'] * ticker_buys['price']).sum() if not ticker_buys.empty else 0
            
            sell_quantity = ticker_sells['quantity'].sum() if not ticker_sells.empty else 0
            sell_value = (ticker_sells['quantity'] * ticker_sells['price']).sum() if not ticker_sells.empty else 0
            
            # Calculate realized P/L for completed trades
            realized_pl = sell_value - (buy_value * (sell_quantity / buy_quantity)) if buy_quantity > 0 else 0
            
            ticker_summary.append({
                'Ticker': ticker,
                'Buy Quantity': buy_quantity,
                'Buy Value': buy_value,
                'Sell Quantity': sell_quantity,
                'Sell Value': sell_value,
                'Realized P/L': realized_pl
            })
        
        ticker_summary_df = pd.DataFrame(ticker_summary)
        
        # Format and display the ticker summary
        if not ticker_summary_df.empty:
            st.dataframe(
                ticker_summary_df,
                column_config={
                    "Ticker": st.column_config.TextColumn("Ticker"),
                    "Buy Quantity": st.column_config.NumberColumn("Buy Quantity", format="%.2f"),
                    "Buy Value": st.column_config.NumberColumn("Buy Value", format="$%.2f"),
                    "Sell Quantity": st.column_config.NumberColumn("Sell Quantity", format="%.2f"),
                    "Sell Value": st.column_config.NumberColumn("Sell Value", format="$%.2f"),
                    "Realized P/L": st.column_config.NumberColumn("Realized P/L", format="$%.2f"),
                },
                use_container_width=True,
                hide_index=True
            )