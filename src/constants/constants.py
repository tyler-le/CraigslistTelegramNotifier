import os

LOCATIONS = ["New York", "San Francisco", "Los Angeles", "Chicago", "Miami"]
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources"))
FILTERS_FILE = os.path.join(BASE_DIR, "filters.json")
RESULTS_FILE = os.path.join(BASE_DIR, "results.json")
LINKS_FILE = os.path.join(BASE_DIR, "scraped_links.txt")
os.makedirs(BASE_DIR, exist_ok=True)