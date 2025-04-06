# app.py - Improved Trading Recommendation System
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf

# Import custom modules
from market_data import get_market_data, get_stock_data
from analysis import calculate_all_indicators, ensure_series_format
from recommendation import generate_recommendation
from risk_management import risk_management
from news_updates import display_news_blocks
from chatbot import minimizable_trading_chatbot
# Import agents
from communication import AgentCommunicationBus
from agents import (
    MarketDataAgent, 
    TechnicalAnalysisAgent, 
    RiskManagementAgent, 
    ExecutionAgent
)

# Initialize agents
bus = AgentCommunicationBus()
market_data_agent = MarketDataAgent(bus)
tech_agent = TechnicalAnalysisAgent(bus)
execution_agent = ExecutionAgent(bus)
risk_agent = RiskManagementAgent(bus)

# Import functions from your db.py file
from db import (
    get_portfolio,
    create_portfolio,
    update_portfolio,
    load_portfolio_from_mongo,
    save_portfolio_to_mongo
)

# Page configuration
st.set_page_config(layout="wide", page_title="FinnXperts")

# Create a three-column layout for the main content area
col_main, col_news = st.columns([2, 1])

if 'user_id' not in st.session_state:
    st.session_state.user_id = "default_user"  # Use a default user for demo

# Initialize session state for portfolio if it doesn't exist
if 'portfolio' not in st.session_state:
    # Try to load from MongoDB
    mongo_portfolio = load_portfolio_from_mongo(st.session_state.user_id)
    
    if mongo_portfolio:
        # Convert MongoDB portfolio format to session state format
        portfolio_dict = {}
        for stock in mongo_portfolio:
            portfolio_dict[stock['symbol']] = {
                'shares': stock['shares'],
                'avg_price': stock['avg_price'],
                'value': 0  # Will be updated later
            }
        st.session_state.portfolio = portfolio_dict
    else:
        # If no portfolio found in MongoDB, create one
        create_portfolio(st.session_state.user_id)
        st.session_state.portfolio = {}

# Define portfolio value update function
def update_portfolio_values():
    """Update portfolio values with current market prices"""
    total_value = 0
    for symbol, details in st.session_state.portfolio.items():
        try:
            current_price = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
            details['current_price'] = current_price
            details['value'] = details['shares'] * current_price
            details['profit_loss'] = (current_price - details['avg_price']) * details['shares']
            details['profit_loss_pct'] = (current_price / details['avg_price'] - 1) * 100
            total_value += details['value']
        except Exception as e:
            st.error(f"Error updating {symbol}: {str(e)}")
            details['current_price'] = 0
            details['value'] = 0
            details['profit_loss'] = 0
            details['profit_loss_pct'] = 0
    
    return total_value


