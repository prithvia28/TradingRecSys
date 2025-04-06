# Add this to your agents.py file or create a new file

from datetime import datetime

class BaseAgent:
    """Base class for all agents in the system"""
    def __init__(self, name, communication_bus=None):
        self.name = name
        self.status = "Initialized"
        self.output = None
        self.latest_update = datetime.now().strftime("%H:%M:%S")
        self.processing_time = 0
        self.communication_bus = communication_bus  # Reference to the communication bus
    
    def update_status(self, status):
        """Update the agent's status"""
        self.status = status
        self.latest_update = datetime.now().strftime("%H:%M:%S")
    
    def send_message(self, recipient, message_type, content, priority="normal"):
        """Send a message to another agent through the communication bus"""
        if self.communication_bus:
            message_id = self.communication_bus.send_message(
                self.name, recipient, message_type, content, priority
            )
            return message_id
        else:
            return None

class MarketDataAgent(BaseAgent):
    """Agent responsible for collecting market data"""
    def __init__(self, communication_bus=None):
        super().__init__("MarketDataAgent", communication_bus)
        self.status = "Waiting for data request"

class TechnicalAnalysisAgent(BaseAgent):
    """Agent responsible for technical analysis"""
    def __init__(self, communication_bus=None):
        super().__init__("TechnicalAnalysisAgent", communication_bus)
        self.status = "Ready for market analysis"

class RiskManagementAgent(BaseAgent):
    """Agent responsible for risk assessment and management"""
    def __init__(self, communication_bus=None):
        super().__init__("RiskManagementAgent", communication_bus)
        self.status = "Monitoring risk levels"

class ExecutionAgent(BaseAgent):
    """Agent responsible for final recommendations and execution decisions"""
    def __init__(self, communication_bus=None):
        super().__init__("ExecutionAgent", communication_bus)
        self.status = "Awaiting trade execution instructions"