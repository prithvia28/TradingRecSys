import market_data
import pandas as pd
import matplotlib.pyplot as plt
import time
from tabulate import tabulate

def display_market_data(symbols, period="6mo", interval="1d"):
    """
    Test and display market data analysis for the given symbols.
    """
    print(f"\n{'='*60}")
    print(f"MARKET DATA ANALYSIS FOR {', '.join(symbols)}")
    print(f"Period: {period}, Interval: {interval}")
    print(f"{'='*60}\n")
    
    # Get basic market data
    print("Fetching market data...")
    market_data_results = market_data.get_market_data(symbols, period, interval)
    
    # Display price information
    print("\nPRICE SUMMARY:")
    price_table = []
    for symbol, data in market_data_results.items():
        # Convert any Series to float before formatting
        real_time_price = float(data['real_time_price']) if data['real_time_price'] is not None else None
        high_price = float(data['high_price']) if data['high_price'] is not None else None
        low_price = float(data['low_price']) if data['low_price'] is not None else None
        average_price = float(data['average_price']) if data['average_price'] is not None else None
        
        price_table.append([
            symbol,
            f"${real_time_price:.2f}" if real_time_price is not None else "N/A",
            f"${high_price:.2f}" if high_price is not None else "N/A",
            f"${low_price:.2f}" if low_price is not None else "N/A",
            f"${average_price:.2f}" if average_price is not None else "N/A"
        ])
    
    print(tabulate(price_table, headers=["Symbol", "Current Price", "High", "Low", "Average"], tablefmt="pretty"))
    
    # Get volume data
    print("\nFetching volume data...")
    volume_data = market_data.get_market_volume_data(symbols, period, interval)
    
    # Display volume information
    print("\nVOLUME SUMMARY:")
    volume_table = []
    for symbol, data in volume_data.items():
        # Convert any Series to float before formatting
        avg_volume = float(data['avg_volume']) if data['avg_volume'] is not None else None
        recent_volume = float(data['recent_volume']) if data['recent_volume'] is not None else None
        relative_volume = float(data['relative_volume']) if data['relative_volume'] is not None else None
        
        volume_table.append([
            symbol,
            f"{avg_volume:,.0f}" if avg_volume is not None else "N/A",
            f"{recent_volume:,.0f}" if recent_volume is not None else "N/A",
            f"{relative_volume:.2f}x" if relative_volume is not None else "N/A"
        ])
    
    print(tabulate(volume_table, headers=["Symbol", "Avg Volume", "Recent Volume", "Relative Volume"], tablefmt="pretty"))
    
    # Get technical indicators
    print("\nCalculating technical indicators...")
    tech_indicators = market_data.get_technical_indicators(symbols, period, interval)
    
    # Display technical indicators
    print("\nTECHNICAL INDICATORS:")
    tech_table = []
    for symbol, data in tech_indicators.items():
        # Extract and convert values safely
        rsi_value = float(data['rsi']) if data['rsi'] is not None else None
        
        ma_20 = data['moving_averages']['MA_20']
        ma_20 = float(ma_20) if ma_20 is not None else None
        
        ma_50 = data['moving_averages']['MA_50']
        ma_50 = float(ma_50) if ma_50 is not None else None
        
        ma_200 = data['moving_averages']['MA_200']
        ma_200 = float(ma_200) if ma_200 is not None else None
        
        macd_line = data['macd']['macd_line']
        macd_line = float(macd_line) if macd_line is not None else None
        
        signal_line = data['macd']['signal_line']
        signal_line = float(signal_line) if signal_line is not None else None
        
        # Determine signals
        rsi_signal = "Oversold" if rsi_value is not None and rsi_value < 30 else "Overbought" if rsi_value is not None and rsi_value > 70 else "Neutral"
        macd_signal = "Bullish" if macd_line is not None and signal_line is not None and macd_line > signal_line else "Bearish" if macd_line is not None and signal_line is not None else "N/A"
        
        tech_table.append([
            symbol,
            f"${ma_20:.2f}" if ma_20 is not None else "N/A",
            f"${ma_50:.2f}" if ma_50 is not None else "N/A",
            f"${ma_200:.2f}" if ma_200 is not None else "N/A",
            f"{rsi_value:.1f} ({rsi_signal})" if rsi_value is not None else "N/A",
            macd_signal
        ])
    
    print(tabulate(tech_table, headers=["Symbol", "MA(20)", "MA(50)", "MA(200)", "RSI", "MACD Signal"], tablefmt="pretty"))
    
    # Get volatility data
    print("\nCalculating volatility metrics...")
    volatility_results = market_data.get_volatility_data(symbols, period, interval)
    
    # Display volatility information
    print("\nVOLATILITY METRICS:")
    volatility_table = []
    for symbol, data in volatility_results.items():
        # Convert any Series to float before formatting
        daily_vol = float(data['daily_volatility']) if data['daily_volatility'] is not None else None
        annual_vol = float(data['annual_volatility']) if data['annual_volatility'] is not None else None
        max_move = float(data['max_daily_move']) if data['max_daily_move'] is not None else None
        
        volatility_table.append([
            symbol,
            f"{daily_vol:.2f}%" if daily_vol is not None else "N/A",
            f"{annual_vol:.2f}%" if annual_vol is not None else "N/A",
            f"{max_move:.2f}%" if max_move is not None else "N/A"
        ])
    
    print(tabulate(volatility_table, headers=["Symbol", "Daily Vol", "Annual Vol", "Max Daily Move"], tablefmt="pretty"))
    
    # Get earnings calendar
    print("\nChecking upcoming earnings...")
    try:
        earnings_results = market_data.get_earnings_calendar(symbols, days_forward=60)
        
        # Display earnings information
        if earnings_results:
            print("\nUPCOMING EARNINGS:")
            earnings_table = []
            for symbol, data in earnings_results.items():
                earnings_table.append([
                    symbol,
                    data['earnings_date'],
                    f"{data['days_until_earnings']} days"
                ])
            
            print(tabulate(earnings_table, headers=["Symbol", "Earnings Date", "Days Until"], tablefmt="pretty"))
        else:
            print("\nNo upcoming earnings found within the next 60 days.")
    except Exception as e:
        print(f"\nError retrieving earnings data: {str(e)}")
    
    # Get sector performance
    print("\nFetching sector performance...")
    try:
        sector_results = market_data.get_market_sector_performance(period, interval)
        
        # Display sector performance
        print("\nSECTOR PERFORMANCE:")
        sector_table = []
        for sector, data in sector_results.items():
            # Safely extract and convert values
            try:
                current_price = float(data['current_price']) if data['current_price'] is not None else None
                total_return = float(data['total_return_pct']) if data['total_return_pct'] is not None else None
                
                sector_table.append([
                    sector,
                    data['etf_symbol'],
                    f"${current_price:.2f}" if current_price is not None else "N/A",
                    f"{total_return:.2f}%" if total_return is not None else "N/A"
                ])
            except Exception as sector_err:
                print(f"Error processing sector {sector}: {str(sector_err)}")
        
        # Sort by performance (descending) - safely
        if sector_table:
            # Define a safe sorting function to handle "N/A" values
            def safe_sort_key(row):
                try:
                    # Extract the percentage value without the % symbol
                    return_str = row[3]
                    if return_str == "N/A":
                        return float('-inf')
                    return float(return_str.replace('%', ''))
                except (ValueError, AttributeError, IndexError):
                    return float('-inf')  # Place N/A values at the end
            
            try:
                sector_table.sort(key=safe_sort_key, reverse=True)
            except Exception as sort_err:
                print(f"Error sorting sector data: {str(sort_err)}")
        
        print(tabulate(sector_table, headers=["Sector", "ETF", "Current Price", "Total Return"], tablefmt="pretty"))
    except Exception as e:
        print(f"\nError processing sector performance: {str(e)}")
    
    # Plot some charts
    try:
        plot_charts(symbols, market_data_results, tech_indicators)
    except Exception as e:
        print(f"\nError generating charts: {str(e)}")
        print("You can still view the tabular data above.")

