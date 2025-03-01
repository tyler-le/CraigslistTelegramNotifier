from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging
import json
import os

# Define a file to store the links
LINKS_FILE = "scraped_links.txt"

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

def scrape_craigslist(url="https://sandiego.craigslist.org/search/sss?query=ps5"):
    """Scrapes Craigslist listings from the given URL and returns them as a list of dictionaries."""
    # Set up logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    
    # Set up Chrome options to run in headless mode (no UI)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")  
    options.add_argument("--no-sandbox")  
    
    # Initialize the WebDriver
    try:
        logger.info("Initializing Chrome WebDriver.")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        logger.error(f"Error initializing Chrome WebDriver: {e}")
        return []
    
    # Open the Craigslist page
    try:
        logger.info(f"Opening URL: {url}")
        driver.get(url)
        driver.implicitly_wait(10)  # Wait for elements to load
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
    
    extracted_listings = []
    for listing in listings:
        try:
            title = listing.find('a', class_='cl-app-anchor text-only posting-title').find('span', class_='label').text.strip()
            price = listing.find('span', class_='priceinfo').text.strip() if listing.find('span', class_='priceinfo') else 'No price listed'
            link = listing.find('a', class_='main singleton').get('href')
            
            if title and price and link and link not in existing_links:
                extracted_listings.append({'title': title, 'price': price, 'link': link})
                save_link_to_file(link)  
        except AttributeError:
            logger.warning("Error extracting details for a listing.")
    
    return extracted_listings

# Example usage
if __name__ == "__main__":
    url = "https://sandiego.craigslist.org/search/sss?query=ps5"
    results = scrape_craigslist(url)
    print(json.dumps(results, indent=4, ensure_ascii=False))