# Main content area
with col_main:
    st.title("🚀 FinnXperts: Financial Trading System")
    
    # Create a dropdown with the ability to select multiple stocks
    available_stocks = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NFLX", "META", "NVDA", "AMD", "INTC", "PYPL", "DIS", "BA", "JPM", "V", "MA","FORD","IBP","ANF"]
    symbols = st.multiselect("Select Stock Symbols", available_stocks, default=["AAPL"])
    
    
    # Select the period for data
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("Select Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], index=4)
    with col2:
        interval = st.selectbox("Select Interval", ["1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"], index=5)
        # Ensure compatible period and interval combinations
        if (interval in ["1m", "5m", "15m", "30m", "60m"]) and (period in ["1y", "2y", "5y"]):
            st.warning("Minute-level data is only available for shorter periods. Adjusting to 1mo period.")
            period = "1mo"

    if st.button("Analyze Stocks"):
        if 'last_analyzed_symbols' not in st.session_state or st.session_state.last_analyzed_symbols != symbols:
            if 'bus' in st.session_state:
                # Clear messages
                st.session_state.bus.messages = []
                
                # Reset agent statuses
                st.session_state.market_data_agent.status = "Waiting for data request"
                st.session_state.tech_agent.status = "Ready for market analysis"
                st.session_state.risk_agent.status = "Monitoring risk levels"
                st.session_state.execution_agent.status = "Awaiting trade execution instructions"
            
            # Store the current symbols
            st.session_state.last_analyzed_symbols = symbols.copy()
        try:
            with st.spinner("Fetching market data..."):
                # Fetch market data for selected stocks
                market_data = get_market_data(symbols, period, interval)
                
                # Process data format for technical analysis
                for symbol, data in market_data.items():
                    if 'stock_data' in data and data['stock_data'] is not None:
                        # Ensure data is in the right format for technical analysis
                        data['stock_data'] = ensure_series_format(data['stock_data'])
                        # Calculate indicators for each stock
                        try:
                            data['indicators'] = calculate_all_indicators(data['stock_data'])
                        except Exception as e:
                            st.error(f"Error calculating indicators for {symbol}: {str(e)}")
                            data['indicators'] = {}

            if not market_data:
                st.error("Failed to fetch market data. Please check the stock symbols and try again.")
            else:
                # Loop through selected stocks and display information for each
                for symbol, data in market_data.items():
                    # Check if stock_data exists and is not empty
                    if 'stock_data' not in data or data['stock_data'] is None or (hasattr(data['stock_data'], 'empty') and data['stock_data'].empty):
                        st.warning(f"No data available for {symbol}. Skipping.")
                        continue

                    st.subheader(f"📊 Market Data for {symbol}")
                    
                    # Get the indicators from market data or calculate if not available
                    indicators = data.get('indicators', {})
                    if not indicators:
                        with st.spinner(f"Calculating technical indicators for {symbol}..."):
                            indicators = calculate_all_indicators(data['stock_data'])
                    
                    # Add charts before tabs for better visibility
                    try:
                        # Create price chart
                        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, 
                                            vertical_spacing=0.03, 
                                            row_heights=[1],
                                            subplot_titles=(f"{symbol} Price", "Volume"))
                        
                        # Add price candlestick
                        fig.add_trace(
                            go.Candlestick(
                                x=data['stock_data'].index,
                                open=data['stock_data']['Open'],
                                high=data['stock_data']['High'],
                                low=data['stock_data']['Low'],
                                close=data['stock_data']['Close'],
                                name="Price"
                            ),
                            row=1, col=1
                        )
                        
                        # Add MA lines if available
                        if 'SMA 50' in indicators and indicators['SMA 50'] is not None:
                            # Make sure index dates match the stock data
                            valid_data = indicators['SMA 50'].dropna()
                            if not valid_data.empty:
                                fig.add_trace(
                                    go.Scatter(
                                        x=valid_data.index,
                                        y=valid_data.values,
                                        line=dict(color='blue', width=1.5),
                                        name="SMA 50"
                                    ),
                                    row=1, col=1
                                )
                        
                        if 'SMA 200' in indicators and indicators['SMA 200'] is not None:
                            # Make sure index dates match the stock data
                            valid_data = indicators['SMA 200'].dropna()
                            if not valid_data.empty:
                                fig.add_trace(
                                    go.Scatter(
                                        x=valid_data.index,
                                        y=valid_data.values,
                                        line=dict(color='red', width=1.5),
                                        name="SMA 200"
                                    ),
                                    row=1, col=1
                                )
                        
                        
                        
                        # Customize layout
                        fig.update_layout(
                            height=600,
                            title_text=f"{symbol} Stock Analysis",
                            xaxis_rangeslider_visible=False,
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                        )
                        
                        # Set y-axes titles
                        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
                        
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error creating charts for {symbol}: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())


                    with col_news:
                        st.write(f"📰 Latest News for {symbol}")
                        display_news_blocks(symbol)

                    # Display stock data in a tab
                    tabs = st.tabs(["Price Data", "Technical Analysis", "Risk Metrics", "Recommendation"])
                    

                    with tabs[0]:  # Price Data tab
                        st.write("### Price Data Summary")
                        
                        # Calculate proper tracding days based on interval
                        if interval in ["1d", "1wk", "1mo"]:
                            # When using daily or longer intervals, each row is a trading day
                            trading_days = len(data['stock_data'])
                        else:
                            # For intraday data (minutes/hours), count unique dates
                            unique_dates = np.unique(data['stock_data'].index.date)
                            trading_days = len(unique_dates)
                        
                        # Calculate summary statistics for the entire period
                        try:
                            period_summary = {
                            'Period Start': data['stock_data'].index.min().strftime('%Y-%m-%d'),
                            'Period End': data['stock_data'].index.max().strftime('%Y-%m-%d'),
                            'Trading Days': trading_days,
                            'Open (First Day)': float(data['stock_data'].iloc[0]['Open']),  
                            'Close (Last Day)': float(data['stock_data'].iloc[-1]['Close']),  
                            'Period High': float(data['stock_data']['High'].max()),  
                            'Period Low': float(data['stock_data']['Low'].min()),  
                            'Average Price': float(data['stock_data']['Close'].mean()),  
                            'Total Volume': int(data['stock_data']['Volume'].sum()),  
                            'Price Change': float((data['stock_data'].iloc[-1]['Close'] - data['stock_data'].iloc[0]['Open'])),
                        }
                                        
                            # Calculate percentage change
                            period_summary['Price Change %'] = (period_summary['Price Change'] / period_summary['Open (First Day)']) * 100
                            
                            # Display summary in a visually appealing way
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Period", f"{period_summary['Period Start']} to {period_summary['Period End']}")
                                st.metric("Trading Days", f"{period_summary['Trading Days']}")
                                st.metric("Open (First Day)", f"${period_summary['Open (First Day)']:.2f}")
                                st.metric("Close (Last Day)", f"${period_summary['Close (Last Day)']:.2f}")
                                st.metric("Total Volume", f"{period_summary['Total Volume']:,.0f}")
                            
                            with col2:
                                st.metric("Period High", f"${period_summary['Period High']:.2f}")
                                st.metric("Period Low", f"${period_summary['Period Low']:.2f}")
                                st.metric("Average Price", f"${period_summary['Average Price']:.2f}")
                                
                                # Display price change with colored indicators
                                delta_color = "normal"
                                if period_summary['Price Change'] > 0:
                                    delta_color = "off"  # Green for positive
                                elif period_summary['Price Change'] < 0:
                                    delta_color = "inverse"  # Red for negative
                                    
                                st.metric(
                                    "Price Change", 
                                    f"${period_summary['Price Change']:.2f}", 
                                    f"{period_summary['Price Change %']:.2f}%",
                                    delta_color="normal"
                                )
                            
                            # Create a summary DataFrame for display - fixing the formatting issue
                            summary_data = {
                                'Metric': ['Period Start', 'Period End', 'Trading Days', 'Open (First Day)', 
                                        'Close (Last Day)', 'Period High', 'Period Low', 
                                        'Average Price', 'Total Volume', 'Price Change', 'Price Change %'],
                                'Value': [
                                    period_summary['Period Start'],
                                    period_summary['Period End'],
                                    str(period_summary['Trading Days']),
                                    f"${period_summary['Open (First Day)']:.2f}",
                                    f"${period_summary['Close (Last Day)']:.2f}",
                                    f"${period_summary['Period High']:.2f}",
                                    f"${period_summary['Period Low']:.2f}",
                                    f"${period_summary['Average Price']:.2f}",
                                    f"{period_summary['Total Volume']:,.0f}",
                                    f"${period_summary['Price Change']:.2f}",
                                    f"{period_summary['Price Change %']:.2f}%"
                                ]
                            }
                            
                            summary_df = pd.DataFrame(summary_data)
                            
                            st.write("### Period Summary Statistics")
                            st.dataframe(summary_df, hide_index=True)
                            
                            # Show raw data in expandable section
                            with st.expander("Show Raw Price Data"):
                                st.write("#### Complete Period Data")
                                st.dataframe(data['stock_data'])
                                
                                st.write("#### Recent Price Data (Last 5 rows)")
                                st.dataframe(data['stock_data'].tail())
                        
                        except Exception as e:
                            st.error(f"Error calculating period summary: {str(e)}")
                            st.error(f"Error details: {type(e).__name__}")
                            import traceback
                            st.error(traceback.format_exc())
                        
                        # Update the Price Overview section to use period data instead of just latest data
                        st.write("### Latest Price Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            if 'Period High' in period_summary and isinstance(period_summary['Period High'], (int, float)):
                                st.metric("Period High", f"${period_summary['Period High']:.2f}")
                            else:
                                st.metric("Period High", "N/A")
                        with col2:
                            if 'Period Low' in period_summary and isinstance(period_summary['Period Low'], (int, float)):
                                st.metric("Period Low", f"${period_summary['Period Low']:.2f}")
                            else:
                                st.metric("Period Low", "N/A")
                        with col3:
                            if 'Average Price' in period_summary and isinstance(period_summary['Average Price'], (int, float)):
                                st.metric("Period Average", f"${period_summary['Average Price']:.2f}")
                            else:
                                st.metric("Period Average", "N/A")
                        with col4:
                            if 'real_time_price' in data and data['real_time_price'] is not None and isinstance(data['real_time_price'], (int, float)):
                                st.metric("Latest Price", f"${data['real_time_price']:.2f}")
                            else:
                                st.metric("Latest Price", "N/A")
                    
                    # Technical Analysis tab - fixed the blank indicators issue
                    with tabs[1]:
                        st.write("### Technical Indicators")
                        
                        # Make sure we have indicators
                        if not indicators:
                            with st.spinner(f"Calculating technical indicators for {symbol}..."):
                                indicators = calculate_all_indicators(data['stock_data'])
                        
                        # Set up columns
                        col1, col2 = st.columns(2)
                        
                        # RSI
                        with col1:
                            st.write("#### Momentum Indicators")
                            if 'RSI' in indicators and indicators['RSI'] is not None and not (hasattr(indicators['RSI'], 'empty') and indicators['RSI'].empty):
                                try:
                                    # Get latest non-NaN RSI value
                                    rsi_series = indicators['RSI'].dropna()
                                    if len(rsi_series) > 0:
                                        rsi_value = rsi_series.iloc[-1]
                                        if isinstance(rsi_value, (int, float)):
                                            st.metric("RSI (14)", f"{rsi_value:.2f}")
                                            
                                            # Color-coded RSI
                                            if rsi_value < 30:
                                                st.success("RSI indicates oversold conditions (buying opportunity)")
                                            elif rsi_value > 70:
                                                st.warning("RSI indicates overbought conditions (selling opportunity)")
                                            else:
                                                st.info("RSI is in neutral territory")
                                    else:
                                        st.error("RSI calculation returned empty data")
                                except Exception as e:
                                    st.error(f"Error displaying RSI: {str(e)}")
                            else:
                                st.info("RSI data not available")
                        
                        # Moving Averages
                        with col2:
                            st.write("#### Moving Averages")
                            sma_values = []
                            
                            if 'SMA 50' in indicators and indicators['SMA 50'] is not None and not (hasattr(indicators['SMA 50'], 'empty') and indicators['SMA 50'].empty):
                                try:
                                    sma_series = indicators['SMA 50'].dropna()
                                    if len(sma_series) > 0:
                                        sma_value = sma_series.iloc[-1]
                                        if isinstance(sma_value, (int, float)):
                                            st.metric("SMA 50", f"${sma_value:.2f}")
                                            sma_values.append(sma_value)
                                except Exception as e:
                                    st.error(f"Error displaying SMA 50: {str(e)}")
                            
                            if 'SMA 200' in indicators and indicators['SMA 200'] is not None and not (hasattr(indicators['SMA 200'], 'empty') and indicators['SMA 200'].empty):
                                try:
                                    sma_200_series = indicators['SMA 200'].dropna()
                                    if len(sma_200_series) > 0:
                                        sma_200_value = sma_200_series.iloc[-1]
                                        if isinstance(sma_200_value, (int, float)):
                                            st.metric("SMA 200", f"${sma_200_value:.2f}")
                                            sma_values.append(sma_200_value)
                                except Exception as e:
                                    st.error(f"Error displaying SMA 200: {str(e)}")
                            
                            if 'EMA 50' in indicators and indicators['EMA 50'] is not None and not (hasattr(indicators['EMA 50'], 'empty') and indicators['EMA 50'].empty):
                                try:
                                    ema_series = indicators['EMA 50'].dropna()
                                    if len(ema_series) > 0:
                                        ema_value = ema_series.iloc[-1]
                                        if isinstance(ema_value, (int, float)):
                                            st.metric("EMA 50", f"${ema_value:.2f}")
                                except Exception as e:
                                    st.error(f"Error displaying EMA 50: {str(e)}")
                            
                            # Check for golden/death cross
                            if len(sma_values) == 2:
                                if sma_values[0] > sma_values[1]:  # SMA 50 > SMA 200
                                    st.success("Golden Cross: Bullish signal (SMA 50 > SMA 200)")
                                elif sma_values[0] < sma_values[1]:  # SMA 50 < SMA 200
                                    st.warning("Death Cross: Bearish signal (SMA 50 < SMA 200)")
                        
                        # MACD
                        st.write("#### Trend Indicators")
                        if 'MACD' in indicators and indicators['MACD'] is not None and not (hasattr(indicators['MACD'], 'empty') and indicators['MACD'].empty):
                            try:
                                macd_df = indicators['MACD']
                                
                                # Check for different column naming conventions
                                macd_col = None
                                signal_col = None
                                
                                for col in macd_df.columns:
                                    if 'MACD_' in col or col == 'MACD':
                                        macd_col = col
                                    elif 'MACDs_' in col or col == 'MACDs':
                                        signal_col = col
                                
                                if macd_col is not None and signal_col is not None:
                                    # Get latest non-NaN values
                                    macd_series = macd_df[macd_col].dropna()
                                    signal_series = macd_df[signal_col].dropna()
                                    
                                    if len(macd_series) > 0 and len(signal_series) > 0:
                                        macd_value = macd_series.iloc[-1]
                                        signal_value = signal_series.iloc[-1]
                                        
                                        if isinstance(macd_value, (int, float)) and isinstance(signal_value, (int, float)):
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.metric("MACD", f"{macd_value:.4f}")
                                            with col2:
                                                st.metric("Signal", f"{signal_value:.4f}")
                                            
                                            if macd_value > signal_value:
                                                st.success("MACD is above Signal Line (bullish)")
                                            else:
                                                st.warning("MACD is below Signal Line (bearish)")
                                    else:
                                        st.info("Insufficient data for MACD calculation")
                                else:
                                    st.info("MACD components not properly identified")
                            except Exception as e:
                                st.error(f"Error displaying MACD: {str(e)}")
                        else:
                            st.info("MACD data not available")
                        
                        # Bollinger Bands
                        st.write("#### Volatility Indicators")
                        if 'Bollinger Bands' in indicators and indicators['Bollinger Bands'] is not None and not (hasattr(indicators['Bollinger Bands'], 'empty') and indicators['Bollinger Bands'].empty):
                            try:
                                bb_df = indicators['Bollinger Bands']
                                
                                # Check for BB column patterns
                                upper_col = None
                                lower_col = None
                                for col in bb_df.columns:
                                    if 'BBU_' in col or col == 'BBU':
                                        upper_col = col
                                    elif 'BBL_' in col or col == 'BBL':
                                        lower_col = col
                                
                                if upper_col is not None and lower_col is not None:
                                    # Get latest non-NaN values
                                    upper_series = bb_df[upper_col].dropna()
                                    lower_series = bb_df[lower_col].dropna()
                                    
                                    if len(upper_series) > 0 and len(lower_series) > 0:
                                        upper_band = upper_series.iloc[-1]
                                        lower_band = lower_series.iloc[-1]
                                        
                                        if isinstance(upper_band, (int, float)) and isinstance(lower_band, (int, float)):
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.metric("Upper Band", f"${upper_band:.2f}")
                                            with col2:
                                                st.metric("Lower Band", f"${lower_band:.2f}")
                                            
                                            # Get current price for comparison
                                            current_price = data['stock_data']['Close'].iloc[-1]
                                            
                                            # Use explicit comparison rather than Series truth value
                                            if isinstance(current_price, (int, float)):
                                                if current_price > upper_band:
                                                    st.warning("Price above upper Bollinger Band (potentially overbought)")
                                                elif current_price < lower_band:
                                                    st.success("Price below lower Bollinger Band (potentially oversold)")
                                                else:
                                                    st.info("Price within Bollinger Bands (normal volatility)")
                                    else:
                                        st.info("Insufficient data for Bollinger Bands")
                                else:
                                    st.info("Bollinger Bands columns not found")
                            except Exception as e:
                                st.error(f"Error displaying Bollinger Bands: {str(e)}")
                                import traceback
                                st.error(traceback.format_exc())
                        else:
                            st.info("Bollinger Bands data not available")
                    
                    # Risk Management Metrics
                    with tabs[2]:
                        st.write("### Risk Management")
                        
                        try:
                            # Calculate risk metrics
                            risk_metrics = risk_management(data['stock_data'], account_balance=10000)
                            
                            # Display metrics in a more visual way
                            col1, col2 = st.columns(2)
                            with col1:
                                volatility = risk_metrics.get('volatility')
                                max_drawdown = risk_metrics.get('max_drawdown')
                                if volatility is not None and isinstance(volatility, (int, float)):
                                    st.metric("Volatility (Annual)", f"{volatility:.2%}")
                                    
                                    # Add volatility interpretation
                                    if volatility < 0.15:
                                        st.info("Low volatility - potentially lower risk")
                                    elif volatility > 0.30:
                                        st.warning("High volatility - potentially higher risk")
                                else:
                                    st.metric("Volatility (Annual)", "N/A")
                                    
                                if max_drawdown is not None and isinstance(max_drawdown, (int, float)):
                                    st.metric("Maximum Drawdown", f"{max_drawdown:.2%}")
                                    
                                    # Add drawdown interpretation
                                    if max_drawdown < -0.2:
                                        st.warning("Significant drawdown detected - proceed with caution")
                                else:
                                    st.metric("Maximum Drawdown", "N/A")
                            
                            with col2:
                                var = risk_metrics.get('VaR')
                                position_size = risk_metrics.get('position_size')
                                if var is not None and isinstance(var, (int, float)):
                                    st.metric("Value at Risk (95%)", f"${var:.2f}")
                                    st.info("Maximum expected loss at 95% confidence level")
                                else:
                                    st.metric("Value at Risk (95%)", "N/A")
                                    
                                if position_size is not None and isinstance(position_size, (int, float)):
                                    st.metric("Recommended Position Size", f"{int(position_size)} shares")
                                    
                                    # Add current price for reference
                                    if 'real_time_price' in data and data['real_time_price'] is not None:
                                        investment_amount = int(position_size) * data['real_time_price']
                                        st.info(f"Approximate investment: ${investment_amount:.2f}")
                                else:
                                    st.metric("Recommended Position Size", "N/A")
                            
                            # Add risk metrics to indicators for recommendation
                            indicators.update(risk_metrics)
                            
                        except Exception as e:
                            st.error(f"Risk management calculations failed for {symbol}: {str(e)}")
                    
                    
                    # Generate and display recommendation
                    
                    with tabs[3]:
                        st.write("### Trading Recommendation")
                        
                        try:
                            # Generate recommendation based on indicators, risk, and AI analysis
                            # Use stock_data if historical_data is not available
                            price_data = data.get('historical_data', data.get('stock_data'))
                            
                            # Add a check to make sure we have enough data for meaningful analysis
                            if indicators and len(indicators) > 0:
                                recommendation_result = generate_recommendation(indicators, symbol, price_data)
                                recommendation = recommendation_result.get('action', 'Hold')
                                
                                # Display recommendation with visual cue and better styling
                                if recommendation == "Buy":
                                    st.success(f"### Recommendation: BUY {symbol}")
                                    recommend_icon = "📈"
                                elif recommendation == "Sell":
                                    st.warning(f"### Recommendation: SELL {symbol}")
                                    recommend_icon = "📉"
                                else:
                                    st.info(f"### Recommendation: HOLD {symbol}")
                                    recommend_icon = "⏸️"
                                
                                # Create a more appealing display with columns
                                col1, col2 = st.columns([1, 3])
                                
                                
                                
                                # Technical analysis reasoning in expandable section
                                with st.expander("Technical Analysis Details", expanded=True):
                                    tech_reasons = recommendation_result.get('technical_analysis', recommendation_result.get('reasons', []))
                                    
                                    if tech_reasons and len(tech_reasons) > 0:
                                        for reason in tech_reasons:
                                            st.write(f"- {reason}")
                                    else:
                                        st.write("- Based on the technical indicators, including moving averages, RSI, and price trends")
                                        st.write("- Current market conditions suggest this position")
                                        st.write("- Volume patterns support this recommendation")
                                
                                # AI insights section
                                with st.expander("AI Analysis Details", expanded=True):
                                    if 'ai_insights' in recommendation_result and recommendation_result['ai_insights'] and len(recommendation_result['ai_insights']) > 0:
                                        ai_insights = recommendation_result['ai_insights']
                                        for insight in ai_insights:
                                            st.write(f"- {insight}")
                                    else:
                                        st.write("- AI analysis requires more historical data for this security")
                                        st.write("- Consider the technical indicators and your risk tolerance")
                                        st.write("- For more detailed AI insights, try analyzing longer time periods")
                                
                                # Risk assessment section
                                with st.expander("Risk Assessment"):
                                    st.write("#### Risk Factors to Consider:")
                                    
                                    if 'risk_factors' in recommendation_result and recommendation_result['risk_factors']:
                                        risk_factors = recommendation_result['risk_factors']
                                        for factor in risk_factors:
                                            st.write(f"- {factor}")
                                    else:
                                        # Default risk factors based on common considerations
                                        st.write("- Market volatility may affect short-term performance")
                                        st.write("- Always consider your personal risk tolerance before trading")
                                        if 'volatility' in indicators and indicators['volatility'] is not None:
                                            volatility = indicators['volatility']
                                            st.write(f"- The current volatility of {volatility:.2%} indicates " + 
                                                    ("high risk" if volatility > 0.25 else "moderate risk" if volatility > 0.15 else "lower risk"))
                                
                                # Action steps
                                st.write("### Suggested Actions:")
                                if recommendation == "Buy":
                                    st.write("1. Consider your current portfolio allocation")
                                    st.write("2. Determine appropriate position size based on risk management")
                                    st.write("3. Consider setting stop-loss orders at key support levels")
                                elif recommendation == "Sell":
                                    st.write("1. Evaluate tax implications before selling")
                                    st.write("2. Consider partial selling to lock in profits")
                                    st.write("3. Look for re-entry points if long-term outlook remains positive")
                                else:  # Hold
                                    st.write("1. Monitor key support and resistance levels")
                                    st.write("2. Watch for changes in volume or momentum")
                                    st.write("3. Consider setting price alerts for significant movements")
                            else:
                                st.warning("Insufficient technical indicator data for a complete recommendation.")
                                st.write("Try selecting a longer time period or a different interval to generate more reliable technical indicators.")
                                st.info("Based on the limited data available, no strong buy or sell signals are present. HOLD position is recommended by default.")
                                
                        except Exception as e:
                            st.error(f"Error generating recommendation for {symbol}: {str(e)}")
                            st.info("Unable to generate recommendation. Consider the technical indicators shown in the previous tab instead.")
                            import traceback
                            st.error(traceback.format_exc())

                    # Add a separator between stocks
                    st.markdown("---")
            # Initialize agents if not already in session state
                if 'bus' not in st.session_state:
                    bus = AgentCommunicationBus()
                    market_data_agent = MarketDataAgent(bus)
                    tech_agent = TechnicalAnalysisAgent(bus)
                    risk_agent = RiskManagementAgent(bus)
                    execution_agent = ExecutionAgent(bus)
                    
                    st.session_state.bus = bus
                    st.session_state.market_data_agent = market_data_agent
                    st.session_state.tech_agent = tech_agent
                    st.session_state.risk_agent = risk_agent
                    st.session_state.execution_agent = execution_agent
                else:
                    bus = st.session_state.bus
                    market_data_agent = st.session_state.market_data_agent
                    tech_agent = st.session_state.tech_agent
                    risk_agent = st.session_state.risk_agent
                    execution_agent = st.session_state.execution_agent

                # After successful analysis, update agent statuses and add messages
                if not st.session_state.bus.messages:  # Only add if no messages yet
                    # First, add messages for the overall process
                    market_data_agent.send_message(
                        "TechnicalAnalysisAgent", 
                        "data_ready", 
                        f"Market data ready for {', '.join(symbols)}"
                    )
                    
                    tech_agent.send_message(
                        "RiskManagementAgent", 
                        "analysis_complete", 
                        f"Technical indicators calculated for all symbols"
                    )
                    
                    risk_agent.send_message(
                        "ExecutionAgent", 
                        "risk_ready", 
                        f"Risk metrics calculated for all symbols"
                    )
                    
                    # Then show status updates for all symbols that were analyzed
                    analyzed_symbols = []
                    for symbol in symbols:
                        if symbol in market_data and 'stock_data' in market_data[symbol]:
                            analyzed_symbols.append(symbol)
                    
                    if analyzed_symbols:
                        # Update final status to show all symbols that were successfully analyzed
                        market_data_agent.update_status(f"Data collection complete for {', '.join(analyzed_symbols)}")
                        tech_agent.update_status(f"Technical analysis complete for {', '.join(analyzed_symbols)}")
                        risk_agent.update_status(f"Risk assessment complete for {', '.join(analyzed_symbols)}")
                        execution_agent.update_status(f"Recommendations generated for {', '.join(analyzed_symbols)}")
                        
                        # Send final summary message
                        execution_agent.send_message(
                            "all", 
                            "recommendations_ready", 
                            f"Trading recommendations ready for {', '.join(analyzed_symbols)}: {recommendation}"
                        )
                    
                    # Demonstrate agent correction based on risk feedback
                    risk_feedback_shown = False
                    for symbol in symbols:
                        if symbol in market_data and 'indicators' in market_data[symbol]:
                            indicators = market_data[symbol]['indicators']
                            # Check for high risk level
                            if 'risk_level' in indicators and indicators['risk_level'] in ["Very High"]:
                                risk_agent.send_message(
                                    "ExecutionAgent",
                                    "risk_warning",
                                    f"Warning: {indicators['risk_level']} risk detected for {symbol}, consider adjusting recommendation"
                                )
                                execution_agent.update_status(f"Adjusting recommendation based on risk feedback for {symbol}")
                                execution_agent.send_message(
                                    "all",
                                    "recommendation_adjusted",
                                    f"Adjusted recommendation for {symbol}: HOLD due to very high risk."
                                )
                                risk_feedback_shown = True
                                break  # Just do one example for demonstration
                    
                    # If no high risk found, still show an interaction for demonstration
                    if not risk_feedback_shown and analyzed_symbols:
                        example_symbol = analyzed_symbols[0]
                        risk_agent.send_message(
                            "ExecutionAgent",
                            "risk_confirmation",
                            f"Risk levels acceptable for {example_symbol}, no adjustment needed"
                        )
                        execution_agent.send_message(
                            "all",
                            "recommendation_confirmed",
                            f"Confirmed recommendation for {example_symbol} without changes"
                        )

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")


# Agent Status Section
st.sidebar.markdown("## 🤖 Agent Status")

# Get agents from session state if available
market_data_agent = st.session_state.get('market_data_agent', None)
tech_agent = st.session_state.get('tech_agent', None)
risk_agent = st.session_state.get('risk_agent', None)
execution_agent = st.session_state.get('execution_agent', None)

# Display each agent status if available
if market_data_agent:
    st.sidebar.markdown("### 📊 MarketDataAgent")
    if "complete" in market_data_agent.status.lower():
        st.sidebar.success(market_data_agent.status)
    else:
        st.sidebar.info(market_data_agent.status)
    st.sidebar.caption(f"Last updated: {market_data_agent.latest_update}")

if tech_agent:
    st.sidebar.markdown("### 🧠 TechnicalAnalysisAgent")
    if "complete" in tech_agent.status.lower():
        st.sidebar.success(tech_agent.status)
    else:
        st.sidebar.info(tech_agent.status)
    st.sidebar.caption(f"Last updated: {tech_agent.latest_update}")

if risk_agent:
    st.sidebar.markdown("### 🛡️ RiskManagementAgent")
    if "complete" in risk_agent.status.lower():
        st.sidebar.success(risk_agent.status)
    else:
        st.sidebar.info(risk_agent.status)
    st.sidebar.caption(f"Last updated: {risk_agent.latest_update}")

if execution_agent:
    st.sidebar.markdown("### 💼 ExecutionAgent")
    if "complete" in execution_agent.status.lower():
        st.sidebar.success(execution_agent.status)
    else:
        st.sidebar.info(execution_agent.status)
    st.sidebar.caption(f"Last updated: {execution_agent.latest_update}")

# Agent Communication display with better styling
st.sidebar.markdown("## 🔌 Inter-Agent Communication")

# Get bus from session state if available
bus = st.session_state.get('bus', None)
if bus and hasattr(bus, 'messages'):
    messages = bus.messages
    if messages:
        # Sort messages by timestamp (assuming messages have timestamps)
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', '00:00:00'))
        
        # Display messages in a more visually appealing way
        for i, msg in enumerate(sorted_messages[-5:]):  # Show last 5 messages
            sender = msg.get('sender', 'Unknown')
            recipient = msg.get('recipient', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', 'Unknown time')
            
            # Choose color based on sender
            if "Market" in sender:
                emoji = "📊"
                color = "#4CAF50"  # Green
            elif "Technical" in sender:
                emoji = "🧠"
                color = "#2196F3"  # Blue
            elif "Risk" in sender:
                emoji = "🛡️"
                color = "#FF9800"  # Orange
            elif "Execution" in sender:
                emoji = "💼"
                color = "#9C27B0"  # Purple
            else:
                emoji = "🤖"
                color = "#607D8B"  # Gray
            
            # Create a styled message card
            st.sidebar.markdown(f"""
            <div style="
                border-left: 3px solid {color};
                padding-left: 10px;
                margin-bottom: 8px;
                background-color: rgba(0,0,0,0.05);
                border-radius: 4px;
                padding: 8px;">
                <div style="font-size: 0.9em; margin-bottom: 4px;">
                    <span style="color: {color};">{emoji} {sender}</span> → {recipient}
                </div>
                <div style="font-size: 0.8em; margin-bottom: 4px;">
                    {content}
                </div>
                <div style="font-size: 0.7em; opacity: 0.7;">
                    {timestamp}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.info("No messages in the queue.")
else:
    st.sidebar.info("No agent communication available.")
   
# minimizable_trading_chatbot() 
