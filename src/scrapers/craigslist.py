from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging
import json
import os
import time
from constants.constants import FILTERS_FILE, RESULTS_FILE, LINKS_FILE

def load_config(config_file=FILTERS_FILE):
    """Loads search parameters from config file."""
    with open(config_file, 'r') as file:
        return json.load(file)

def load_existing_links():
    """Loads the list of previously scraped links from the file."""
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r') as file:
            return set(line.strip() for line in file.readlines())
    return set()

def save_link_to_file(link):
    """Saves a new link to the file."""
    with open(LINKS_FILE, 'a') as file:
        file.write(link + '\n')

def save_results(results):
    """Saves the scraped results to a JSON file safely."""
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r') as file:
                existing_results = json.load(file)
        except (json.JSONDecodeError, ValueError):
            existing_results = []  
    else:
        existing_results = []

    existing_results.extend(results)

    with open(RESULTS_FILE, 'w') as file:
        json.dump(existing_results, file, indent=4, ensure_ascii=False)

def build_search_url(search_params):
    """Builds a Craigslist search URL based on item, location, and price."""
    item = search_params['item']
    location = search_params['location']
    price = search_params['price']
    
    # Normalize location for URL
    location_map = {
        "San Francisco": "sfbay",
        "Chicago": "chicago",
        "New York": "newyork",
        # Add more mappings as needed
    }
    
    # Default to San Diego if location not in map
    city_code = location_map.get(location, "sandiego")
    
    # Base URL with search query
    url = f"https://{city_code}.craigslist.org/search/sss?query={item}"
    
    # Add price filter if specified
    if price and price.isdigit():
        url += f"&max_price={price}"
    
    return url

def scrape_craigslist(url, search_params):
    """Scrapes Craigslist listings from the given URL and returns them as a list of dictionaries."""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    
    # Set up Chrome options to run in headless modefrom selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("--headless=new")  # Faster headless mode
    options.add_argument("--disable-gpu")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Prevents crashes due to limited `/dev/shm`
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    options.add_argument("--disable-extensions")  # Speeds up loading
    options.add_argument("--disable-infobars")  # Removes unnecessary UI
    options.add_argument("--remote-debugging-port=9222")  # Allows Chrome to be debugged
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-renderer-backgrounding")  # Prevents Chrome from throttling when in the background
    options.add_argument("--disable-background-timer-throttling")  # Speeds up timers
    options.add_argument("--disable-backgrounding-occluded-windows")  
    options.add_argument("--blink-settings=imagesEnabled=false")  # Disables images for faster loading
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    chrome_driver_path = "/usr/bin/chromedriver"
    
    # Initialize the WebDriver
    try:
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
    except Exception as e:
        logger.error(f"Error initializing Chrome WebDriver: {e}")
        return []
    
    # Open the Craigslist page
    try:
        logger.info(f"Opening URL: {url}")
        driver.get(url)
    except Exception as e:
        logger.error(f"Error opening URL {url}: {e}")
        driver.quit()
        return []
    
    # Get the page source after rendering
    html = driver.page_source
    driver.quit()
    
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.find_all('div', class_='cl-search-result cl-search-view-mode-gallery')
    
    # Load existing links
    existing_links = load_existing_links()
    
    # Extract data from listings
    extracted_listings = []
    for listing in listings:
        try:
            title_element = listing.find('a', class_='cl-app-anchor text-only posting-title')
            if title_element:
                title = title_element.find('span', class_='label').text.strip()
            else:
                continue
                
            price_element = listing.find('span', class_='priceinfo')
            price = price_element.text.strip() if price_element else 'No price listed'
            
            link_element = listing.find('a', class_='main singleton')
            if not link_element:
                continue
            link = link_element.get('href')
            
            if title and link and link not in existing_links:
                extracted_listings.append({
                    'title': title, 
                    'price': price, 
                    'link': link,
                    'search_item': search_params['item'],
                    'search_location': search_params['location'],
                    'max_price': search_params['price']
                })
                save_link_to_file(link)
                
        except Exception as e:
            logger.warning(f"Error extracting details for a listing: {e}")
    
    return extracted_listings

def main(chat_id: str):
    # Load config
    config = load_config()
    
    all_results = []
    for user_id, search_params_list in config.items():
        if chat_id != user_id:  continue
        for search_params in search_params_list:
            try:
                url = build_search_url(search_params)
                print(f"Searching for {search_params['item']} in {search_params['location']} with max price ${search_params['price']}")
                results = scrape_craigslist(url, search_params)
                
                # Add user ID to each result
                for result in results:
                    result['user_id'] = user_id
                
                all_results.extend(results)
                print(f"Found {len(results)} results")
                
                # Sleep between requests to avoid rate limiting
                time.sleep(3)
                
            except Exception as e:
                print(f"Error processing search for {search_params}: {e}")
    
    # Save all results
    save_results(all_results)
    print(f"Total results saved: {len(all_results)}")
    return all_results

if __name__ == "__main__":
    main()