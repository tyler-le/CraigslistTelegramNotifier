# CraigslistTelegramNotifier

This bot allows users to set filters for Craigslist items and receive notifications via Telegram when matching listings are found.

## Features

- Users can add filters for specific items, price ranges, and locations.
- Filters are stored persistently in a JSON file.
- Notifications are sent via Telegram when a matching listing is found.
- Users can view and edit their filters at any time.

## Requirements

- Python 3.8+
- A Telegram bot token (register via [BotFather](https://t.me/BotFather))
- A Raspberry Pi or other hosting environment (optional)

## Installation

1. Clone this repository:

   ```sh
   git clone https://github.com/your-repo/craigslist-filter-bot.git
   cd craigslist-filter-bot
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your Telegram bot token:

   ```sh
   TOKEN=your_telegram_bot_token_here
   ```

4. Run the bot:

   ```sh
   python main.py
   ```

## Usage

1. Start a chat with your Telegram bot.
2. Use `/start` to begin the filter setup.
3. Follow the bot's prompts to specify:
   - Item name
   - Price range
   - Location
4. The bot will monitor Craigslist and notify you when matching listings appear.
5. Use commands to manage your filters:
   - `/add_filter` – Add a new filter
   - `/view_filters` – View existing filters
   - `/edit_filter` – Modify an existing filter
   - `/delete_filter` – Remove a filter

## Configuration

- The bot stores filters in a JSON file (`filters.json`).
- Modify `constants/constants.py` if you need to change file paths or other settings.

## Deployment

- You can run this bot on a Raspberry Pi or a cloud server.
- Consider using `systemd` or `screen/tmux` to keep it running persistently.

## Future Improvements

- Add advanced filtering options (e.g., keyword matching, auto-refresh rates).
- Improve user interaction with inline buttons.

## License

This project is licensed under the MIT License.
