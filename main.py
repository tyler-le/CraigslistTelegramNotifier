import time
from craigslist import scrape_craigslist
from telegram import send_telegram

while True:
    print("Scraping Craigslist...")
    deals = scrape_craigslist()

    if deals:
        send_telegram(deals) 
        pass
    else:
        print("Found no deals")

    print("Waiting 10 minutes before checking again...")
    time.sleep(600)  
