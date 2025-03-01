import json
import requests
import time
import logging
from enum import Enum
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TOKEN = os.getenv("TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Predefined list of locations
LOCATIONS = ["New York", "San Francisco", "Los Angeles", "Chicago", "Miami"]
FILTERS_FILE = "filters.json"

class State(Enum):
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


# User data storage
user_data = {}

# Load filters from JSON file
def load_filters():
    """Load filters from the JSON file."""
    try:
        with open(FILTERS_FILE, "r") as file:
            filters_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        filters_data = {}
    
    return filters_data

# Save filters to JSON file
def save_filters(filters_data):
    """Save filters to the JSON file."""
    with open(FILTERS_FILE, "w") as file:
        json.dump(filters_data, file, indent=4)

# Fetch updates from Telegram
def get_updates():
    """Fetch new updates from Telegram."""
    global last_update_id
    response = requests.get(f"{API_URL}/getUpdates", params={"offset": last_update_id}).json()

    if "result" in response:
        for update in response["result"]:
            last_update_id = update["update_id"] + 1
            if "callback_query" in update:
                handle_callback_query(update["callback_query"])  # Handle callback queries
            else:
                handle_message(update)

# Handle incoming messages
def handle_message(update):
    """Handle incoming messages."""
    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    logging.info(f"Received message from {chat_id}: {text}")

    if text == "/start":
        send_welcome(chat_id)
    elif text == "/help":
        send_help(chat_id)
    elif text == "/add":
        add_filter(chat_id)
    elif text == "/view":
        view_filters(chat_id)
    elif text == "/delete":
        delete_filter(chat_id)
    elif text == "/update":
        update_filter(chat_id)
    elif text.lower() == "confirm" and chat_id in user_data:
        confirm_filter(chat_id)
    elif text.lower() == "edit" and chat_id in user_data:
        edit_filter(chat_id)
    elif chat_id in user_data:
        state = user_data[chat_id]["state"]
        if state == State.ITEM:
            user_data[chat_id]["filters"].append({"item": text})
            ask_price(chat_id)
        elif state == State.PRICE:
            user_data[chat_id]["filters"][-1]["price"] = text
            ask_location(chat_id)
        elif state == State.LOCATION:
            user_data[chat_id]["filters"][-1]["location"] = text
            ask_confirmation(chat_id)
        elif state == State.EDIT_ITEM:
            user_data[chat_id]["filters"][-1]["item"] = text
            ask_confirmation(chat_id)
        elif state == State.EDIT_PRICE:
            user_data[chat_id]["filters"][-1]["price"] = text
            ask_confirmation(chat_id)
        elif state == State.EDIT_LOCATION:
            user_data[chat_id]["filters"][-1]["location"] = text
            ask_confirmation(chat_id)
    else:
        send_message(chat_id, "I didn't understand that. Please use /start to begin.")

# Handle callback queries
def handle_callback_query(callback_query):
    """Handle callback queries from inline buttons."""
    chat_id = callback_query["message"]["chat"]["id"]
    callback_data = callback_query["data"]

    if callback_data.startswith("location_") and chat_id in user_data:
        location = callback_data[len("location_"):]
        user_data[chat_id]["filters"][-1]["location"] = location
        send_message(chat_id, f"You selected {location}. Let's proceed!")
        ask_confirmation(chat_id)  # Proceed to confirmation after location selection

# Send welcome message
def send_welcome(chat_id):
    """Send welcome message when user starts the bot."""
    if chat_id not in user_data:
        user_data[chat_id] = {"state": State.ITEM, "filters": []}  # Initialize filters as an empty list
    send_message(chat_id, "Welcome! What item are you looking for?")

# Send help message
def send_help(chat_id):
    """Send the help message listing all available commands."""
    help_message = (
        "Here are the available commands:\n"
        "/start - Start the bot and initiate the filter creation process\n"
        "/help - Display this message with a list of commands\n"
        "/add - Add a new filter\n"
        "/view - View all your saved filters\n"
        "/delete - Delete a specific filter\n"
        "/update - Update an existing filter\n"
    )
    send_message(chat_id, help_message)

# Add new filter
def add_filter(chat_id):
    """Initiate the process of adding a new filter."""
    if chat_id not in user_data:
        user_data[chat_id] = {"state": State.ITEM, "filters": []} 
    user_data[chat_id]["state"] = State.ITEM
    send_message(chat_id, "What item are you looking for?")

# Ask for price
def ask_price(chat_id):
    """Ask for the price."""
    user_data[chat_id]["state"] = State.PRICE
    send_message(chat_id, "What price are you looking for?")

# Ask for location
def ask_location(chat_id):
    """Ask for the location."""
    user_data[chat_id]["state"] = State.LOCATION
    location_buttons = [
        [{"text": location, "callback_data": f"location_{location}"}] for location in LOCATIONS
    ]
    send_inline_buttons(chat_id, "Select a location:", location_buttons)

# Ask for confirmation
def ask_confirmation(chat_id):
    """Ask for confirmation."""
    user_data[chat_id]["state"] = State.CONFIRMATION
    filter_data = user_data[chat_id]["filters"][-1]
    confirmation_message = (
        f"Please confirm the following filter details:\n"
        f"Item: {filter_data['item']}\n"
        f"Price: {filter_data['price']}\n"
        f"Location: {filter_data['location']}\n"
        "Reply with 'confirm' to save or 'edit' to modify."
    )
    send_message(chat_id, confirmation_message)

# Confirm filter and save
def confirm_filter(chat_id):
    """Confirm the filter and save it."""
    chat_id_str = str(chat_id)  # Ensure chat_id is a string
    filters_data = load_filters()  
    
    if chat_id_str not in filters_data:
        filters_data[chat_id_str] = []  # Initialize an empty list if not present
    
    # Append the new filter to the user's list of filters
    filters_data[chat_id_str].append(user_data[chat_id]["filters"][-1])  # Use string chat_id
    save_filters(filters_data)  # Save the filters with updated data

    send_message(chat_id, "Your filter has been saved.")
    del user_data[chat_id]  # Remove the user's data after saving


# Edit existing filter
def edit_filter(chat_id):
    """Allow user to edit an existing filter."""
    filters_data = load_filters()
    if chat_id not in filters_data or not filters_data[chat_id]:
        send_message(chat_id, "You have no saved filters to edit.")
        return

    filters_message = "Select the filter you want to edit:\n"
    for idx, filter_data in enumerate(filters_data[chat_id]):
        filters_message += f"\nFilter {idx+1}:\nItem: {filter_data['item']}\nPrice: {filter_data['price']}\nLocation: {filter_data['location']}\n"
    
    send_message(chat_id, filters_message)
    user_data[chat_id]["state"] = State.EDIT_ITEM

# View saved filters
def view_filters(chat_id):
    """View all the filters the user has saved."""
    filters_data = load_filters()
    chat_id = str(chat_id)

    if chat_id not in filters_data or not filters_data[chat_id]:
        send_message(chat_id, "You have no saved filters.")
        return

    filters_message = "Your saved filters:\n"
    for idx, filter_data in enumerate(filters_data[chat_id]):
        filters_message += f"\nFilter {idx + 1}:\nItem: {filter_data['item']}\nPrice: {filter_data['price']}\nLocation: {filter_data['location']}\n"

    send_message(chat_id, filters_message)

# Delete filter (not yet implemented)
def delete_filter(chat_id):
    send_message(chat_id, "Deletion is not yet supported!")

# Update filter (not yet implemented)
def update_filter(chat_id):
    send_message(chat_id, "Update is not yet supported!")

# Send message to user
def send_message(chat_id, text):
    """Send a message to the user and log it."""
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(f"{API_URL}/sendMessage", data=payload)
    logging.info(f"Sent message to {chat_id}: {text}")

# Send inline keyboard buttons
def send_inline_buttons(chat_id, text, buttons):
    """Send inline buttons."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps({"inline_keyboard": buttons}),
    }
    response = requests.post(f"{API_URL}/sendMessage", data=payload)
    logging.info(f"Sent inline buttons to {chat_id}: {buttons}")

# Main loop to fetch and process updates
if __name__ == "__main__":
    last_update_id = None  # Initialize the last update ID
    while True:
        get_updates()  # Fetch updates from Telegram
        time.sleep(1)  # Sleep to avoid hitting API limits
