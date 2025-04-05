# app.py
import streamlit as st
from market_data import get_market_data
from analysis import calculate_all_indicators
from recommendation import generate_recommendation
from risk_management import risk_management

portfolio = {"AAPL": 0}  # Initial portfolio with no shares

def manage_portfolio(recommendation, portfolio):
    """
    Adjust portfolio based on trading recommendations.
    :param recommendation: Buy/Sell recommendation
    :param portfolio: Current portfolio
    :return: Updated portfolio
    """
    if recommendation == "Buy":
        portfolio["AAPL"] += 10  # Buy 10 shares of AAPL
    elif recommendation == "Sell":
        portfolio["AAPL"] -= 5  # Sell 5 shares of AAPL
    return portfolio

# Title for the app
st.title("Trading Recommendation System")

# User input for stock symbols
symbols_input = st.text_input("Enter Stock Symbols (comma separated)", "AAPL, MSFT, GOOG")
symbols = [symbol.strip() for symbol in symbols_input.split(",")]

period = st.selectbox("Select Period", ["1d", "5d", "1mo", "1y"])

try:
    # Fetch market data for multiple symbols
    market_data = get_market_data(symbols, period)

    if not market_data:
        st.error("Failed to fetch market data. Please check the stock symbols and try again.")
    else:
        for symbol, data in market_data.items():
            st.subheader(f"Market Data for {symbol}")

            # Display stock data
            st.write(data['stock_data'])

            # Get and display all technical indicators
            indicators = calculate_all_indicators(data['stock_data'])

            # Display technical indicators
            if indicators['RSI'] is not None:
                st.write(f"RSI: {indicators['RSI'].iloc[-1]}")
            if indicators['SMA 50'] is not None:
                st.write(f"SMA 50: {indicators['SMA 50'].iloc[-1]}")
            if indicators['EMA 50'] is not None:
                st.write(f"EMA 50: {indicators['EMA 50'].iloc[-1]}")
            if indicators['MACD'] is not None:
                st.write(f"MACD: {indicators['MACD']['MACD'].iloc[-1]}")
            if indicators['Bollinger Bands'] is not None:
                st.write(f"Bollinger Bands - Upper: {indicators['Bollinger Bands'].iloc[-1]['BBU']}, Lower: {indicators['Bollinger Bands'].iloc[-1]['BBL']}")

            # Risk Management Metrics
            risk_metrics = risk_management(data['stock_data'], account_balance=10000)  # Example account balance
            st.write(f"Volatility: {risk_metrics['volatility']}")
            st.write(f"Maximum Drawdown: {risk_metrics['max_drawdown']}")
            st.write(f"Value at Risk (VaR): {risk_metrics['VaR']}")
            st.write(f"Position Size: {risk_metrics['position_size']}")

            # Generate recommendation based on indicators and riskgit pul
            recommendation = generate_recommendation(indicators)
            st.write(f"Recommendation: {recommendation}")

            # Portfolio Management
            portfolio = manage_portfolio(recommendation, portfolio)
            st.write(f"Portfolio: {portfolio}")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
