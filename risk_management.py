# risk_management.py
import numpy as np
import pandas as pd

def calculate_volatility(data):
    """
    Calculate the volatility of the stock (annualized standard deviation of returns).
    :param data: Stock data with 'Close' price
    :return: Volatility value
    """
    try:
        # Check if Returns column exists, otherwise create it
        if 'Returns' not in data.columns:
            data['Returns'] = data['Close'].pct_change()
        
        # Remove NaN values to avoid calculation errors
        returns = data['Returns'].dropna()
        
        # Check if returns is empty
        if len(returns) == 0:
            return 0.0
            
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        return volatility
    except Exception as e:
        print(f"Error calculating volatility: {str(e)}")
        return 0.0

def calculate_max_drawdown(data):
    """
    Calculate the maximum drawdown of the stock (maximum loss from peak to trough).
    :param data: Stock data with 'Close' price
    :return: Maximum drawdown value
    """
    try:
        # Check if Returns column exists, otherwise create it
        if 'Returns' not in data.columns:
            data['Returns'] = data['Close'].pct_change()
        
        # Create a copy to avoid SettingWithCopyWarning
        data_copy = data.copy()
        
        # Calculate cumulative returns
        data_copy['Cumulative Returns'] = (1 + data_copy['Returns'].fillna(0)).cumprod()
        data_copy['Peak'] = data_copy['Cumulative Returns'].cummax()
        
        # Calculate drawdown
        drawdown = (data_copy['Cumulative Returns'] - data_copy['Peak']) / data_copy['Peak']
        max_drawdown = drawdown.min()
        
        return max_drawdown
    except Exception as e:
        print(f"Error calculating max drawdown: {str(e)}")
        return 0.0

def risk_management(data, account_balance=10000):
    """
    Perform risk management calculations.
    :param data: Stock data with 'Close' price
    :param account_balance: User account balance (default is 10,000)
    :return: Dictionary with various risk metrics
    """
    try:
        # Check if data is empty
        if data.empty:
            return {
                'volatility': 0.0,
                'max_drawdown': 0.0,
                'VaR': 0.0,
                'position_size': 0.0
            }
        
        volatility = calculate_volatility(data)
        max_drawdown = calculate_max_drawdown(data)
        
        # Get most recent closing price
        latest_price = data['Close'].iloc[-1] if not data.empty else 0
        
        # Calculate VaR (95% confidence, 1-day horizon) - simplified approach
        VaR = account_balance * volatility * 1.65 / np.sqrt(252)
        
        # Calculate position size (how many shares can be bought with 2% risk per trade)
        risk_per_trade = account_balance * 0.02  # 2% risk
        position_size = risk_per_trade / (latest_price * 0.02)  # Assuming 2% stop loss
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'VaR': VaR,
            'position_size': position_size
        }
    except Exception as e:
        print(f"Error in risk management calculations: {str(e)}")
        return {
            'volatility': 0.0,
            'max_drawdown': 0.0,
            'VaR': 0.0,
            'position_size': 0.0
        }