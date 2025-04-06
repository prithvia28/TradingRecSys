import streamlit as st

class AgentCommunicationBus:
    def __init__(self):
        """
        Initialize the communication bus to manage messages between agents.
        """
        self.messages = []
    
    def send_message(self, sender, recipient, message_type, content):
        """
        Send a message from one agent to another.
        
        :param sender: Name of the sending agent
        :param recipient: Name of the receiving agent
        :param message_type: Type of message (e.g., 'analysis', 'risk_assessment')
        :param content: Content of the message
        """
        self.messages.append({
            "from": sender,
            "to": recipient,
            "type": message_type,
            "content": content,
            "timestamp": st.session_state.get('current_time', 'N/A')
        })
    
    def get_messages_for(self, recipient):
        """
        Retrieve all messages for a specific recipient.
        
        :param recipient: Name of the recipient agent
        :return: List of messages for the recipient
        """
        return [m for m in self.messages if m['to'] == recipient]
    
    def clear_messages_for(self, recipient):
        """
        Clear messages for a specific recipient.
        
        :param recipient: Name of the recipient agent
        """
        self.messages = [m for m in self.messages if m['to'] != recipient]

class BaseAgent:
    """
    Base class for all agents with common functionality.
    """
    def __init__(self, bus, name):
        """
        Initialize an agent with a communication bus.
        
        :param bus: AgentCommunicationBus instance
        :param name: Name of the agent
        """
        self.bus = bus
        self.name = name
        self.status = "Initialized"
    
    def send_message(self, recipient, message_type, content):
        """
        Send a message to another agent.
        
        :param recipient: Name of the receiving agent
        :param message_type: Type of message
        :param content: Content of the message
        """
        self.bus.send_message(self.name, recipient, message_type, content)
    
    def receive_messages(self):
        """
        Retrieve messages for this agent.
        
        :return: List of messages for this agent
        """
        return self.bus.get_messages_for(self.name)
    
    def clear_messages(self):
        """
        Clear messages for this agent.
        """
        self.bus.clear_messages_for(self.name)

class MarketDataAgent(BaseAgent):
    def __init__(self, bus):
        super().__init__(bus, "MarketDataAgent")
        self.status = "Waiting for data request"

class TechnicalAnalysisAgent(BaseAgent):
    def __init__(self, bus):
        super().__init__(bus, "TechnicalAnalysisAgent")
        self.status = "Ready for market analysis"

class RiskManagementAgent(BaseAgent):
    def __init__(self, bus):
        super().__init__(bus, "RiskManagementAgent")
        self.status = "Monitoring risk levels"

class ExecutionAgent(BaseAgent):
    def __init__(self, bus):
        super().__init__(bus, "ExecutionAgent")
        self.status = "Awaiting trade execution instructions"

# --- Initialize Bus + Agents ---
bus = AgentCommunicationBus()
market_data_agent = MarketDataAgent(bus)
tech_agent = TechnicalAnalysisAgent(bus)
execution_agent = ExecutionAgent(bus)
risk_agent = RiskManagementAgent(bus)

# --- Session state for button click ---
if "analyze" not in st.session_state:
    st.session_state["analyze"] = False

# -------------------- AGENT STATUS ---------------------
st.markdown("## 🤖 Agent Status")

# Market Data Agent
st.markdown("### 📊 MarketDataAgent")
st.info(market_data_agent.status)

# Technical Analysis Agent
st.markdown("### 🧠 TechnicalAnalysisAgent")
st.info(tech_agent.status)

# Risk Management Agent
st.markdown("### 🛡️ RiskManagementAgent")
st.info(risk_agent.status)

# Execution Agent
st.markdown("### 💼 ExecutionAgent")
st.info(execution_agent.status)

# -------------------- COMMUNICATION ---------------------
st.markdown("## 🔌 Inter-Agent Communication")
st.markdown("### 📡 Message Queue")

if bus.messages:
    for msg in bus.messages:
        st.json(msg)
else:
    st.info("No messages in the queue. Agents processed and cleared them.")