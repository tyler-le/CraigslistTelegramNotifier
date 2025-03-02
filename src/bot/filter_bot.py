from .base import BaseBot, BotState
from enum import Enum
from threading import Thread
import time
import schedule

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

class TelegramBot(BaseBot):
    """Bot for managing item filters"""
    
    LOCATIONS = ["New York", "San Francisco", "Los Angeles", "Chicago", "Miami"]
    
    def __init__(self, messenger, filter_service):
        super().__init__(messenger)
        self.filter_service = filter_service
        # Start the periodic search thread
        self._start_background_search()
    
    def _start_background_search(self):
        """Start the background thread for periodic searching"""
        search_thread = Thread(target=self._run_periodic_search, daemon=True)
        search_thread.start()
    
    def _run_periodic_search(self):
        """Run periodic search every 10 minutes"""
        # Schedule the job to run every 10 minutes
        schedule.every(10).minutes.do(self._search_all_filters)
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def _search_all_filters(self):
        """Search for all users' filters"""
        try:
            from scrapers import craigslist
            # Get all users with filters
            all_users = self.filter_service.get_all_users()
            
            for user_id in all_users:
                # Convert string user_id to integer for messenger
                chat_id = int(user_id)
                results = craigslist.main(user_id)
                
                if results:
                    self.messenger.send_message(chat_id, "New listings matching your filters:")
                    for result in results:
                        self.messenger.send_message(chat_id, f"{result['title']}\n{result['price']}\n{result['link']}")
        except Exception as e:
            # Log the error but don't crash the thread
            print(f"Error in periodic search: {str(e)}")
    
    def handle_message(self, update):
        """Handle incoming messages"""
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        # Command handling
        if text == "/start":
            self.send_welcome(chat_id)
        elif text == "/help":
            self.send_help(chat_id)
        elif text == "/add":
            self.add_filter(chat_id)
        elif text == "/view":
            self.view_filters(chat_id)
        elif text == "/delete":
            self.delete_filter(chat_id)
        elif text == "/update":
            self.update_filter(chat_id)
        elif text.lower() == "confirm" and chat_id in self.user_data:
            self.confirm_filter(chat_id)
        elif text.lower() == "edit" and chat_id in self.user_data:
            self.edit_filter(chat_id)
        # State-based handling
        elif chat_id in self.user_data:
            self.process_state_input(chat_id, text)
        else:
            self.messenger.send_message(chat_id, "I didn't understand that. Please use /start to begin.")
    
    def handle_callback(self, callback_query):
        """Handle callback queries from inline buttons"""
        chat_id = callback_query["message"]["chat"]["id"]
        callback_data = callback_query["data"]
        
        if callback_data.startswith("location_") and chat_id in self.user_data:
            location = callback_data[len("location_"):]
            self.user_data[chat_id]["filters"][-1]["location"] = location
            self.messenger.send_message(chat_id, f"You selected {location}. Let's proceed!")
            self.ask_confirmation(chat_id)
    
    def process_state_input(self, chat_id, text):
        """Process user input based on the current state"""
        state = self.user_data[chat_id]["state"]
        
        if state == FilterState.ITEM:
            self.user_data[chat_id]["filters"].append({"item": text})
            self.ask_price(chat_id)
        elif state == FilterState.PRICE:
            self.user_data[chat_id]["filters"][-1]["price"] = text
            self.ask_location(chat_id)
        elif state == FilterState.LOCATION:
            self.user_data[chat_id]["filters"][-1]["location"] = text
            self.ask_confirmation(chat_id)
        elif state == FilterState.EDIT_ITEM:
            self.user_data[chat_id]["filters"][-1]["item"] = text
            self.ask_confirmation(chat_id)
        elif state == FilterState.EDIT_PRICE:
            self.user_data[chat_id]["filters"][-1]["price"] = text
            self.ask_confirmation(chat_id)
        elif state == FilterState.EDIT_LOCATION:
            self.user_data[chat_id]["filters"][-1]["location"] = text
            self.ask_confirmation(chat_id)
    
    def send_welcome(self, chat_id):
        """Send welcome message"""
        if chat_id not in self.user_data:
            self.user_data[chat_id] = {"state": FilterState.ITEM, "filters": []}
        self.messenger.send_message(chat_id, "Welcome! What item are you looking for?")
    
    def send_help(self, chat_id):
        """Send help message"""
        help_message = (
            "Here are the available commands:\n"
            "/start - Start the bot and initiate the filter creation process\n"
            "/help - Display this message with a list of commands\n"
            "/add - Add a new filter\n"
            "/view - View all your saved filters\n"
            "/delete - Delete a specific filter\n"
            "/update - Update an existing filter\n"
        )
        self.messenger.send_message(chat_id, help_message)
    
    def add_filter(self, chat_id):
        """Start adding a new filter"""
        if chat_id not in self.user_data:
            self.user_data[chat_id] = {"state": FilterState.ITEM, "filters": []}
        self.user_data[chat_id]["state"] = FilterState.ITEM
        self.messenger.send_message(chat_id, "What item are you looking for?")
    
    def ask_price(self, chat_id):
        """Ask for price"""
        self.user_data[chat_id]["state"] = FilterState.PRICE
        self.messenger.send_message(chat_id, "What price are you looking for?")
    
    def ask_location(self, chat_id):
        """Ask for location"""
        self.user_data[chat_id]["state"] = FilterState.LOCATION
        location_buttons = [
            [{"text": location, "callback_data": f"location_{location}"}] 
            for location in self.LOCATIONS
        ]
        self.messenger.send_buttons(chat_id, "Select a location:", location_buttons)
    
    def ask_confirmation(self, chat_id):
        """Ask for confirmation"""
        self.user_data[chat_id]["state"] = FilterState.CONFIRMATION
        filter_data = self.user_data[chat_id]["filters"][-1]
        confirmation_message = (
            f"Please confirm the following filter details:\n"
            f"Item: {filter_data['item']}\n"
            f"Price: {filter_data['price']}\n"
            f"Location: {filter_data['location']}\n"
            "Reply with 'confirm' to save or 'edit' to modify."
        )
        self.messenger.send_message(chat_id, confirmation_message)
    
    def confirm_filter(self, chat_id):
        """Confirm and save the filter"""
        chat_id_str = str(chat_id)
        filter_data = self.user_data[chat_id]["filters"][-1]
        self.filter_service.add_filter(chat_id_str, filter_data)
        self.messenger.send_message(chat_id, "Your filter has been saved.")
        del self.user_data[chat_id]
    
    def view_filters(self, chat_id):
        """View saved filters"""
        chat_id_str = str(chat_id)
        filters = self.filter_service.get_user_filters(chat_id_str)
        
        if not filters:
            self.messenger.send_message(chat_id, "You have no saved filters.")
            return
        
        filters_message = "Your saved filters:\n"
        for idx, filter_data in enumerate(filters):
            filters_message += f"\nFilter {idx + 1}:\nItem: {filter_data['item']}\nPrice: {filter_data['price']}\nLocation: {filter_data['location']}\n"
        
        self.messenger.send_message(chat_id, filters_message)
    
    def delete_filter(self, chat_id):
        """Delete a filter"""
        self.messenger.send_message(chat_id, "Deletion is not yet supported!")
    
    def update_filter(self, chat_id):
        """Update a filter"""
        self.messenger.send_message(chat_id, "Update is not yet supported!")
    
    def edit_filter(self, chat_id):
        """Edit a filter"""
        chat_id_str = str(chat_id)
        filters = self.filter_service.get_user_filters(chat_id_str)
        
        if not filters:
            self.messenger.send_message(chat_id, "You have no saved filters to edit.")
            return
        
        filters_message = "Select the filter you want to edit:\n"
        for idx, filter_data in enumerate(filters):
            filters_message += f"\nFilter {idx+1}:\nItem: {filter_data['item']}\nPrice: {filter_data['price']}\nLocation: {filter_data['location']}\n"
        
        self.messenger.send_message(chat_id, filters_message)
        self.user_data[chat_id]["state"] = FilterState.EDIT_ITEM