import pandas as pd
from datetime import datetime
import io

def validate_csv_format(df):
    """
    Validate that the uploaded CSV has the required columns and formats.
    
    Args:
        df (pandas.DataFrame): DataFrame to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_columns = ['ticker', 'date', 'transaction_type', 'quantity', 'price']
    
    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check if transaction_type is either 'BUY' or 'SELL'
    invalid_types = df[~df['transaction_type'].isin(['BUY', 'SELL'])]['transaction_type'].unique()
    if len(invalid_types) > 0:
        return False, f"Invalid transaction types: {', '.join(invalid_types)}. Must be 'BUY' or 'SELL'."
    
    # Check if quantity and price are numeric
    try:
        df['quantity'] = pd.to_numeric(df['quantity'])
        df['price'] = pd.to_numeric(df['price'])
    except ValueError:
        return False, "Quantity and price must be numeric values."
    
    # Check if date is in the correct format
    try:
        df['date'] = pd.to_datetime(df['date'])
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."
    
    # Check for non-positive values in quantity or price
    if (df['quantity'] <= 0).any():
        return False, "Quantity must be a positive number."
    if (df['price'] <= 0).any():
        return False, "Price must be a positive number."
    
    return True, ""

def get_sample_csv():
    """
    Generate a sample CSV file for the user to download.
    
    Returns:
        str: Sample CSV content
    """
    sample_data = [
        {'ticker': 'AAPL', 'date': '2022-01-15', 'transaction_type': 'BUY', 'quantity': 10, 'price': 150.75},
        {'ticker': 'MSFT', 'date': '2022-02-20', 'transaction_type': 'BUY', 'quantity': 5, 'price': 280.25},
        {'ticker': 'AAPL', 'date': '2022-06-10', 'transaction_type': 'SELL', 'quantity': 3, 'price': 175.50}
    ]
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False).encode('utf-8')

def process_uploaded_csv(uploaded_file):
    """
    Process the uploaded CSV file into a DataFrame.
    
    Args:
        uploaded_file: The uploaded file object from Streamlit
        
    Returns:
        tuple: (success, result)
            If success is True, result is the processed DataFrame
            If success is False, result is an error message
    """
    try:
        df = pd.read_csv(uploaded_file)
        is_valid, error_message = validate_csv_format(df)
        
        if not is_valid:
            return False, error_message
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure correct types
        df['quantity'] = df['quantity'].astype(float)
        df['price'] = df['price'].astype(float)
        df['ticker'] = df['ticker'].str.upper()
        
        # Sort by date (oldest first)
        df = df.sort_values('date')
        
        return True, df
    
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"

def add_transaction(transactions_df, ticker, date, transaction_type, quantity, price):
    """
    Add a new transaction to the existing transactions DataFrame.
    
    Args:
        transactions_df (pandas.DataFrame): Existing transactions
        ticker (str): Stock ticker symbol
        date (datetime): Transaction date
        transaction_type (str): 'BUY' or 'SELL'
        quantity (float): Number of shares
        price (float): Price per share
        
    Returns:
        pandas.DataFrame: Updated transactions DataFrame
    """
    new_transaction = pd.DataFrame({
        'ticker': [ticker.upper()],
        'date': [date],
        'transaction_type': [transaction_type],
        'quantity': [float(quantity)],
        'price': [float(price)]
    })
    
    if transactions_df is None:
        return new_transaction
    
    updated_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
    return updated_df.sort_values('date').reset_index(drop=True)

def get_unique_tickers(transactions_df):
    """
    Get a list of unique ticker symbols from the transactions DataFrame.
    
    Args:
        transactions_df (pandas.DataFrame): Transactions DataFrame
        
    Returns:
        list: List of unique ticker symbols
    """
    if transactions_df is None or len(transactions_df) == 0:
        return []
    
    return transactions_df['ticker'].unique().tolist()