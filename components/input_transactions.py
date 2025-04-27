import streamlit as st
import pandas as pd
from datetime import datetime
import io

from utils.data_processing import (
    validate_csv_format,
    get_sample_csv,
    process_uploaded_csv,
    add_transaction
)

def render_input_transactions():
    """
    Render the Input Transactions tab UI.
    """
    st.header("Input Transactions")
    
    # Initialize session state for transactions if it doesn't exist
    if 'transactions' not in st.session_state:
        st.session_state.transactions = None
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["CSV Upload", "Manual Input"])
    
    with tab1:
        render_csv_upload()
    
    with tab2:
        render_manual_input()
    
    # Display current transactions
    if st.session_state.transactions is not None and not st.session_state.transactions.empty:
        st.subheader("Transaction History")
        st.dataframe(
            st.session_state.transactions.sort_values('date', ascending=False),
            use_container_width=True,
            column_config={
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
            }
        )
        
        # Clear transactions button
        if st.button("Clear All Transactions"):
            st.session_state.transactions = None
            st.rerun()

def render_csv_upload():
    """
    Render the CSV upload section.
    """
    st.subheader("Upload Transaction CSV")
    
    # Show sample CSV
    st.write("Your CSV should have the following columns: ticker, date, transaction_type, quantity, price")
    
    # Sample data for display
    sample_data = pd.DataFrame([
        {'ticker': 'AAPL', 'date': '2022-01-15', 'transaction_type': 'BUY', 'quantity': 10, 'price': 150.75},
        {'ticker': 'MSFT', 'date': '2022-02-20', 'transaction_type': 'BUY', 'quantity': 5, 'price': 280.25},
        {'ticker': 'AAPL', 'date': '2022-06-10', 'transaction_type': 'SELL', 'quantity': 3, 'price': 175.50}
    ])
    
    st.write("Sample CSV format:")
    st.dataframe(sample_data, use_container_width=True)
    
    # Download sample CSV button
    csv = get_sample_csv()
    st.download_button(
        label="Download Sample CSV",
        data=csv,
        file_name="sample_transactions.csv",
        mime="text/csv"
    )
    
    # CSV file uploader
    uploaded_file = st.file_uploader("Upload your transaction CSV", type=["csv"])
    
    if uploaded_file is not None:
        success, result = process_uploaded_csv(uploaded_file)
        
        if success:
            # Display the uploaded data
            st.write("Uploaded transactions:")
            st.dataframe(
                result,
                use_container_width=True,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
                }
            )
            
            # Add data to session state
            if st.button("Add to Portfolio"):
                if st.session_state.transactions is None:
                    st.session_state.transactions = result
                else:
                    # Concatenate and drop duplicates
                    combined = pd.concat([st.session_state.transactions, result])
                    # Consider a transaction a duplicate if all fields match
                    st.session_state.transactions = combined.drop_duplicates().reset_index(drop=True)
                
                st.success("Transactions added to portfolio!")
                st.rerun()
        else:
            st.error(f"Error: {result}")

def render_manual_input():
    """
    Render the manual input section.
    """
    st.subheader("Manual Transaction Entry")
    
    # Create form for manual input
    with st.form("transaction_form"):
        # Form inputs
        ticker = st.text_input("Ticker Symbol", value="").upper()
        date = st.date_input("Transaction Date", value=datetime.now())
        transaction_type = st.selectbox("Transaction Type", options=["BUY", "SELL"])
        quantity = st.number_input("Quantity", min_value=0.01, value=1.0, step=0.01)
        price = st.number_input("Price per Share ($)", min_value=0.01, value=100.0, step=0.01)
        
        # Submit button
        submitted = st.form_submit_button("Add Transaction")
        
        if submitted:
            if not ticker:
                st.error("Ticker symbol is required.")
            else:
                # Add transaction to session state
                if st.session_state.transactions is None:
                    st.session_state.transactions = add_transaction(None, ticker, date, transaction_type, quantity, price)
                else:
                    st.session_state.transactions = add_transaction(
                        st.session_state.transactions, ticker, date, transaction_type, quantity, price
                    )
                
                st.success(f"{transaction_type} transaction for {ticker} added successfully!")
                st.rerun()