# market_data.py
import yfinance as yf
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
        try:
            stock_data = yf.download(symbol, period=period, interval=interval)
            if stock_data is not None and not stock_data.empty:
                stock_data_dict[symbol] = stock_data
            else:
                print(f"Warning: No data found for {symbol}")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
    
    return stock_data_dict

def get_real_time_price(symbol="AAPL"):
    """
    Fetch real-time price for a single stock symbol.
    :param symbol: Stock symbol (e.g., "AAPL")
    :return: Current price of the stock
    """
    try:
        stock = yf.Ticker(symbol)
        # Get the most recent closing price - using last available data
        todays_data = stock.history(period="1d")
        if not todays_data.empty:
            current_price = todays_data["Close"].iloc[-1]  # Get the last available closing price
            return current_price
        else:
            print(f"Warning: No price data available for {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching real-time price for {symbol}: {str(e)}")
        return None

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
        try:
            # Calculate price trends (High, Low, Open, Close)
            high_price = stock_data['High'].max()
            low_price = stock_data['Low'].min()
            average_price = stock_data['Close'].mean()

            # To get real time price
            real_time_price = get_real_time_price(symbol)

            # Adding stock data & trends to dictionary
            market_data[symbol] = {
                "stock_data": stock_data,  # Keep all data for calculations
                "high_price": high_price,
                "low_price": low_price,
                "average_price": average_price,
                "real_time_price": real_time_price
            }
        except Exception as e:
            print(f"Error processing market data for {symbol}: {str(e)}")
    
    return market_data