def plot_charts(symbols, market_data_results, tech_indicators):
    """
    Create and display charts for the analyzed data.
    """
    print("\nGenerating charts (close window to continue)...")
    
    # Create a figure with subplots based on the number of symbols
    fig, axes = plt.subplots(len(symbols), 2, figsize=(15, 5 * len(symbols)))
    fig.suptitle("Market Data Analysis Visualization", fontsize=16)
    
    # Handle the case when there's only one symbol
    if len(symbols) == 1:
        axes = [axes]
    
    for i, symbol in enumerate(symbols):
        if symbol in market_data_results and symbol in tech_indicators:
            try:
                price_data = market_data_results[symbol]['stock_data']['Close']
                tech_data = tech_indicators[symbol]['indicators_data']
                
                # Plot price and moving averages
                ax1 = axes[i][0]
                price_data.plot(ax=ax1, label='Close Price')
                
                if 'MA_20' in tech_data.columns:
                    tech_data['MA_20'].plot(ax=ax1, label='MA(20)')
                if 'MA_50' in tech_data.columns:
                    tech_data['MA_50'].plot(ax=ax1, label='MA(50)')
                if 'MA_200' in tech_data.columns:
                    tech_data['MA_200'].plot(ax=ax1, label='MA(200)')
                
                ax1.set_title(f"{symbol} - Price and Moving Averages")
                ax1.set_ylabel("Price ($)")
                ax1.legend()
                ax1.grid(True)
                
                # Plot RSI
                ax2 = axes[i][1]
                if 'RSI' in tech_data.columns:
                    tech_data['RSI'].plot(ax=ax2, label='RSI', color='purple')
                    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
                    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
                    ax2.set_ylim([0, 100])
                
                ax2.set_title(f"{symbol} - RSI")
                ax2.set_ylabel("RSI")
                ax2.legend()
                ax2.grid(True)
            except Exception as e:
                # If there's an error with one stock's chart, print a message but continue with others
                print(f"Error plotting data for {symbol}: {str(e)}")
                if i < len(axes):
                    axes[i][0].set_title(f"{symbol} - Error plotting data")
                    axes[i][1].set_title(f"{symbol} - Error plotting data")
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()

