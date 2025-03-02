from abc import ABC, abstractmethod
from threading import Thread
import time
from enum import Enum
import logging
import schedule

from scrapers import craigslist

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotState(Enum):
    """Base enum for bot states - can be extended by specific bots"""
    INITIAL = "initial"
    PROCESSING = "processing"
    CONFIRMATION = "confirmation"
    
class FilterState(Enum):
    """States specific to the filter bot"""
    ITEM = "item"
    PRICE = "price"
    LOCATION = "location"
    CONFIRMATION = "confirmation"
    EDIT_ITEM = "edit_item"
    EDIT_PRICE = "edit_price"
    EDIT_LOCATION = "edit_location"
    VIEW_FILTER = "view_filter"
    DELETE_FILTER = "delete_filter"
    UPDATE_FILTER = "update_filter"

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
    
    def _start_background_search(self):
        """Start the background thread for periodic searching"""
        search_thread = Thread(target=self._run_periodic_search, daemon=True)
        search_thread.start()
        logger.info("Background search thread started")

    def _run_periodic_search(self):
        """Run periodic search every 10 minutes"""
        # Schedule the job to run every 10 minutes
        schedule.every(10).minutes.do(self._search_all_filters)
        logger.info("Scheduled periodic search every 10 minutes")
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def _search_all_filters(self):
        """Search for all users' filters"""
        try:
            logger.info("Starting periodic search for all users")
            
            # Get all users with filters
            all_users = self.filter_service.get_all_users()
            logger.info(f"Found {len(all_users)} users with filters")
            
            for user_id in all_users:
                # Skip if user is currently being searched in confirm_filter
                chat_id = int(user_id)
                if chat_id in self.is_searching and self.is_searching[chat_id]:
                    logger.info(f"Skipping user {user_id} - already being searched")
                    continue
                
                logger.info(f"Searching for user {user_id}")
                results = craigslist.main(user_id)
                
                if results:
                    logger.info(f"Found {len(results)} results for user {user_id}")
                    self.messenger.send_message(chat_id, "New listings matching your filters:")
                    for result in results:
                        self.messenger.send_message(chat_id, f"{result['title']}\n{result['price']}\n{result['link']}")
                else:
                    logger.info(f"No results found for user {user_id}")
            
            logger.info("Completed periodic search for all users")
        except Exception as e:
            logger.error(f"Error in periodic search: {str(e)}", exc_info=True)
    
    def _search_for_user(self, chat_id):
        """Run an immediate search for a specific user in a separate thread"""
        def search_thread_func():
            chat_id_str = str(chat_id)
            self.is_searching[chat_id] = True
            logger.info(f"Starting immediate search for user {chat_id_str}")
            
            try:
                results = craigslist.main(chat_id_str)
                
                if results:
                    logger.info(f"Found {len(results)} results for user {chat_id_str}")
                    self.messenger.send_message(chat_id, "Here are current listings matching your filter:")
                    for result in results:
                        self.messenger.send_message(chat_id, f"{result['title']}\n{result['price']}\n{result['link']}")
                else:
                    logger.info(f"No results found for user {chat_id_str}")
                    self.messenger.send_message(
                        chat_id,
                        "No listings found matching your filter currently. You'll be notified when items appear."
                    )
            except Exception as e:
                logger.error(f"Error in immediate search for user {chat_id_str}: {str(e)}", exc_info=True)
                self.messenger.send_message(
                    chat_id,
                    f"Your filter has been saved, but there was an error running the search: {str(e)}"
                )
            finally:
                # Clear search status
                self.is_searching[chat_id] = False
                logger.info(f"Completed immediate search for user {chat_id_str}")
        
        # Start search in a new thread
        search_thread = Thread(target=search_thread_func)
        search_thread.daemon = True
        search_thread.start()