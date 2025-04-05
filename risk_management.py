# risk_management.py
import numpy as np
import pandas as pd

def calculate_volatility(data):
    """
    Calculate the volatility of the stock (annualized standard deviation of returns).
    :param data: Stock data with 'Close' price
    :return: Annualized volatility
    """
    data['Returns'] = data['Close'].pct_change()
    volatility = np.std(data['Returns']) * np.sqrt(252)  # Annualized volatility (252 trading days in a year)
    return volatility

def calculate_max_drawdown(data):
    """
    Calculate the maximum drawdown of the stock (maximum loss from peak to trough).
    :param data: Stock data with 'Close' price
    :return: Maximum drawdown
    """
    data['Cumulative Returns'] = (1 + data['Returns']).cumprod()
    data['Peak'] = data['Cumulative Returns'].cummax()
    drawdown = (data['Cumulative Returns'] - data['Peak']) / data['Peak']
    max_drawdown = drawdown.min()  # Maximum drawdown is the minimum value of the drawdown series
    return max_drawdown

def calculate_var(data, confidence_level=0.95):
    """
    Calculate the Value at Risk (VaR) using the historical method.
    :param data: Stock data with 'Close' price
    :param confidence_level: The confidence level for VaR calculation (default is 95%)
    :return: Value at Risk (VaR) at the given confidence level
    """
    data['Returns'] = data['Close'].pct_change()
    var = np.percentile(data['Returns'].dropna(), (1 - confidence_level) * 100)
    return var

def calculate_position_size(account_balance, risk_per_trade, volatility):
    """
    Calculate the position size based on volatility and risk per trade.
    :param account_balance: Total value of the account
    :param risk_per_trade: Percentage of account balance to risk on a single trade
    :param volatility: The volatility of the asset
    :return: Position size
    """
    position_size = (account_balance * risk_per_trade) / volatility
    return position_size

def risk_management(data, account_balance, risk_per_trade=0.02, confidence_level=0.95):
    """
    Run the risk management functions and return key risk metrics.
    :param data: Stock data with 'Close' prices
    :param account_balance: Total account balance
    :param risk_per_trade: Percentage of the account balance to risk on a single trade (default is 2%)
    :param confidence_level: Confidence level for VaR calculation (default is 95%)
    :return: A dictionary with risk metrics (volatility, max_drawdown, VaR, position_size)
    """
    # Calculate volatility
    volatility = calculate_volatility(data)

    # Calculate maximum drawdown
    max_drawdown = calculate_max_drawdown(data)

    # Calculate Value at Risk (VaR)
    var = calculate_var(data, confidence_level)

    # Calculate position size
    position_size = calculate_position_size(account_balance, risk_per_trade, volatility)

    # Return all risk metrics in a dictionary
    return {
        "volatility": volatility,
        "max_drawdown": max_drawdown,
        "VaR": var,
        "position_size": position_size
    }
