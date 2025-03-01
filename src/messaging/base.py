from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class BaseMessenger(ABC):
    """Abstract base class for all messaging platforms"""
    
    @abstractmethod
    def get_updates(self):
        """Fetch new updates from the messaging platform"""
        pass
    
    @abstractmethod
    def send_message(self, recipient_id, text):
        """Send a message to a user"""
        pass
    
    @abstractmethod
    def send_buttons(self, recipient_id, text, buttons):
        """Send interactive buttons to a user"""
        pass