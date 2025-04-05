# recommendation.py
import pandas as pd

def generate_recommendation(indicators):
    """
    Generate a recommendation based on technical analysis indicators and risk management metrics.
    :param indicators: Dictionary containing technical indicators and risk metrics
    :return: Buy, Sell, or Hold recommendation with explanation
    """
    try:
        # Initialize with default recommendation
        recommendation = "Hold"
        reasons = []
        
        # Extract indicator values if they exist and are not None
        # RSI check
        if ('RSI' in indicators and indicators['RSI'] is not None and 
            not (hasattr(indicators['RSI'], 'empty') and indicators['RSI'].empty)):
            try:
                rsi = indicators['RSI'].iloc[-1]
                if not pd.isna(rsi) and isinstance(rsi, (int, float)):
                    if rsi < 30:
                        recommendation = "Buy"
                        reasons.append(f"RSI is oversold ({rsi:.2f} < 30)")
                    elif rsi > 70:
                        recommendation = "Sell"
                        reasons.append(f"RSI is overbought ({rsi:.2f} > 70)")
            except Exception as e:
                print(f"RSI evaluation error: {str(e)}")
        
        # Moving average checks - SMA 50/200 for golden/death cross
        if ('SMA 50' in indicators and 'SMA 200' in indicators and 
            indicators['SMA 50'] is not None and indicators['SMA 200'] is not None and
            not (hasattr(indicators['SMA 50'], 'empty') and indicators['SMA 50'].empty) and 
            not (hasattr(indicators['SMA 200'], 'empty') and indicators['SMA 200'].empty)):
            
            try:
                sma_50_last = indicators['SMA 50'].iloc[-1] if not pd.isna(indicators['SMA 50'].iloc[-1]) else None
                sma_200_last = indicators['SMA 200'].iloc[-1] if not pd.isna(indicators['SMA 200'].iloc[-1]) else None
                
                if sma_50_last is not None and sma_200_last is not None:
                    if sma_50_last > sma_200_last:
                        if recommendation != "Sell":  # Don't override a stronger sell signal
                            recommendation = "Buy"
                        reasons.append(f"Golden Cross: SMA 50 ({sma_50_last:.2f}) > SMA 200 ({sma_200_last:.2f})")
                    elif sma_50_last < sma_200_last:
                        if recommendation != "Buy":  # Don't override a stronger buy signal
                            recommendation = "Sell"
                        reasons.append(f"Death Cross: SMA 50 ({sma_50_last:.2f}) < SMA 200 ({sma_200_last:.2f})")
            except Exception as e:
                print(f"SMA evaluation error: {str(e)}")
        
        # EMA 50 vs SMA 50 check
        if ('EMA 50' in indicators and 'SMA 50' in indicators and 
            indicators['EMA 50'] is not None and indicators['SMA 50'] is not None and
            not (hasattr(indicators['EMA 50'], 'empty') and indicators['EMA 50'].empty) and 
            not (hasattr(indicators['SMA 50'], 'empty') and indicators['SMA 50'].empty)):
            
            try:
                ema_50_last = indicators['EMA 50'].iloc[-1] if not pd.isna(indicators['EMA 50'].iloc[-1]) else None
                sma_50_last = indicators['SMA 50'].iloc[-1] if not pd.isna(indicators['SMA 50'].iloc[-1]) else None
                
                if ema_50_last is not None and sma_50_last is not None:
                    if ema_50_last > sma_50_last:
                        if recommendation != "Sell":
                            recommendation = "Buy"
                        reasons.append(f"EMA 50 ({ema_50_last:.2f}) > SMA 50 ({sma_50_last:.2f})")
                    elif ema_50_last < sma_50_last:
                        if recommendation != "Buy":
                            recommendation = "Sell"
                        reasons.append(f"EMA 50 ({ema_50_last:.2f}) < SMA 50 ({sma_50_last:.2f})")
            except Exception as e:
                print(f"EMA evaluation error: {str(e)}")
        
        # MACD check
        if ('MACD' in indicators and indicators['MACD'] is not None and 
            not (hasattr(indicators['MACD'], 'empty') and indicators['MACD'].empty)):
            try:
                macd_df = indicators['MACD']
                
                # Check both possible column naming conventions
                macd_col = None
                signal_col = None
                
                if 'MACD_12_26_9' in macd_df.columns:
                    macd_col = 'MACD_12_26_9'
                elif 'MACD' in macd_df.columns:
                    macd_col = 'MACD'
                
                if 'MACDs_12_26_9' in macd_df.columns:
                    signal_col = 'MACDs_12_26_9'
                elif 'MACDs' in macd_df.columns:
                    signal_col = 'MACDs'
                    
                if macd_col and signal_col:
                    macd_val = macd_df[macd_col].iloc[-1] if not pd.isna(macd_df[macd_col].iloc[-1]) else None
                    macd_signal = macd_df[signal_col].iloc[-1] if not pd.isna(macd_df[signal_col].iloc[-1]) else None
                    
                    if macd_val is not None and macd_signal is not None:
                        if macd_val > macd_signal:
                            if recommendation != "Sell":
                                recommendation = "Buy"
                            reasons.append(f"MACD ({macd_val:.4f}) > Signal ({macd_signal:.4f})")
                        elif macd_val < macd_signal:
                            if recommendation != "Buy":
                                recommendation = "Sell"
                            reasons.append(f"MACD ({macd_val:.4f}) < Signal ({macd_signal:.4f})")
            except Exception as e:
                print(f"MACD evaluation error: {str(e)}")
        
        # Risk management considerations (if present in indicators)
        volatility = indicators.get('volatility')
        max_drawdown = indicators.get('max_drawdown')
        
        if volatility is not None and isinstance(volatility, (int, float)) and volatility > 0.25:  # High volatility
            if recommendation == "Buy":
                recommendation = "Hold"
                reasons.append(f"High volatility ({volatility:.2%}) suggests caution")
        
        if max_drawdown is not None and isinstance(max_drawdown, (int, float)) and max_drawdown < -0.2:  # Significant drawdown
            if recommendation == "Buy":
                recommendation = "Hold"
                reasons.append(f"Significant drawdown ({max_drawdown:.2%}) suggests caution")
        
        # If no specific signals were found
        if not reasons:
            reasons.append("Technical indicators are neutral")
        
        # Combine recommendation with reasons
        recommendation_with_reasons = {
            "action": recommendation,
            "reasons": reasons
        }
        
        return recommendation_with_reasons
        
    except Exception as e:
        print(f"Error generating recommendation: {str(e)}")
        return {
            "action": "Hold",
            "reasons": ["Error in recommendation generation"]
        }