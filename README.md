# CraigslistTelegramNotifier

messaging_bot/
├── main.py                    # Entry point
├── bot/
│   ├── __init__.py
│   ├── base.py                # Base bot class
│   └── filter_bot.py          # Filter bot implementation
├── messaging/
│   ├── __init__.py
│   ├── base.py                # Base messenger interface
│   ├── telegram.py            # Telegram implementation
│   ├── discord.py             # Future Discord implementation
│   └── email.py               # Future Email implementation
├── services/
│   ├── __init__.py
│   └── filter_service.py      # Filter data management
└── filters.json               # Data storage