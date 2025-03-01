import requests
import json
import logging
from .base import BaseMessenger

class TelegramMessenger(BaseMessenger):
    """Implementation for Telegram messaging platform"""
    
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = None
        self.callback_handler = None
        self.message_handler = None

    def set_handlers(self, message_handler, callback_handler):
        """Set the handlers for messages and callbacks"""
        self.message_handler = message_handler
        self.callback_handler = callback_handler
    
    def get_updates(self):
        """Fetch new updates from Telegram"""
        params = {"offset": self.last_update_id} if self.last_update_id else {}
        response = requests.get(f"{self.api_url}/getUpdates", params=params).json()
        
        if "result" in response:
            for update in response["result"]:
                self.last_update_id = update["update_id"] + 1
                if "callback_query" in update and self.callback_handler:
                    self.callback_handler(update["callback_query"])
                elif "message" in update and self.message_handler:
                    self.message_handler(update)
    
    def send_message(self, chat_id, text):
        """Send a message to the user"""
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(f"{self.api_url}/sendMessage", data=payload)
        logging.info(f"Sent message to {chat_id}: {text}")
        return response.json()
    
    def send_buttons(self, chat_id, text, buttons):
        """Send inline buttons to the user"""
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps({"inline_keyboard": buttons})
        }
        response = requests.post(f"{self.api_url}/sendMessage", data=payload)
        logging.info(f"Sent inline buttons to {chat_id}")
        return response.json()