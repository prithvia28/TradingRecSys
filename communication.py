# Save this as communication.py or add to your agents.py file

from datetime import datetime
import time
import pandas as pd
import streamlit as st

class AgentCommunicationBus:
    """Simplified communication bus that manages messages between agents"""
    def __init__(self):
        """Initialize the communication bus with message storage and tracking"""
        self.messages = []
        self.message_history = []  # For keeping a history of all messages
        self.last_updated = datetime.now().strftime("%H:%M:%S")
    
    def send_message(self, sender, recipient, message_type, content, priority="normal"):
        """
        Send a message from one agent to another with tracking.
        
        :param sender: Name of the sending agent
        :param recipient: Name of the receiving agent ('all' for broadcast)
        :param message_type: Type of message (e.g., 'data_request', 'analysis_result')
        :param content: Content of the message (can be any serializable object)
        :param priority: Message priority ('high', 'normal', 'low')
        :return: Message ID for tracking
        """
        # Generate timestamp and message ID
        timestamp = datetime.now()
        message_id = f"{len(self.messages) + 1}-{int(timestamp.timestamp())}"
        
        # Create the message object
        message = {
            "id": message_id,
            "timestamp": timestamp.strftime("%H:%M:%S"),
            "sender": sender,
            "recipient": recipient,
            "type": message_type,
            "content": content,
            "priority": priority,
            "status": "sent"
        }
        
        # Add to active messages and history
        self.messages.append(message)
        self.message_history.append(message.copy())
        
        # Update last updated timestamp
        self.last_updated = timestamp.strftime("%H:%M:%S")
        
        return message_id
    
    def acknowledge_message(self, message_id, recipient):
        """
        Mark a message as acknowledged by a recipient.
        
        :param message_id: ID of the message to acknowledge
        :param recipient: Name of the recipient acknowledging the message
        :return: True if acknowledged, False if message not found
        """
        for message in self.messages:
            if message["id"] == message_id and (message["recipient"] == recipient or message["recipient"] == "all"):
                message["status"] = "acknowledged"
                # Update the corresponding message in history
                for hist_message in self.message_history:
                    if hist_message["id"] == message_id:
                        hist_message["status"] = "acknowledged"
                return True
        return False
    
    def complete_message(self, message_id, recipient, response=None):
        """
        Mark a message as completed by a recipient and optionally add a response.
        
        :param message_id: ID of the message to complete
        :param recipient: Name of the recipient completing the message
        :param response: Optional response data
        :return: True if completed, False if message not found
        """
        for i, message in enumerate(self.messages):
            if message["id"] == message_id and (message["recipient"] == recipient or message["recipient"] == "all"):
                message["status"] = "completed"
                if response:
                    message["response"] = response
                
                # Update the corresponding message in history
                for hist_message in self.message_history:
                    if hist_message["id"] == message_id:
                        hist_message["status"] = "completed"
                        if response:
                            hist_message["response"] = response
                
                return True
        return False
    
    def get_messages_for(self, recipient):
        """
        Retrieve all active messages for a specific recipient.
        
        :param recipient: Name of the recipient agent
        :return: List of messages for the recipient
        """
        return [m for m in self.messages if m['recipient'] == recipient or m['recipient'] == 'all']
    
    def get_message_metrics(self):
        """
        Get metrics about message activity.
        
        :return: Dictionary with message metrics
        """
        # Calculate metrics on-demand
        by_type = {}
        by_sender = {}
        by_recipient = {}
        
        for msg in self.messages:
            # Count by type
            msg_type = msg['type']
            if msg_type not in by_type:
                by_type[msg_type] = 0
            by_type[msg_type] += 1
            
            # Count by sender
            sender = msg['sender']
            if sender not in by_sender:
                by_sender[sender] = 0
            by_sender[sender] += 1
            
            # Count by recipient
            recipient = msg['recipient']
            if recipient not in by_recipient:
                by_recipient[recipient] = 0
            by_recipient[recipient] += 1
        
        return {
            'total_messages': len(self.message_history),
            'active_messages': len(self.messages),
            'by_type': by_type,
            'by_sender': by_sender,
            'by_recipient': by_recipient,
            'last_updated': self.last_updated
        }