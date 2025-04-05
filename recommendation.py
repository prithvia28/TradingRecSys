# recommendation.py
from analysis import calculate_rsi, calculate_sma, calculate_ema, calculate_macd, calculate_bollinger_bands
from risk_management import risk_management

def generate_recommendation(data):
    """
    Generate a recommendation based on technical analysis indicators and risk management metrics.
    :param data: Stock data with technical indicators like RSI, SMA, MACD, etc.
    :return: Buy, Sell, or Hold recommendation
    """
    rsi = data['RSI'].iloc[-1] if 'RSI' in data else None
    sma_50 = data['SMA 50'].iloc[-1] if 'SMA 50' in data else None
    sma_200 = data['SMA 200'].iloc[-1] if 'SMA 200' in data else None
    ema_50 = data['EMA 50'].iloc[-1] if 'EMA 50' in data else None
    macd = data['MACD']['MACD'].iloc[-1] if 'MACD' in data else None
    macd_signal = data['MACD']['MACDs'].iloc[-1] if 'MACD' in data else None

    # Risk management values
    volatility = data['volatility'] if 'volatility' in data else None
    max_drawdown = data['max_drawdown'] if 'max_drawdown' in data else None
    position_size = data['position_size'] if 'position_size' in data else None

    recommendation = "Hold"  # Default recommendation

    # Technical Analysis Conditions
    if rsi is not None:
        if rsi < 30:
            recommendation = "Buy"
        elif rsi > 70:
            recommendation = "Sell"
    
    if sma_50 is not None and sma_200 is not None:
        if sma_50 > sma_200:
            recommendation = "Buy"
        elif sma_50 < sma_200:
            recommendation = "Sell"
    
    if ema_50 is not None and sma_50 is not None:
        if ema_50 > sma_50:
            recommendation = "Buy"
        elif ema_50 < sma_50:
            recommendation = "Sell"
    
    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            recommendation = "Buy"
        elif macd < macd_signal:
            recommendation = "Sell"

    # Risk Management Conditions
    if volatility is not None and volatility > 0.02:  # If volatility is too high, hold the position
        recommendation = "Hold"

    if max_drawdown is not None and max_drawdown < -0.2:  # If max drawdown exceeds 20%, avoid the position
        recommendation = "Hold"

    if position_size is not None and position_size > 0.1:  # If position size is too high (e.g., 10% of portfolio)
        recommendation = "Hold"  # Suggest holding if position size is too large relative to account size

    return recommendation
