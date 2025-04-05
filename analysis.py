# analysis.py
import pandas as pd
import pandas_ta as ta
import numpy as np

def calculate_rsi(data, period=14):
    """
    Calculate Relative Strength Index (RSI) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for RSI calculation (default is 14).
    :return: pandas Series with RSI values.
    """
    try:
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
        return {}
        
    indicators = {}
    indicators['RSI'] = calculate_rsi(data)
    indicators['SMA 50'] = calculate_sma(data, 50)
    indicators['SMA 200'] = calculate_sma_200(data)
    indicators['EMA 50'] = calculate_ema(data, 50)
    indicators['MACD'] = calculate_macd(data)
    indicators['Bollinger Bands'] = calculate_bollinger_bands(data)
    
    # Add returns calculation for risk management
    if 'Returns' not in data.columns:
        data['Returns'] = data['Close'].pct_change()
    
    return indicators