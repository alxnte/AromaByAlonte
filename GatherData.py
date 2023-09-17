import requests
from bs4 import BeautifulSoup
import csv
import re
import time

# Function to extract notes from a notes list
def extract_notes_list(notes_list):
    pattern = r'</a>([^<]+)'
    notes_list = str(notes_list)
    matches = re.findall(pattern, notes_list)
    words = [match.strip() for match in matches]
    return words

# Function to gather data for a given URL with retries and incremental wait time to combat rate limit failures
def gather_data(url, max_retries=5):
    agent = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    
    retries = 0
    wait_time = 60  # Initial wait time

    while retries < max_retries:
        response = requests.get(url, headers=agent)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            fragrance_elements = soup.find_all("div", class_="grid-x bg-white grid-padding-x grid-padding-y")

            fragrances = []

            for fragrance_element in fragrance_elements:
                designer = fragrance_element.find("span", itemprop="name", class_="vote-button-name").text.strip()

                notes = []
                notes_container = fragrance_element.find("div", id="pyramid")
                top_notes = notes_container.find("b", text="Top Notes")
                middle_notes = notes_container.find("b", text="Middle Notes")
                base_notes = notes_container.find("b", text="Base Notes")

                if top_notes:
                    top_notes_list = top_notes.find_next("div")
                    notes += extract_notes_list(top_notes_list)

                if middle_notes:
                    middle_notes_list = middle_notes.find_next("div")
                    notes += extract_notes_list(middle_notes_list)

                if base_notes:
                    base_notes_list = base_notes.find_next("div")
                    notes += extract_notes_list(base_notes_list)

                fragrances.append({
                    "Designer": designer,
                    "Notes": notes
                })

            return fragrances
        else:
            print(f"Failed to retrieve the webpage for URL: {url}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
            wait_time *= 2  # Double the wait time for the next retry

    print(f"Max retries reached. Failed to retrieve the webpage for URL: {url}")
    return []

# Scraping for each fragrance
all_fragrances = []
for i, fragrance in enumerate(fragrance_data, start=1):
    fragrance_name = fragrance["Name"]
    fragrance_url = fragrance["Link"]
    fragrances = gather_data(fragrance_url)

    if fragrances:
        for f in fragrances:
            f["Name"] = fragrance_name
        all_fragrances.extend(fragrances)

    # To avoid rate limiting, wait 60 seconds after loading 10 pages 
    if i % 10 == 0:
        print(f"Processed {i} entries. Waiting for 60 seconds...")
        time.sleep(60)
