import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_portfolio_allocation_chart(holdings_df):
    """
    Create a pie chart of portfolio allocation.
    
    Args:
        holdings_df (pandas.DataFrame): DataFrame with current holdings and values
        
    Returns:
        plotly.graph_objects.Figure: Plotly pie chart figure
    """
    if holdings_df.empty or 'current_value' not in holdings_df.columns:
        # Return an empty chart with a message
        fig = go.Figure(go.Pie(
            labels=['No Data'],
            values=[1],
            textinfo='label'
        ))
        fig.update_layout(
            title="Portfolio Allocation (No Data Available)",
            height=400
        )
        return fig
    
    # Create pie chart
    fig = px.pie(
        holdings_df,
        values='current_value',
        names='ticker',
        title='Portfolio Allocation',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    # Add percentage labels
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextorientation='radial'
    )
    
    # Update layout
    fig.update_layout(
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_historical_value_chart(holdings_history):
    """
    Create a line chart showing the historical value of the portfolio.
    
    Args:
        holdings_history (pandas.DataFrame): DataFrame with dates and portfolio values
        
    Returns:
        plotly.graph_objects.Figure: Plotly line chart figure
    """
    if holdings_history.empty:
        # Return an empty chart with a message
        fig = go.Figure()
        fig.update_layout(
            title="Portfolio Value Over Time (No Data Available)",
            xaxis_title="Date",
            yaxis_title="Value ($)",
            height=400
        )
        return fig
    
    # Create line chart
    fig = px.line(
        holdings_history,
        x=holdings_history.index,
        y='total_value',
        title='Portfolio Value Over Time',
        labels={'total_value': 'Portfolio Value ($)', 'index': 'Date'}
    )
    
    # Add markers for specific points
    fig.update_traces(mode='lines+markers', marker=dict(size=5))
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickprefix='$'
        )
    )
    
    return fig

def format_currency(value):
    """
    Format a number as a currency string.
    
    Args:
        value (float): Number to format
        
    Returns:
        str: Formatted currency string
    """
    return f"${value:,.2f}"

def format_percentage(value):
    """
    Format a number as a percentage string.
    
    Args:
        value (float): Number to format
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value:.2f}%"