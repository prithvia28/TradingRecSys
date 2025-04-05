# # Use your actual API key here
# FINNHUB_API_KEY = "cvocq01r01qppf5cab4gcvcocq01r01qppf5cab50"
import requests
import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf


# Use your actual API key here
FINNHUB_API_KEY = "cvonf2hr01qihjtpq20gcvonf2hr01qihjtpq210"
# Function to fetch stock-related news from Finnhub
def fetch_stock_news(symbol):
    today = datetime.today().date()
    week_ago = today - timedelta(days=7)

    url = (
        f"https://finnhub.io/api/v1/company-news"
        f"?symbol={symbol}&from={week_ago}&to={today}&token={FINNHUB_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        if not news_data:
            st.warning(f"No news articles found for {symbol}.")
        return news_data
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network error while fetching news for {symbol}: {str(e)}")
        return []
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return []

# Function to fetch current stock price using yfinance
def fetch_current_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        stock_data = stock.history(period="1d")
        current_price = stock_data["Close"].iloc[-1]
        return current_price
    except Exception as e:
        st.error(f"❌ Error fetching price for {symbol}: {str(e)}")
        return None

# Function to display news in styled blocks
def display_news_blocks(symbol):
    news_articles = fetch_stock_news(symbol)

    if not news_articles:
        st.info("No recent news articles found.")
        return

    for article in news_articles[:5]:  # show top 5 articles
        headline = article.get("headline", "No Title")
        summary = article.get("summary", "No Summary Available")
        url = article.get("url", "#")
        source = article.get("source", "Unknown")
        datetime_field = article.get("datetime", 0)

        try:
            datetime_str = datetime.fromtimestamp(datetime_field).strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            datetime_str = "Unknown Date"
    
        # Slimmed down styling for the news block
        st.markdown(
            f"""
            <div style="
                border-radius: 8px;
                background-color: #1e1e1e;
                padding: 8px;
                margin-bottom: 8px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
                font-size: 0.85rem;
            ">
                <h6 style="color: #60a5fa; font-size: 0.95rem; margin-bottom: 4px;">{headline}</h6>
                <p style="color: #d1d5db; font-size: 0.75rem; margin-bottom: 6px;">{summary}</p>
                <p style="color: #9ca3af; font-size: 0.7rem; margin-bottom: 4px;">🕒 {datetime_str} | 📰 {source}</p>
                <a href="{url}" target="_blank" style="color: #facc15; text-decoration: none; font-size: 0.75rem;">Read More →</a>
            </div>
            """,
            unsafe_allow_html=True
        )

# Display stock news based on the entered symbol
# display_news_blocks(symbol)
