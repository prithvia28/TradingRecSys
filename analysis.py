# analysis.py
import pandas as pd
import pandas_ta as ta
import numpy as np

def ensure_series_format(data):
    """
    Ensure data is in the correct format for technical analysis
    """
    # If we have a multi-level column structure (which happens with yfinance sometimes)
    if isinstance(data.columns, pd.MultiIndex):
        # Extract the data with single-level columns
        data_flat = pd.DataFrame()
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in data.columns.get_level_values(0):
                data_flat[col] = data[col].iloc[:, 0]  # Get the first column
        return data_flat
    return data

def calculate_rsi(data, period=14):
    """
    Calculate Relative Strength Index (RSI) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for RSI calculation (default is 14).
    :return: pandas Series with RSI values.
    """
    try:
        data = ensure_series_format(data)
        rsi = ta.rsi(data['Close'], length=period)
        return rsi
    except Exception as e:
        print(f"Error calculating RSI: {str(e)}")
        return pd.Series(np.nan, index=data.index)

def calculate_sma(data, period=50):
    """
    Calculate Simple Moving Average (SMA) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for SMA calculation (default is 50).
    :return: pandas Series with SMA values.
    """
    try:
        data = ensure_series_format(data)
        sma = ta.sma(data['Close'], length=period)
        return sma
    except Exception as e:
        print(f"Error calculating SMA: {str(e)}")
        return pd.Series(np.nan, index=data.index)

def calculate_ema(data, period=50):
    """
    Calculate Exponential Moving Average (EMA) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for EMA calculation (default is 50).
    :return: pandas Series with EMA values.
    """
    try:
        data = ensure_series_format(data)
        ema = ta.ema(data['Close'], length=period)
        return ema
    except Exception as e:
        print(f"Error calculating EMA: {str(e)}")
        return pd.Series(np.nan, index=data.index)

def calculate_macd(data):
    """
    Calculate MACD (Moving Average Convergence Divergence) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :return: pandas DataFrame with MACD line and Signal line.
    """
    try:
        data = ensure_series_format(data)
        macd = ta.macd(data['Close'])
        return macd
    except Exception as e:
        print(f"Error calculating MACD: {str(e)}")
        return pd.DataFrame(index=data.index)

def calculate_bollinger_bands(data, period=20):
    """
    Calculate Bollinger Bands using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for Bollinger Bands calculation (default is 20).
    :return: pandas DataFrame with upper and lower bands.
    """
    try:
        data = ensure_series_format(data)
        bollinger = ta.bbands(data['Close'], length=period)
        return bollinger
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {str(e)}")
        return pd.DataFrame(index=data.index)

def calculate_sma_200(data):
    """
    Calculate SMA 200 for golden cross/death cross signals.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :return: pandas Series with SMA 200 values.
    """
    try:
        data = ensure_series_format(data)
        sma_200 = ta.sma(data['Close'], length=200)
        return sma_200
    except Exception as e:
        print(f"Error calculating SMA 200: {str(e)}")
        return pd.Series(np.nan, index=data.index)

def calculate_all_indicators(data):
    """
    Calculate all the indicators needed for stock analysis.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :return: Dictionary with all indicators calculated.
    """
    if data is None or data.empty:
        print("No data provided to calculate_all_indicators")
        return {}
    
    # Ensure data is in the correct format first
    data = ensure_series_format(data)
    
    # debug prints
    print(f"Data columns: {data.columns}")
    print(f"Data shape: {data.shape}")
    print(f"First 3 rows: {data.head(3)}")
    
    indicators = {}
    try:
        indicators['RSI'] = calculate_rsi(data)
        print(f"RSI calculated, shape: {indicators['RSI'].shape}")
    except Exception as e:
        print(f"RSI calculation failed: {e}")
    
    try:
        indicators['SMA 50'] = calculate_sma(data, 50)
        print(f"SMA 50 calculated, shape: {indicators['SMA 50'].shape}")
    except Exception as e:
        print(f"SMA 50 calculation failed: {e}")
    
    try:
        indicators['SMA 200'] = calculate_sma_200(data)
        print(f"SMA 200 calculated, shape: {indicators['SMA 200'].shape}")
    except Exception as e:
        print(f"SMA 200 calculation failed: {e}")
    
    try:
        indicators['EMA 50'] = calculate_ema(data, 50)
        print(f"EMA 50 calculated, shape: {indicators['EMA 50'].shape}")
    except Exception as e:
        print(f"EMA 50 calculation failed: {e}")
    
    try:
        indicators['MACD'] = calculate_macd(data)
        print(f"MACD calculated, shape: {indicators['MACD'].shape}")
    except Exception as e:
        print(f"MACD calculation failed: {e}")
    
    try:
        indicators['Bollinger Bands'] = calculate_bollinger_bands(data)
        print(f"Bollinger Bands calculated, shape: {indicators['Bollinger Bands'].shape}")
    except Exception as e:
        print(f"Bollinger Bands calculation failed: {e}")
    
    # Return and risk calculation
    if 'Returns' not in data.columns:
        try:
            data['Returns'] = data['Close'].pct_change()
            print(f"Returns calculated, shape: {data['Returns'].shape}")
        except Exception as e:
            print(f"Returns calculation failed: {e}")
    
    return indicators