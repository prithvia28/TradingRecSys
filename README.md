# 📈 FinnXperts - Multi-Agent Stock Recommendation System

**TradingRecSys** is an intelligent, multi-agent stock recommendation system that uses a goal-driven architecture to analyze, recommend, and manage trades with a focus on execution quality and risk management.

Built with ❤️ using Python, Streamlit, and a modular agent-based design, this app is ideal for both educational and experimental financial AI applications.

---

## 🚀 Features

- 📊 **Real-time stock buy/sell/hold Recommendations**
- 🧠 **Multi-Agent Architecture**
- 🛡️ **Dynamic Risk Management**
- 🤖 **Autonomous Execution Decisions**
- 🔁 **Feedback Loop Between risk management and execution agent**
- 🌐 **Streamlit Web Interface**
- :newspaper:	  **Display news for selected stock**
- :robot: **Chatbot integration for better understandiung for financial terms and working.**

---

## 🧩 Multi-Agent Design

The system consists of four specialized agents that collaborate to analyze stock data, generate recommendations, evaluate risk, and execute trades. Communication is handled via a shared `AgentCommunicationBus`, enabling real-time feedback and coordination.

### 1. MarketDataAgent
- **Goal:** Fetch and manage stock market data for selected tickers.
- **State:** Historical price data, OHLCV values, volume trends.
- **Action:** Supplies raw data for analysis and decision-making.

### 2. TechnicalAnalysisAgent
- **Goal:** Analyze stock data using technical indicators to generate a confidence score.
- **State:** Moving averages, RSI, MACD, Bollinger Bands, custom scoring models.
- **Action:** Evaluates and scores stocks, passing results to the ExecutionAgent.

### 3. ExecutionAgent
- **Goal:** Determine whether to execute trades based on signals and risk evaluation.
- **State:** Analysis output, portfolio constraints, market conditions.
- **Action:** Initiates trade actions or holds based on received feedback from Risk_Management agent.

### 4. RiskManagementAgent
- **Goal:** Evaluate and control risk exposure across trade opportunities.
- **State:** Volatility levels, stop-loss thresholds, risk-reward ratios.
- **Action:** Can approve, adjust, or reject trades. If risk is too high, instructs ExecutionAgent to HOLD.

---

### 🔁 Agent Interaction Flow

**MarketDataAgent** → **TechnicalAnalysisAgent** → **ExecutionAgent**  
**RiskManagementAgent** ↔ **ExecutionAgent**  
All communication happens via the `AgentCommunicationBus`.

If the **RiskManagementAgent** detects high exposure or unfavorable conditions, it sends a feedback signal to the **ExecutionAgent** to **HOLD** the stock and skip execution.



### Cloning and Running the App

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/prithvia28/TradingRecSys.git>
   cd <path to your repo>
   ### Setting Up

2. **Create and activate a virtual environment:**

   ```bash
   # Create a virtual environment named 'venv'
   python -m venv venv

   # Activate the virtual environment
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate

3. **Running project**

   ```bash
   
   pip install -r requirements.txt
   streamlit run app.py

