import json
import os
import time
from urllib.parse import urljoin
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load variables from .env file
load_dotenv()

INDEX_PAGE_URL = os.getenv("INDEX_PAGE_URL")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "vocab_lists.json")

# Delay (in seconds) between requests to prevent 429 Too Many Requests errors
REQUEST_DELAY = 2.0


def get_soup(url):
    """Utility helper to fetch a page and parse it with BeautifulSoup."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def load_existing_data(file_path):
    """Loads existing JSON file if present; returns an empty dictionary otherwise."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"Loaded existing data with {len(data)} lists from '{file_path}'.")
                return data
        except json.JSONDecodeError:
            print(f"Warning: Could not parse '{file_path}'. Starting fresh.")
    return {}


def save_data(file_path, data):
    """Saves vocabulary dictionary to JSON."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def scrape_vocab_lists(index_url, output_file):
    """Scrapes vocabulary lists linked from the index page, skipping existing entries."""
    if not index_url:
        raise ValueError("INDEX_PAGE_URL is missing. Please set it in your .env file.")

    # 1. Load pre-existing data to resume progress
    vocab_data = load_existing_data(output_file)

    print(f"Fetching index page: {index_url}")
    index_soup = get_soup(index_url)
    time.sleep(REQUEST_DELAY)

    links = index_soup.find_all("a", href=True)
    visited_urls = set()

    for link in links:
        page_url = urljoin(index_url, link["href"])

        if not page_url.startswith("http") or page_url in visited_urls:
            continue

        visited_urls.add(page_url)

        try:
            # Quick check: inspect target page title or link context if known,
            # or fetch page and verify if title already exists in vocab_data
            print(f"\nScraping: {page_url}")
            page_soup = get_soup(page_url)

            # Extract page title
            if page_soup.title and page_soup.title.string:
                title = page_soup.title.string.strip()
            elif page_soup.find("h1"):
                title = page_soup.find("h1").get_text(strip=True)
            else:
                title = page_url

            # 2. Check if this title is already in OUTPUT_FILE
            if title in vocab_data:
                print(f"  -> Skipping '{title}': Already saved in {output_file}.")
                continue

            # Extract words
            word_elements = page_soup.find_all(class_="wordlist-item")
            words = [
                elem.get_text(strip=True)
                for elem in word_elements
                if elem.get_text(strip=True)
            ]

            if words:
                vocab_data[title] = words
                print(f"  -> Extracted {len(words)} words under '{title}'")
                
                # Save progress immediately after each success
                save_data(output_file, vocab_data)
            else:
                print("  -> No '.wordlist-item' elements found, skipping.")

            # Respectful rate limiting
            time.sleep(REQUEST_DELAY)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"  -> Hit rate limit (429)! Waiting 10 seconds before resuming...")
                time.sleep(10)
            else:
                print(f"Failed to scrape {page_url}: {e}")
        except requests.RequestException as e:
            print(f"Failed to scrape {page_url}: {e}")

    print(f"\nDone! Total of {len(vocab_data)} lists saved in '{output_file}'.")


if __name__ == "__main__":
    scrape_vocab_lists(INDEX_PAGE_URL, OUTPUT_FILE)