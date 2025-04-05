import numpy as np
import pandas as pd

def calculate_volatility(data):
    """
    Calculate the volatility of the stock (annualized standard deviation of returns).
    
    :param data: Stock data with 'Close' price (A DataFrame with 'Close' column)
    :return: Volatility value (Annualized Standard Deviation of Returns)
    """
    try:
        # Check if 'Returns' column exists, otherwise create it. Returns = Percentage Change in 'Close' Price
        if 'Returns' not in data.columns:
            data['Returns'] = data['Close'].pct_change()  # pct_change() calculates daily returns
        
        # Remove NaN values (due to the first row in 'Returns' being NaN after pct_change())
        returns = data['Returns'].dropna()
        
        # If returns is empty, return volatility as 0
        if len(returns) == 0:
            return 0.0
        
        # Calculate standard deviation of the daily returns
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility (252 trading days in a year)
        return volatility
    except Exception as e:
        # If there's an error in the volatility calculation, return 0
        print(f"Error calculating volatility: {str(e)}")
        return 0.0


def calculate_max_drawdown(data):
    """
    Calculate the maximum drawdown of the stock (maximum loss from peak to trough).
    
    :param data: Stock data with 'Close' price (A DataFrame with 'Close' column)
    :return: Maximum drawdown value (as a percentage)
    """
    try:
        # Check if 'Returns' column exists, otherwise create it
        if 'Returns' not in data.columns:
            data['Returns'] = data['Close'].pct_change()  # pct_change() calculates daily returns
        
        # Create a copy of data to avoid SettingWithCopyWarning
        data_copy = data.copy()
        
        # Calculate cumulative returns (total return over time)
        data_copy['Cumulative Returns'] = (1 + data_copy['Returns'].fillna(0)).cumprod()
        
        # Track the peak (highest cumulative return up to that point)
        data_copy['Peak'] = data_copy['Cumulative Returns'].cummax()
        
        # Calculate the drawdown, which is the difference between the cumulative return and the peak
        drawdown = (data_copy['Cumulative Returns'] - data_copy['Peak']) / data_copy['Peak']
        
        # The maximum drawdown is the lowest point in the drawdown series
        max_drawdown = drawdown.min()
        
        return max_drawdown
    except Exception as e:
        # If there's an error in the max drawdown calculation, return 0
        print(f"Error calculating max drawdown: {str(e)}")
        return 0.0


def calculate_risk_level(volatility, max_drawdown):
    """
    Risk Level Assessment based on volatility and max drawdown.
    Classifies the risk level as 'Low', 'Medium', 'High', or 'Very High'.

    :param volatility: Volatility value (annualized standard deviation of returns)
    :param max_drawdown: Maximum drawdown value (as a percentage)
    :return: Risk Level classification as string
    """
    # Define thresholds for risk classification
    LOW_VOL_THRESHOLD = 0.10  # Low volatility is less than 10%
    MEDIUM_VOL_THRESHOLD = 0.20  # Medium volatility between 10% and 20%
    HIGH_VOL_THRESHOLD = 0.30  # High volatility is above 30%

    LOW_DRAW_THRESHOLD = -0.10  # Low max drawdown less than 10%
    MEDIUM_DRAW_THRESHOLD = -0.20  # Medium max drawdown between -10% and -20%
    HIGH_DRAW_THRESHOLD = -0.30  # High max drawdown is below -30%

    # Risk level classification
    if volatility < LOW_VOL_THRESHOLD and max_drawdown > LOW_DRAW_THRESHOLD:
        return "Low"
    elif volatility < MEDIUM_VOL_THRESHOLD and max_drawdown > MEDIUM_DRAW_THRESHOLD:
        return "Medium"
    elif volatility < HIGH_VOL_THRESHOLD and max_drawdown > HIGH_DRAW_THRESHOLD:
        return "High"
    else:
        return "Very High"


def risk_management(data, account_balance=10000):
    """
    Perform risk management calculations, including risk level assessment.
    
    :param data: Stock data with 'Close' price (A DataFrame with 'Close' column)
    :param account_balance: User account balance (default is 10,000 USD)
    :return: Dictionary with various risk metrics and risk level
    """
    try:
        # Check if data is empty. If it is, return default values (no risk data)
        if data.empty:
            return {
                'volatility': 0.0,
                'max_drawdown': 0.0,
                'VaR': 0.0,
                'position_size': 0.0,
                'risk_level': 'Low'
            }
        
        # Calculate volatility (annualized standard deviation of returns)
        volatility = calculate_volatility(data)
        
        # Calculate maximum drawdown (the maximum loss from peak to trough)
        max_drawdown = calculate_max_drawdown(data)
        
        # Get the most recent closing price of the stock
        latest_price = data['Close'].iloc[-1] if not data.empty else 0
        
        # Calculate VaR (Value at Risk) - simplified approach (95% confidence, 1-day horizon)
        VaR = account_balance * volatility * 1.65 / np.sqrt(252)
        
        # Calculate position size (how many shares can be bought with 2% risk per trade)
        risk_per_trade = account_balance * 0.02  # 2% risk per trade
        position_size = risk_per_trade / (latest_price * 0.02)  # Assuming 2% stop loss (risk management method)
        
        # Assess the risk level
        risk_level = calculate_risk_level(volatility, max_drawdown)
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'VaR': VaR,
            'position_size': position_size,
            'risk_level': risk_level  # Risk Level: Low, Medium, High, Very High
        }
    except Exception as e:
        # If there's an error in the risk management calculation, return default values
        print(f"Error in risk management calculations: {str(e)}")
        return {
            'volatility': 0.0,
            'max_drawdown': 0.0,
            'VaR': 0.0,
            'position_size': 0.0,
            'risk_level': 'Low'
        }
