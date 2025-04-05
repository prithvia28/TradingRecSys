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
from analysis import calculate_all_indicators
from recommendation import generate_recommendation
from risk_management import risk_management
from news_updates import display_news_blocks

# Page configuration
st.set_page_config(layout="wide", page_title="Trading Recommendation System")

# Create a two-column layout with portfolio on the right
col_main, col_portfolio = st.columns([3, 1])

# Initialize session state for portfolio if it doesn't exist
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        'AAPL': {'shares': 10, 'avg_price': 170.50, 'value': 0},
        'MSFT': {'shares': 5, 'avg_price': 325.20, 'value': 0},
        'GOOG': {'shares': 3, 'avg_price': 145.75, 'value': 0}
    }


# Define portfolio management functions
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
            st.sidebar.error(f"Error updating {symbol}: {str(e)}")
            details['current_price'] = 0
            details['value'] = 0
            details['profit_loss'] = 0
            details['profit_loss_pct'] = 0
    
    return total_value

# Main content area
with col_main:
    st.title("🚀 Trading Recommendation System")
    
    # Create a dropdown with the ability to select multiple stocks
    available_stocks = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NFLX", "META", "NVDA", "AMD", "INTC", "PYPL", "DIS", "BA", "JPM", "V", "MA","FORD"]
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
        try:
            with st.spinner("Fetching market data..."):
                # Fetch market data for selected stocks
                market_data = get_market_data(symbols, period, interval)
                

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
                    
                    # Add charts before tabs for better visibility
                    try:
                        # Calculate indicators first - this is important to have indicators ready for charts
                        indicators = calculate_all_indicators(data['stock_data'])
                        
                        # Create price chart
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                            vertical_spacing=0.03, 
                                            row_heights=[0.7, 0.3],
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
                        
                        # Add volume bar chart
                        fig.add_trace(
                            go.Bar(
                                x=data['stock_data'].index,
                                y=data['stock_data']['Volume'],
                                marker_color='rgba(0, 150, 255, 0.6)',
                                name="Volume"
                            ),
                            row=2, col=1
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
                        fig.update_yaxes(title_text="Volume", row=2, col=1)
                        
                        # st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error creating charts for {symbol}: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())


                    with col_portfolio:
                        st.write(f"📰 Latest News for {symbol}")
                        display_news_blocks(symbol)

                    # Display stock data in a tab
                    tabs = st.tabs(["Price Data", "Technical Analysis", "Risk Metrics", "Recommendation"])
                    

                    with tabs[0]:  # Price Data tab
                        st.write("### Price Data Summary")
                        
                        # Calculate proper trading days based on interval
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
                            'Open (First Day)': float(data['stock_data'].iloc[0]['Open'].iloc[0]),  
                            'Close (Last Day)': float(data['stock_data'].iloc[-1]['Close'].iloc[0]),  
                            'Period High': float(data['stock_data']['High'].max().iloc[0]),  
                            'Period Low': float(data['stock_data']['Low'].min().iloc[0]),  
                            'Average Price': float(data['stock_data']['Close'].mean().iloc[0]),  
                            'Total Volume': int(data['stock_data']['Volume'].sum().iloc[0]),  
                            'Price Change': float((data['stock_data'].iloc[-1]['Close'].iloc[0] - data['stock_data'].iloc[0]['Open'].iloc[0])),
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
                                    if not rsi_series.empty:
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
                                st.error("RSI data not available")
                        
                        # Moving Averages
                        with col2:
                            st.write("#### Moving Averages")
                            sma_values = []
                            
                            if 'SMA 50' in indicators and indicators['SMA 50'] is not None and not (hasattr(indicators['SMA 50'], 'empty') and indicators['SMA 50'].empty):
                                try:
                                    sma_series = indicators['SMA 50'].dropna()
                                    if not sma_series.empty:
                                        sma_value = sma_series.iloc[-1]
                                        if isinstance(sma_value, (int, float)):
                                            st.metric("SMA 50", f"${sma_value:.2f}")
                                            sma_values.append(sma_value)
                                except Exception as e:
                                    st.error(f"Error displaying SMA 50: {str(e)}")
                            
                            if 'SMA 200' in indicators and indicators['SMA 200'] is not None and not (hasattr(indicators['SMA 200'], 'empty') and indicators['SMA 200'].empty):
                                try:
                                    sma_200_series = indicators['SMA 200'].dropna()
                                    if not sma_200_series.empty:
                                        sma_200_value = sma_200_series.iloc[-1]
                                        if isinstance(sma_200_value, (int, float)):
                                            st.metric("SMA 200", f"${sma_200_value:.2f}")
                                            sma_values.append(sma_200_value)
                                except Exception as e:
                                    st.error(f"Error displaying SMA 200: {str(e)}")
                            
                            if 'EMA 50' in indicators and indicators['EMA 50'] is not None and not (hasattr(indicators['EMA 50'], 'empty') and indicators['EMA 50'].empty):
                                try:
                                    ema_series = indicators['EMA 50'].dropna()
                                    if not ema_series.empty:
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
                                
                                if macd_col and signal_col:
                                    # Get latest non-NaN values
                                    last_idx = macd_df.apply(pd.Series.last_valid_index)
                                    if last_idx[macd_col] and last_idx[signal_col]:
                                        macd_value = macd_df[macd_col].loc[last_idx[macd_col]]
                                        signal_value = macd_df[signal_col].loc[last_idx[signal_col]]
                                        
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
                                        st.error("MACD calculation returned incomplete data")
                                else:
                                    st.error("MACD components not properly identified")
                            except Exception as e:
                                st.error(f"Error displaying MACD: {str(e)}")
                        else:
                            st.error("MACD data not available")
                        
                        # Bollinger Bands
                        st.write("#### Volatility Indicators")
                        if 'Bollinger Bands' in indicators and indicators['Bollinger Bands'] is not None and not (hasattr(indicators['Bollinger Bands'], 'empty') and indicators['Bollinger Bands'].empty):
                            try:
                                bb_df = indicators['Bollinger Bands']
                                
                                # Check for BB column patterns
                                upper_col = next((col for col in bb_df.columns if 'BBU_' in col or col == 'BBU'), None)
                                lower_col = next((col for col in bb_df.columns if 'BBL_' in col or col == 'BBL'), None)
                                middle_col = next((col for col in bb_df.columns if 'BBM_' in col or col == 'BBM'), None)
                                
                                if upper_col and lower_col:
                                    # Get latest non-NaN values
                                    last_idx = bb_df.apply(pd.Series.last_valid_index)
                                    
                                    if last_idx[upper_col] and last_idx[lower_col]:
                                        upper_band = bb_df[upper_col].loc[last_idx[upper_col]]
                                        lower_band = bb_df[lower_col].loc[last_idx[lower_col]]
                                        
                                        if isinstance(upper_band, (int, float)) and isinstance(lower_band, (int, float)):
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.metric("Upper Band", f"${upper_band:.2f}")
                                            with col2:
                                                st.metric("Lower Band", f"${lower_band:.2f}")
                                            
                                            # Get current price for comparison
                                            current_price = data['stock_data']['Close'].iloc[-1]
                                            
                                            if current_price > upper_band:
                                                st.warning("Price above upper Bollinger Band (potentially overbought)")
                                            elif current_price < lower_band:
                                                st.success("Price below lower Bollinger Band (potentially oversold)")
                                            else:
                                                st.info("Price within Bollinger Bands (normal volatility)")
                                    else:
                                        st.error("Bollinger Bands calculation returned incomplete data")
                                else:
                                    st.error("Bollinger Bands components not properly identified")
                            except Exception as e:
                                st.error(f"Error displaying Bollinger Bands: {str(e)}")
                        else:
                            st.error("Bollinger Bands data not available")
                    
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
                            # Pass in the symbol and price data for OpenAI enhancement
                            price_data = data.get('historical_data') if 'historical_data' in data else None
                            recommendation_result = generate_recommendation(indicators, symbol, price_data)
                            recommendation = recommendation_result.get('action', 'Hold')
                            
                            # Display recommendation with visual cue
                            if recommendation == "Buy":
                                st.success(f"**Recommendation: BUY {symbol}**")
                            elif recommendation == "Sell":
                                st.warning(f"**Recommendation: SELL {symbol}**")
                            else:
                                st.info(f"**Recommendation: HOLD {symbol}**")
                            
                            # Display confidence score if available
                            if 'confidence_score' in recommendation_result and recommendation_result['confidence_score'] is not None:
                                confidence = recommendation_result['confidence_score']
                                st.write(f"**Confidence Score:** {confidence:.2f}")
                                # Visual confidence meter
                                st.progress(confidence)
                            
                            # Technical analysis reasoning
                            st.write("#### Technical Analysis:")
                            tech_reasons = recommendation_result.get('technical_analysis', recommendation_result.get('reasons', ['No technical analysis provided']))
                            for reason in tech_reasons:
                                st.write(f"- {reason}")
                            
                            # AI insights section
                            if 'ai_insights' in recommendation_result:
                                st.write("#### AI Insights:")
                                ai_insights = recommendation_result['ai_insights']
                                for insight in ai_insights:
                                    st.write(f"- {insight}")
                            
                            
                            
                        except Exception as e:
                            st.error(f"Error generating recommendation for {symbol}: {str(e)}")
                    
                    # Add a separator between stocks
                    st.markdown("---")

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

# Portfolio panel on the right side
with col_portfolio:
    st.sidebar.title("📈 Portfolio")
    
    # Update portfolio values
    total_value = update_portfolio_values()
    
    # Display total portfolio value
    st.sidebar.metric("Total Portfolio Value", f"${total_value:.2f}")
    
    # Display individual stocks in portfolio
    st.sidebar.markdown("### Holdings")
    
    for symbol, details in st.session_state.portfolio.items():
        if details['shares'] > 0:  # Only show stocks with shares
            with st.sidebar.expander(f"{symbol} - {details['shares']} shares"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Avg Price: ${details['avg_price']:.2f}")
                with col2:
                    if 'current_price' in details and details['current_price'] > 0:
                        st.write(f"Current: ${details['current_price']:.2f}")
                
                # Show profit/loss
                if 'profit_loss' in details:
                    profit_text = f"P/L: ${details['profit_loss']:.2f} ({details['profit_loss_pct']:.2f}%)"
                    if details['profit_loss'] > 0:
                        st.success(profit_text)
                    elif details['profit_loss'] < 0:
                        st.error(profit_text)
                    else:
                        st.info(profit_text)
                
                # Value
                st.write(f"Value: ${details['value']:.2f}")
    
    