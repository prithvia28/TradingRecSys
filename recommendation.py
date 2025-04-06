import pandas as pd
import json
import requests
from datetime import datetime
import os
import openai
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


def generate_recommendation(indicators, symbol=None, price_data=None):
    """
    Generate a recommendation based on technical analysis indicators, risk management metrics,
    and AI-enhanced analysis.
    
    :param indicators: Dictionary containing technical indicators and risk metrics
    :param symbol: Stock/crypto symbol being analyzed
    :param price_data: Recent price data for additional context
    :return: Enhanced recommendation with technical analysis and AI insights
    """
    try:
        # Generate traditional technical analysis recommendation
        tech_recommendation = generate_technical_recommendation(indicators)
        
        # If symbol and price_data are provided, enhance with AI recommendation
        if symbol and price_data is not None:
            ai_recommendation = generate_ai_recommendation(
                symbol, 
                price_data, 
                indicators, 
                tech_recommendation
            )
            
            # Combine technical and AI recommendations
            final_recommendation = {
                "action": ai_recommendation["action"],
                "technical_analysis": tech_recommendation["reasons"],
                "ai_insights": ai_recommendation["insights"],
                "confidence_score": ai_recommendation["confidence_score"]
            }
        else:
            # Fall back to technical recommendation if data for AI is missing
            final_recommendation = {
                "action": tech_recommendation["action"],
                "technical_analysis": tech_recommendation["reasons"],
                "ai_insights": ["AI analysis unavailable - insufficient data"],
                "confidence_score": None
            }
        
        return final_recommendation
        
    except Exception as e:
        print(f"Error generating recommendation: {str(e)}")
        return {
            "action": "Hold",
            "technical_analysis": ["Error in recommendation generation"],
            "ai_insights": ["Error in AI analysis"],
            "confidence_score": None
        }

def generate_technical_recommendation(indicators):
    """
    Generate recommendation based purely on technical indicators
    """
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

def generate_ai_recommendation(symbol, price_data, indicators, tech_recommendation):
    """
    Generate an AI-enhanced recommendation using a free API
    
    :param symbol: Stock/crypto symbol being analyzed
    :param price_data: Recent price data
    :param indicators: Dictionary containing technical indicators
    :param tech_recommendation: Result from technical analysis
    :return: AI-enhanced recommendation
    """
    try:
        # Option 1: Using Google's Gemini API (free tier available)
        # Uncomment and use this section if you prefer Gemini
        return generate_gemini_recommendation(symbol, price_data, indicators, tech_recommendation)
        
        # Option 2: Using OpenAI's API (requires API key but has free credits)
        #return generate_openai_recommendation(symbol, price_data, indicators, tech_recommendation)
        
    except Exception as e:
        print(f"Error in AI recommendation: {str(e)}")
        # Fall back to technical recommendation if AI fails
        return {
            "action": tech_recommendation["action"],
            "insights": ["AI analysis failed, relying on technical indicators only"],
            "confidence_score": 0.5  # Neutral confidence score
        }

def generate_gemini_recommendation(symbol, price_data, indicators, tech_recommendation):
    """
    Use Google's Gemini API to generate enhanced trading recommendations
    """
    try:
        # Get Gemini API key from environment variable (more secure)
        api_key = os.environ.get('GOOGLE_API_KEY', '')
        
        if not api_key:
            return {
                "action": tech_recommendation["action"],
                "insights": ["Gemini API key not configured"],
                "confidence_score": 0.5
            }
        
        # Prepare data for the API request
        # Extract recent price trends (last 5 data points)
        recent_prices = price_data.tail(5).to_dict('records') if price_data is not None else []
        
        # Extract key indicators for the prompt
        key_indicators = {}
        for indicator_name in ['RSI', 'MACD', 'SMA 50', 'SMA 200', 'EMA 50']:
            if indicator_name in indicators and indicators[indicator_name] is not None:
                try:
                    # Safely extract the last value, handling both Series and other types
                    if hasattr(indicators[indicator_name], 'iloc'):
                        # For Series, get the last non-NaN value
                        indicator_series = indicators[indicator_name].dropna()
                        if not indicator_series.empty:
                            value = float(indicator_series.iloc[-1])
                        else:
                            value = "N/A"
                    else:
                        # If it's not a Series, convert directly
                        value = float(indicators[indicator_name])
                    
                    key_indicators[indicator_name] = value
                except (TypeError, ValueError, pd.errors.IntCastingNaNError):
                    # If conversion fails, skip or use "N/A"
                    key_indicators[indicator_name] = "N/A"
        
        # Add risk metrics
        for metric in ['volatility', 'max_drawdown']:
            if metric in indicators:
                try:
                    # Safely convert to float
                    if hasattr(indicators[metric], 'iloc'):
                        # For Series, get the last non-NaN value
                        metric_series = indicators[metric].dropna()
                        if not metric_series.empty:
                            value = float(metric_series.iloc[-1])
                        else:
                            value = "N/A"
                    else:
                        # If it's not a Series, convert directly
                        value = float(indicators[metric])
                    
                    key_indicators[metric] = value
                except (TypeError, ValueError, pd.errors.IntCastingNaNError):
                    # If conversion fails, skip or use "N/A"
                    key_indicators[metric] = "N/A"
        
        # Create prompt for Gemini
        prompt = f"""
        Analyze the trading data for {symbol} and provide a recommendation.
        
        Technical indicators:
        {json.dumps(key_indicators, indent=2)}
        
        Recent price action:
        {json.dumps(recent_prices, indent=2)}
        
        Technical analysis recommendation: {tech_recommendation['action']}
        Technical reasons: {', '.join(tech_recommendation['reasons'])}
        
        Based on this data, provide:
        1. A recommendation (Buy, Sell, or Hold)
        2. 2-3 key insights about this asset based on the data
        3. A confidence score between 0 (low confidence) and 1 (high confidence)
        
        Format your response as JSON with keys: action, insights (array), confidence_score
        """
        
        # Gemini API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-001:generateContent"
        
        # Prepare the request
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        # Parse the AI response
        if response.status_code == 200 and 'candidates' in response_data:
            ai_text_response = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from the response
            try:
                # Handle potential formatting issues in the AI response
                ai_json_str = ai_text_response.strip()
                if "```json" in ai_json_str:
                    ai_json_str = ai_json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_json_str:
                    ai_json_str = ai_json_str.split("```")[1].strip()
                
                ai_recommendation = json.loads(ai_json_str)
                
                # Ensure all required keys are present
                if not all(key in ai_recommendation for key in ['action', 'insights', 'confidence_score']):
                    raise ValueError("Missing required fields in AI response")
                
                # Additional validation
                if ai_recommendation['action'] not in ['Buy', 'Sell', 'Hold']:
                    ai_recommendation['action'] = tech_recommendation['action']
                
                return ai_recommendation
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw AI response: {ai_text_response}")
                # Fall back to technical analysis if JSON parsing fails
                return {
                    "action": tech_recommendation["action"],
                    "insights": ["AI analysis could not be parsed correctly"],
                    "confidence_score": 0.5
                }
        else:
            print(f"API Error: {response.status_code}")
            print(response_data)
            return {
                "action": tech_recommendation["action"],
                "insights": ["API error occurred during AI analysis"],
                "confidence_score": 0.5
            }
            
    except Exception as e:
        print(f"Gemini recommendation error: {str(e)}")
        return {
            "action": tech_recommendation["action"],
            "insights": ["Error in AI recommendation process"],
            "confidence_score": 0.5
        }
