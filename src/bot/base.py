from abc import ABC, abstractmethod
import time
from enum import Enum

class BotState(Enum):
    """Base enum for bot states - can be extended by specific bots"""
    INITIAL = "initial"
    PROCESSING = "processing"
    CONFIRMATION = "confirmation"

class BaseBot(ABC):
    """Abstract base class for all bots"""
    
    def __init__(self, messenger):
        self.messenger = messenger
        self.user_data = {}  # Store user session data
    
    def run(self):
        """Main loop for bot operation"""
        self.messenger.set_handlers(self.handle_message, self.handle_callback)
        
        while True:
            self.messenger.get_updates()
            time.sleep(1)
    
    @abstractmethod
    def handle_message(self, message):
        """Handle incoming messages"""
        pass
    
    @abstractmethod
    def handle_callback(self, callback):
        """Handle callback queries"""
        pass