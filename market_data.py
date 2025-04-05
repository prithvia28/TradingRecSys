import yfinance as yf
import pandas as pd
import datetime
import numpy as np
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

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
            if stock_data is not None and len(stock_data) > 0:
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
        if len(todays_data) > 0:
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
            # Get real-time price
            real_time_price = get_real_time_price(symbol)
            # Add stock data and trends to dictionary
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

def get_market_volume_data(symbols=["AAPL"], period="1y", interval="1d"):
    """
    Extract volume-specific market data for analysis.
    :param symbols: List of stock symbols
    :param period: Data period (e.g., "1y", "1mo")
    :param interval: Data interval (e.g., "1d", "1m")
    :return: Dictionary with volume data and trends for each symbol
    """
    volume_data = {}
    stock_data_dict = get_stock_data(symbols, period, interval)
    
    for symbol, stock_data in stock_data_dict.items():
        try:
            if 'Volume' in stock_data.columns:
                # Calculate volume trends
                avg_volume = stock_data['Volume'].mean()
                max_volume = stock_data['Volume'].max()
                recent_volume = stock_data['Volume'].iloc[-5:].mean()  # Average of last 5 periods
                
                # Calculate relative volume (recent vs average)
                relative_volume = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Add volume data to dictionary
                volume_data[symbol] = {
                    "avg_volume": avg_volume,
                    "max_volume": max_volume,
                    "recent_volume": recent_volume,
                    "relative_volume": relative_volume,
                    "volume_data": stock_data['Volume']  # Full volume series
                }
            else:
                print(f"Warning: No volume data available for {symbol}")
        except Exception as e:
            print(f"Error processing volume data for {symbol}: {str(e)}")
    
    return volume_data

def get_technical_indicators(symbols=["AAPL"], period="1y", interval="1d"):
    """
    Calculate basic technical indicators for given symbols.
    :param symbols: List of stock symbols
    :param period: Data period
    :param interval: Data interval
    :return: Dictionary with technical indicators for each symbol
    """
    technical_data = {}
    stock_data_dict = get_stock_data(symbols, period, interval)
    
    for symbol, stock_data in stock_data_dict.items():
        try:
            # Make a copy to avoid modifying the original data
            df = stock_data.copy()
            
            # Calculate moving averages
            df['MA_20'] = df['Close'].rolling(window=20).mean()
            df['MA_50'] = df['Close'].rolling(window=50).mean()
            df['MA_200'] = df['Close'].rolling(window=200).mean()
            
            # Calculate RSI (Relative Strength Index)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD (Moving Average Convergence Divergence)
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            # Extract the latest values
            ma_20 = None if df['MA_20'].isna().all() else df['MA_20'].iloc[-1]
            ma_50 = None if df['MA_50'].isna().all() else df['MA_50'].iloc[-1]
            ma_200 = None if df['MA_200'].isna().all() else df['MA_200'].iloc[-1]
            rsi = None if df['RSI'].isna().all() else df['RSI'].iloc[-1]
            macd_line = None if df['MACD'].isna().all() else df['MACD'].iloc[-1]
            macd_signal = None if df['MACD_Signal'].isna().all() else df['MACD_Signal'].iloc[-1]
            
            # Store indicators in result dictionary
            technical_data[symbol] = {
                "moving_averages": {
                    "MA_20": ma_20,
                    "MA_50": ma_50,
                    "MA_200": ma_200
                },
                "rsi": rsi,
                "macd": {
                    "macd_line": macd_line,
                    "signal_line": macd_signal
                },
                "indicators_data": df[['Close', 'MA_20', 'MA_50', 'MA_200', 'RSI', 'MACD', 'MACD_Signal']]
            }
        except Exception as e:
            print(f"Error calculating technical indicators for {symbol}: {str(e)}")
    
    return technical_data

def get_market_index_data(indices=["^GSPC", "^DJI", "^IXIC"], period="1y", interval="1d"):
    """
    Fetch data for major market indices.
    :param indices: List of index symbols (^GSPC: S&P 500, ^DJI: Dow Jones, ^IXIC: NASDAQ)
    :param period: Data period
    :param interval: Data interval
    :return: Dictionary with index data
    """
    return get_stock_data(indices, period, interval)

def get_market_sector_performance(period="1y", interval="1d"):
    """
    Fetch performance data for major market sectors using ETFs.
    :param period: Data period
    :param interval: Data interval
    :return: Dictionary with sector performance data
    """
    # Sector ETFs
    sector_etfs = {
        "Technology": "XLK",
        "Healthcare": "XLV",
        "Financials": "XLF",
        "Consumer_Discretionary": "XLY", 
        "Consumer_Staples": "XLP",
        "Energy": "XLE",
        "Industrials": "XLI",
        "Materials": "XLB",
        "Utilities": "XLU",
        "Real_Estate": "XLRE",
        "Communication_Services": "XLC"
    }
    
    # Get data for all sector ETFs
    etf_data = get_stock_data(list(sector_etfs.values()), period, interval)
    
    # Calculate performance metrics
    sector_performance = {}
    for sector_name, etf_symbol in sector_etfs.items():
        if etf_symbol in etf_data:
            data = etf_data[etf_symbol]
            if len(data) > 0:
                # Calculate returns for different periods
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                
                if start_price > 0:
                    total_return = (end_price - start_price) / start_price * 100
                    
                    # Calculate additional metrics
                    sector_performance[sector_name] = {
                        "etf_symbol": etf_symbol,
                        "total_return_pct": total_return,
                        "start_price": float(start_price),
                        "current_price": float(end_price),
                        "price_data": data['Close']
                    }
    
    return sector_performance

