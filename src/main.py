# main.py
import time
from dotenv import load_dotenv
import os
from messaging.telegram import TelegramMessenger
from services.filter_service import FilterService
from bot.filter_bot import TelegramBot
from constants.constants import FILTERS_FILE

# Load environment variables
load_dotenv()

def main():
    # Initialize the filter service
    filter_service = FilterService(FILTERS_FILE)
    
    # Initialize the messenger
    token = os.getenv("TOKEN")
    messenger = TelegramMessenger(token)
    
    # Create and run the bot
    bot = TelegramBot(messenger, filter_service)
    bot.run()

if __name__ == "__main__":
    main()