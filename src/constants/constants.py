import os

# Get the root directory of the project (adjust if needed)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources"))

# File paths
FILTERS_FILE = os.path.join(BASE_DIR, "filters.json")
RESULTS_FILE = os.path.join(BASE_DIR, "results.json")
LINKS_FILE = os.path.join(BASE_DIR, "scraped_links.txt")

# Ensure the directory exists
os.makedirs(BASE_DIR, exist_ok=True)