def get_volatility_data(symbols=["AAPL"], period="1y", interval="1d"):
    """
    Calculate volatility metrics for given symbols.
    :param symbols: List of stock symbols
    :param period: Data period
    :param interval: Data interval
    :return: Dictionary with volatility metrics for each symbol
    """
    volatility_data = {}
    stock_data_dict = get_stock_data(symbols, period, interval)
    
    for symbol, stock_data in stock_data_dict.items():
        try:
            # Calculate daily returns
            df = stock_data.copy()
            df['Returns'] = df['Close'].pct_change() * 100
            
            # Calculate historical volatility (standard deviation of returns)
            daily_volatility = df['Returns'].std()
            
            # Annualize volatility (approx. based on trading days)
            if interval == "1d":
                annual_volatility = daily_volatility * np.sqrt(252)
            elif interval == "1wk":
                annual_volatility = daily_volatility * np.sqrt(52)
            elif interval == "1mo":
                annual_volatility = daily_volatility * np.sqrt(12)
            else:
                annual_volatility = daily_volatility  # No annualization for other intervals
            
            # Calculate volatility over different time windows
            vol_10d = None
            if len(df) >= 10:
                vol_10d = df['Returns'].rolling(window=10).std().iloc[-1]
                
            vol_30d = None
            if len(df) >= 30:
                vol_30d = df['Returns'].rolling(window=30).std().iloc[-1]
            
            # Store volatility metrics
            volatility_data[symbol] = {
                "daily_volatility": daily_volatility,
                "annual_volatility": annual_volatility,
                "volatility_10d": vol_10d,
                "volatility_30d": vol_30d,
                "max_daily_move": df['Returns'].abs().max(),
                "returns_series": df['Returns']
            }
        except Exception as e:
            print(f"Error calculating volatility for {symbol}: {str(e)}")
    
    return volatility_data

def get_earnings_calendar(symbols=["AAPL"], days_forward=30):
    """
    Get upcoming earnings dates for specified symbols.
    :param symbols: List of stock symbols
    :param days_forward: Number of days to look ahead
    :return: Dictionary with upcoming earnings dates
    """
    earnings_data = {}
    
    for symbol in symbols:
        try:
            # Get ticker information
            ticker = yf.Ticker(symbol)
            
            # Try to get calendar data - with better error handling
            try:
                calendar = ticker.calendar
                
                if calendar is not None and isinstance(calendar, pd.DataFrame) and len(calendar) > 0:
                    # Extract earnings date
                    earnings_date = calendar.iloc[0, 0] if len(calendar) > 0 else None
                    
                    # Check if within the specified days
                    if earnings_date is not None:
                        now = datetime.datetime.now()
                        days_until_earnings = (earnings_date - now).days
                        
                        if 0 <= days_until_earnings <= days_forward:
                            earnings_data[symbol] = {
                                "earnings_date": earnings_date.strftime('%Y-%m-%d'),
                                "days_until_earnings": days_until_earnings
                            }
            except AttributeError:
                # Alternative method - try to get next earnings date directly
                try:
                    earnings_date = ticker.earnings_dates
                    if earnings_date is not None and isinstance(earnings_date, pd.DataFrame) and len(earnings_date) > 0:
                        # Get the most recent future date
                        now = datetime.datetime.now()
                        future_dates = earnings_date[earnings_date.index > now]
                        
                        if len(future_dates) > 0:
                            next_date = future_dates.index[0]
                            days_until_earnings = (next_date - now).days
                            
                            if 0 <= days_until_earnings <= days_forward:
                                earnings_data[symbol] = {
                                    "earnings_date": next_date.strftime('%Y-%m-%d'),
                                    "days_until_earnings": days_until_earnings
                                }
                except Exception as inner_e:
                    print(f"Alternative earnings detection failed for {symbol}: {str(inner_e)}")
        except Exception as e:
            print(f"Error retrieving earnings data for {symbol}: {str(e)}")
    
    return earnings_data

if __name__ == "__main__":
    # Example usage
    symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
    
    # Get market data
    market_data = get_market_data(symbols, period="1y", interval="1d")
    print(f"Market data retrieved for {len(market_data)} symbols")
    
    # Get technical indicators
    tech_data = get_technical_indicators(symbols)
    print(f"Technical indicators calculated for {len(tech_data)} symbols")
    
    # Get sector performance
    sector_data = get_market_sector_performance()
    print(f"Sector performance data retrieved for {len(sector_data)} sectors")