# market_data.py
import yfinance as yf
from forex_python.converter import CurrencyRates
import pandas as pd

def get_stock_data(symbols=["AAPL"], period="1y", interval="1d"):
    """
    Fetch historical stock data for multiple symbols from Yahoo Finance.
    :param symbols: List of stock symbols (e.g., ["AAPL", "MSFT", "GOOG"])
    :param period: Data period (e.g., "1mo", "1y")
    :param interval: Data interval (e.g., "1d" for daily, "1m" for minute)
    :return: Dictionary of Pandas DataFrames, each containing stock data for a symbol
    """
    stock_data_dict = {}

    for symbol in symbols:
        stock_data = yf.download(symbol, period=period, interval=interval)
        if stock_data is not None and not stock_data.empty:
            stock_data_dict[symbol] = stock_data
        else:
            print(f"Warning: No data available for {symbol}")
    
    return stock_data_dict

def get_real_time_price(symbol="AAPL"):
    """
    Fetch real-time price for a single stock symbol.
    :param symbol: Stock symbol (e.g., "AAPL")
    :return: Current price of the stock
    """
    stock = yf.Ticker(symbol)
    current_price = stock.history(period="1d")["Close"].iloc[0]  # Last closing price for today
    return current_price

def get_currency_exchange_rate(from_currency="USD", to_currency="EUR"):
    """
    Fetch real-time currency exchange rate.
    :param from_currency: The currency to convert from (e.g., "USD")
    :param to_currency: The currency to convert to (e.g., "EUR")
    :return: Current exchange rate
    """
    currency_rate = CurrencyRates()
    rate = currency_rate.get_rate(from_currency, to_currency)
    return rate

def get_market_data(symbols=["AAPL"], period="1y", interval="1d"):
    """
    Fetch both stock data and real-time prices for multiple symbols and calculate price trends.
    :param symbols: List of stock symbols (e.g., ["AAPL", "GOOG"])
    :param period: Data period (e.g., "1y", "1mo")
    :param interval: Data interval (e.g., "1d", "1m")
    :return: Dictionary with stock data and price trends for each symbol
    """
    market_data = {}

    # Fetch historical stock data
    stock_data_dict = get_stock_data(symbols, period, interval)

    for symbol, stock_data in stock_data_dict.items():
        # Calculate price trends (High, Low, Open, Close)
        high_price = stock_data['High'].max()
        low_price = stock_data['Low'].min()
        average_price = stock_data['Close'].mean()

        # Get real-time price
        real_time_price = get_real_time_price(symbol)

        # Add stock data and trends to dictionary
        market_data[symbol] = {
            "stock_data": stock_data.tail(5),  # Latest 5 rows of data
            "high_price": high_price,
            "low_price": low_price,
            "average_price": average_price,
            "real_time_price": real_time_price
        }

    return market_data
