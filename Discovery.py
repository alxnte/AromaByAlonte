from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.fragrantica.com/search/")

def discover():
    try:
        while True:
            try:
                show_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Show more results')]")
                driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                driver.execute_script("arguments[0].click();", show_more_button)
                driver.implicitly_wait(5)
                time.sleep(5)
                WebDriverWait(driver, 15).until(EC.staleness_of(show_more_button))
                break

            except (NoSuchElementException):
                print("Exiting Loop")
                break

        # Perform scrolling and scraping after expanding all results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        html = driver.page_source
        html_soup = BeautifulSoup(html, 'html.parser')
        page = html_soup.find('span', class_="grid-x grid-margin-x grid-margin-y small-up-3 medium-up-2 large-up-4 perfumes-row text-center")

        frags = []

        for a in page.find_all('a', href=True):
            data = {}
            data["Name"] = a.text.strip()
            data["Link"] = a['href']
            frags.append(data)

        return frags

    except Exception as e:
        print(e)
        return []

def write_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

def main():
    try:
        fragrances = discover()
        if fragrances:
            write_to_csv(fragrances, 'fragrances.csv')
            print(f"Data saved to fragrances.csv")
        else:
            print("No fragrance data to save.")

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    main()