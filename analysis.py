# analysis.py
import pandas as pd
import pandas_ta as ta

def calculate_rsi(data, period=14):
    """
    Calculate the Relative Strength Index (RSI) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for RSI calculation (default is 14).
    :return: pandas Series with RSI values.
    """
    rsi = ta.rsi(data['Close'], length=period)
    if rsi is not None and not rsi.empty:
        return rsi.dropna()  # Drop NaN values
    return None  # Return None if RSI couldn't be calculated

def calculate_sma(data, period=50):
    """
    Calculate the Simple Moving Average (SMA) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for SMA calculation (default is 50).
    :return: pandas Series with SMA values.
    """
    sma = ta.sma(data['Close'], length=period)
    if sma is not None and not sma.empty:
        return sma.dropna()  # Drop NaN values
    return None  # Return None if SMA couldn't be calculated

def calculate_ema(data, period=50):
    """
    Calculate the Exponential Moving Average (EMA) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for EMA calculation (default is 50).
    :return: pandas Series with EMA values.
    """
    ema = ta.ema(data['Close'], length=period)
    if ema is not None and not ema.empty:
        return ema.dropna()  # Drop NaN values
    return None  # Return None if EMA couldn't be calculated

def calculate_macd(data):
    """
    Calculate the Moving Average Convergence Divergence (MACD) using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :return: pandas DataFrame with MACD and Signal line values.
    """
    macd = ta.macd(data['Close'])
    if macd is not None and not macd.empty:
        return macd.dropna()  # Drop NaN values
    return None  # Return None if MACD couldn't be calculated

def calculate_bollinger_bands(data, period=20):
    """
    Calculate Bollinger Bands using pandas_ta.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :param period: Period for Bollinger Bands calculation (default is 20).
    :return: pandas DataFrame with upper and lower bands, as well as the middle band (SMA).
    """
    bbands = ta.bbands(data['Close'], length=period)
    if bbands is not None and not bbands.empty:
        return bbands.dropna()  # Drop NaN values
    return None  # Return None if Bollinger Bands couldn't be calculated

def calculate_all_indicators(data):
    """
    Calculate all important technical analysis indicators.
    :param data: Stock data (pandas DataFrame) containing 'Close' prices.
    :return: A dictionary with all calculated indicators (RSI, SMA, EMA, MACD, Bollinger Bands).
    """
    indicators = {}

    # Calculate RSI (14-period by default)
    indicators['RSI'] = calculate_rsi(data)

    # Calculate SMA (50-period by default)
    indicators['SMA 50'] = calculate_sma(data, period=50)

    # Calculate EMA (50-period by default)
    indicators['EMA 50'] = calculate_ema(data, period=50)

    # Calculate MACD
    indicators['MACD'] = calculate_macd(data)

    # Calculate Bollinger Bands (20-period by default)
    indicators['Bollinger Bands'] = calculate_bollinger_bands(data, period=20)

    return indicators