def run_test():
    """
    Main function to run tests with different parameters.
    """
    # Default test case
    default_symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
    
    # Ask for user input
    print("\nMARKET DATA ANALYSIS TOOL")
    print("========================")
    
    user_input = input("Enter stock symbols (comma separated) or press Enter for defaults: ")
    symbols = [s.strip() for s in user_input.split(",")] if user_input and user_input.strip() else default_symbols
    
    period_options = {
        "1": "1mo",
        "2": "3mo",
        "3": "6mo",
        "4": "1y",
        "5": "2y",
        "6": "5y"
    }
    
    print("\nSelect time period:")
    for key, value in period_options.items():
        print(f"{key}: {value}")
    
    period_choice = input("Enter choice (default is 6mo): ")
    period = period_options.get(period_choice, "6mo")
    
    interval_options = {
        "1": "1d",
        "2": "1wk",
        "3": "1mo"
    }
    
    print("\nSelect interval:")
    for key, value in interval_options.items():
        print(f"{key}: {value}")
    
    interval_choice = input("Enter choice (default is 1d): ")
    interval = interval_options.get(interval_choice, "1d")
    
    # Run the analysis
    display_market_data(symbols, period, interval)

if __name__ == "__main__":
    try:
        # Check if we can import required modules
        required_modules = ["yfinance", "pandas", "matplotlib", "tabulate"]
        missing_modules = []

        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            print(f"Error: Missing required modules: {', '.join(missing_modules)}")
        else:
            run_test()

    except Exception as e:
        print(f"Error during execution: {str(e)}")
