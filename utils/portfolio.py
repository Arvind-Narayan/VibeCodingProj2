import pandas as pd
import numpy as np
import numpy_financial as npf
import yfinance as yf
from datetime import datetime
import streamlit as st
from scipy import optimize

def get_current_prices(tickers):
    """
    Get the current prices for a list of ticker symbols.
    
    Args:
        tickers (list): List of ticker symbols
        
    Returns:
        dict: Dictionary mapping ticker symbols to current prices
    """
    prices = {}
    if not tickers:
        return prices
    
    try:
        data = yf.download(tickers, period="1d")['Close']
        
        # If only one ticker is provided, data will be a Series
        if isinstance(data, pd.Series):
            prices[tickers[0]] = data.iloc[-1]
        else:
            # Multiple tickers will result in a DataFrame
            latest_prices = data.iloc[-1]
            for ticker in tickers:
                if ticker in latest_prices:
                    prices[ticker] = latest_prices[ticker]
    except Exception as e:
        print(f"Error fetching prices: {e}")
    
    return prices

def calculate_holdings_fifo(transactions_df):
    """
    Calculate current holdings and cost basis using the FIFO method.
    
    Args:
        transactions_df (pandas.DataFrame): DataFrame of transactions
        
    Returns:
        pandas.DataFrame: DataFrame with current holdings and cost basis
    """
    if transactions_df is None or len(transactions_df) == 0:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    df = transactions_df.copy()
    
    # Sort by date (oldest first)
    df = df.sort_values('date')
    
    # Initialize an empty dictionary to track lots for each ticker
    # Each lot is a tuple of (quantity, price)
    lots = {}
    
    # Process each transaction
    for _, row in df.iterrows():
        ticker = row['ticker']
        transaction_type = row['transaction_type']
        quantity = row['quantity']
        price = row['price']
        
        if ticker not in lots:
            lots[ticker] = []
        
        if transaction_type == 'BUY':
            # Add new lot
            lots[ticker].append((quantity, price))
        
        elif transaction_type == 'SELL':
            remaining_quantity = quantity
            
            # Sell from oldest lots first (FIFO)
            while remaining_quantity > 0 and lots[ticker]:
                lot_quantity, lot_price = lots[ticker][0]
                
                if lot_quantity <= remaining_quantity:
                    # Remove entire lot
                    lots[ticker].pop(0)
                    remaining_quantity -= lot_quantity
                else:
                    # Reduce lot quantity
                    lots[ticker][0] = (lot_quantity - remaining_quantity, lot_price)
                    remaining_quantity = 0
    
    # Create holdings DataFrame
    holdings = []
    
    for ticker, ticker_lots in lots.items():
        total_quantity = sum(qty for qty, _ in ticker_lots)
        
        if total_quantity > 0:
            # Calculate average cost basis
            total_cost = sum(qty * price for qty, price in ticker_lots)
            avg_cost_basis = total_cost / total_quantity
            
            holdings.append({
                'ticker': ticker,
                'quantity': total_quantity,
                'avg_cost_basis': avg_cost_basis
            })
    
    return pd.DataFrame(holdings)

def calculate_portfolio_value(holdings_df, prices_dict):
    """
    Calculate current value and performance metrics for the portfolio.
    
    Args:
        holdings_df (pandas.DataFrame): Holdings DataFrame
        prices_dict (dict): Dictionary of current prices
        
    Returns:
        pandas.DataFrame: Enhanced holdings DataFrame with value and performance metrics
    """
    if holdings_df.empty:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    df = holdings_df.copy()
    
    # Add current price column
    df['current_price'] = df['ticker'].map(prices_dict)
    
    # Calculate current value and profit/loss
    df['current_value'] = df['quantity'] * df['current_price']
    df['unrealized_pl'] = df['current_value'] - (df['quantity'] * df['avg_cost_basis'])
    df['unrealized_pl_percent'] = (df['unrealized_pl'] / (df['quantity'] * df['avg_cost_basis'])) * 100
    
    return df

