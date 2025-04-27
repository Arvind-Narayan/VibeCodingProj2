# Stock Portfolio Tracker

A Streamlit web application to track the performance of a US stock portfolio. This application allows users to input their transaction history (buys and sells) and provides visualizations and metrics related to their portfolio's current state and historical performance.

## Features

- Input stock transactions through CSV upload or manual entry
- View current portfolio status with real-time stock prices
- Calculate performance metrics including FIFO cost basis, unrealized P/L
- Visualize portfolio allocation
- Track historical performance with metrics like XIRR

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

The application is organized into three tabs:

1. **Input Transactions**: Upload a CSV or manually enter stock transactions
2. **View Portfolio**: See current portfolio allocation and performance
3. **Portfolio Performance**: Analyze historical performance with advanced metrics

### CSV Format

To upload transactions, use a CSV file with the following headers:
- ticker: Stock symbol (e.g., AAPL)
- date: Transaction date (YYYY-MM-DD)
- transaction_type: 'BUY' or 'SELL'
- quantity: Number of shares
- price: Price per share at time of transaction