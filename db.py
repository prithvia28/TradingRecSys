from pymongo import MongoClient
import os

# Replace with your MongoDB Atlas URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://edelynblack:Hcw12lnIo0o5gRg6@tradingrecsys.usnddqq.mongodb.net/?retryWrites=true&w=majority&appName=TradingRecSys")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
# Access the database and collection
db = client['TradingRecSys']
portfolio_collection = db['portfolio_collection']

def create_portfolio(user_id):
    """
    Create an empty portfolio for the user.
    :param user_id: The unique identifier for the user.
    """
    portfolio = {
        "user_id": user_id,
        "stocks": []  # Empty list, will be populated with stock data as user buys/sells
    }
    portfolio_collection.insert_one(portfolio)

def update_portfolio(user_id, symbol, shares, avg_price, action):
    """
    Update the portfolio based on buy or sell action.
    :param user_id: The unique identifier for the user.
    :param symbol: The stock symbol.
    :param shares: The number of shares bought/sold.
    :param avg_price: The price at which the stock was bought/sold.
    :param action: "buy" or "sell" action.
    """
    portfolio = portfolio_collection.find_one({"user_id": user_id})
    
    # Check if stock already exists in portfolio
    stock_exists = False
    for stock in portfolio["stocks"]:
        if stock["symbol"] == symbol:
            stock_exists = True
            if action == "buy":
                stock["shares"] += shares  # Add shares to portfolio
                # Update the average price based on the new shares bought
                total_cost = (stock["avg_price"] * (stock["shares"] - shares)) + (avg_price * shares)
                stock["avg_price"] = total_cost / stock["shares"]  # Update the average price
            elif action == "sell" and stock["shares"] >= shares:
                stock["shares"] -= shares  # Sell the shares
            break
        
    # If the stock doesn't exist in the portfolio, add it
    if not stock_exists:
        portfolio["stocks"].append({
            "symbol": symbol,
            "shares": shares,
            "avg_price": avg_price
        })
    
    # Update the portfolio document in MongoDB
    portfolio_collection.update_one(
        {"user_id": user_id},
        {"$set": {"stocks": portfolio["stocks"]}}
    )

def get_portfolio(user_id):
    """
    Fetch the portfolio for the user.
    :param user_id: The unique identifier for the user.
    :return: Portfolio document
    """
    portfolio = portfolio_collection.find_one({"user_id": user_id})
    return portfolio

def save_portfolio_to_mongo(user_id):
    """
    Save the updated portfolio to MongoDB.
    :param user_id: The unique identifier for the user.
    :return: None
    """
    try:
        # Fetch the portfolio from the database
        portfolio = get_portfolio(user_id)
        
        # If the portfolio is empty, return
        if portfolio is None:
            print("Portfolio does not exist!")
            return
        
        # Save portfolio to MongoDB
        portfolio_collection.update_one(
            {"user_id": user_id},
            {"$set": portfolio},  # Replace the entire portfolio document
            upsert=True  # If the portfolio doesn't exist, create it
        )
        print("Portfolio data saved to MongoDB.")
    except Exception as e:
        print(f"Error saving portfolio to MongoDB: {e}")

def load_portfolio_from_mongo(user_id):
    """
    Load the portfolio from MongoDB.
    :param user_id: The unique identifier for the user.
    :return: Dictionary containing portfolio data.
    """
    portfolio = {}
    try:
        # Fetch the portfolio document for the user
        portfolio_doc = portfolio_collection.find_one({"user_id": user_id})
        
        if portfolio_doc:
            portfolio = portfolio_doc["stocks"]
            print("Portfolio data loaded from MongoDB.")
        else:
            print("Portfolio not found in MongoDB.")
    except Exception as e:
        print(f"Error loading portfolio from MongoDB: {e}")
    
    return portfolio