def calculate_portfolio_metrics(transactions_df, holdings_df):
    """
    Calculate overall portfolio performance metrics.
    
    Args:
        transactions_df (pandas.DataFrame): DataFrame of transactions
        holdings_df (pandas.DataFrame): DataFrame of current holdings with values
        
    Returns:
        dict: Dictionary of portfolio metrics
    """
    metrics = {
        'total_investment': 0,
        'total_sells': 0,
        'current_value': 0,
        'total_return': 0,
        'total_return_percent': 0,
        'xirr': None
    }
    
    if transactions_df is None or holdings_df is None:
        return metrics
    
    # Calculate total investment (sum of buy transactions)
    if not transactions_df.empty:
        buys = transactions_df[transactions_df['transaction_type'] == 'BUY']
        metrics['total_investment'] = (buys['quantity'] * buys['price']).sum()
        
        # Calculate total sells (sum of sell transactions)
        sells = transactions_df[transactions_df['transaction_type'] == 'SELL']
        metrics['total_sells'] = (sells['quantity'] * sells['price']).sum()
    
    # Calculate current portfolio value
    if not holdings_df.empty:
        metrics['current_value'] = holdings_df['current_value'].sum()
    
    # Calculate total return
    metrics['total_return'] = metrics['total_sells'] + metrics['current_value'] - metrics['total_investment']
    
    # Calculate total return percentage
    if metrics['total_investment'] > 0:
        metrics['total_return_percent'] = (metrics['total_return'] / metrics['total_investment']) * 100
    
    # Calculate XIRR
    metrics['xirr'] = calculate_xirr(transactions_df, metrics['current_value'])
    
    return metrics

def calculate_xirr(transactions_df, current_value):
    """
    Calculate the Extended Internal Rate of Return (XIRR) for the portfolio
    using scipy's optimization function.
    
    Args:
        transactions_df (pandas.DataFrame): DataFrame of transactions
        current_value (float): Current portfolio value
        
    Returns:
        float: XIRR value as a percentage, or None if calculation fails
    """
    if transactions_df is None or len(transactions_df) == 0:
        st.write("XIRR calculation: No transactions found")
        return None
    
    # Create cash flows from transactions
    cash_flows = []
    dates = []
    
    for _, row in transactions_df.iterrows():
        amount = row['quantity'] * row['price']
        
        if row['transaction_type'] == 'BUY':
            cash_flows.append(-amount)  # Negative for buys (money out)
        else:  # SELL
            cash_flows.append(amount)   # Positive for sells (money in)
            
        dates.append(row['date'])
    
    # Add current portfolio value as a cash flow today
    if current_value > 0:
        cash_flows.append(current_value)
        current_date = datetime.now()
        dates.append(current_date)
        st.write(f"XIRR calculation: Added current portfolio value (${current_value:.2f}) as final cash flow")
    
    # Check if we have valid cash flows
    if len(cash_flows) < 2:
        st.write("XIRR calculation: Insufficient cash flows (need at least 2)")
        return None
    
    # Convert dates to days since first date
    min_date = min(dates)
    days = [(date - min_date).days for date in dates]
    
    st.write(f"XIRR calculation: Processing {len(cash_flows)} cash flows from {min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}")
    
    try:
        # Define the XIRR function to minimize
        def xirr_equation(rate):
            result = 0
            for i, cf in enumerate(cash_flows):
                result += cf / (1 + rate) ** (days[i] / 365.0)
            return result
        
        # Use scipy's optimization to find the rate that makes the NPV = 0
        result = optimize.newton(xirr_equation, x0=0.1)
        
        # Convert to percentage and round to 2 decimal places
        xirr_value = result * 100
        
        # Check if result is valid
        if np.isnan(xirr_value) or np.isinf(xirr_value):
            st.write("XIRR calculation: Invalid result (NaN or infinity)")
            return None
        
        st.write(f"XIRR calculation: Successful - {xirr_value:.2f}%")
        return xirr_value
    except Exception as e:
        # Try a different optimization method if newton fails
        try:
            # Use brentq which is more robust but slower
            result = optimize.brentq(xirr_equation, -0.999, 10)
            xirr_value = result * 100
            
            if np.isnan(xirr_value) or np.isinf(xirr_value):
                st.write("XIRR calculation: Invalid result (NaN or infinity)")
                return None
            
            st.write(f"XIRR calculation: Successful (alternate method) - {xirr_value:.2f}%")
            return xirr_value
        except Exception as e2:
            # Handle errors
            st.write(f"XIRR calculation: Error - {str(e2)}")
            print(f"Error calculating XIRR: {e2}")
            return None

def get_historical_data(tickers, start_date=None, end_date=None):
    """
    Get historical stock data for the given tickers.
    
    Args:
        tickers (list): List of ticker symbols
        start_date (str, optional): Start date in 'YYYY-MM-DD' format
        end_date (str, optional): End date in 'YYYY-MM-DD' format
        
    Returns:
        pandas.DataFrame: DataFrame with historical price data
    """
    if not tickers:
        return pd.DataFrame()
    
    try:
        data = yf.download(tickers, start=start_date, end=end_date)['Close']
        return data
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return pd.DataFrame()