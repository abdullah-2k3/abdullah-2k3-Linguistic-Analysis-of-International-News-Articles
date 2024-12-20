from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime

url = input("Enter url: ")
topic = input("Enter topic: ")
region = input("Enter region: ")
source = "Al Jazeera"

# Setup Selenium WebDriver in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless Chrome
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=chrome_options
)


driver.get(url)
time.sleep(3)  # Let the page load

data = {
    "Source": [],
    "Link": [],
    "Headline": [],
    "Description": [],
    "Date": [],
    "Timestamp": [],
    "Topic": [],
    "Author": [],
    "Region": [],
    "Article_Content": [],
}


def scrape_articles():
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "article.gc.u-clickable-card",
            )
        )
    )

    articles = driver.find_elements(By.CSS_SELECTOR, "article.gc.u-clickable-card")

    for article in articles:
        try:

            link_element = article.find_element(
                By.CSS_SELECTOR, "a.u-clickable-card__link"
            )
            link = link_element.get_attribute("href")
            print(f"Article Link: {link}")

            headline_element = article.find_element(
                By.CSS_SELECTOR, "h3.gc__title span"
            )
            headline = headline_element.text if headline_element else None

            description_element = article.find_element(
                By.CSS_SELECTOR, "div.gc__excerpt p"
            )
            description = description_element.text if description_element else None

            date_element = article.find_elements(
                By.CSS_SELECTOR, "div.gc__date__date span[aria-hidden='true']"
            )
            date = date_element[0].text if date_element else "Unknown"

            data["Source"].append(source)
            data["Link"].append(link)
            data["Headline"].append(headline)
            data["Description"].append(description)
            data["Date"].append(date)
            data["Timestamp"].append(datetime.now())
            data["Region"].append(region)
            data["Topic"].append(topic)
            data["Article_Content"].append("-")
            data["Author"].append("-")

        except Exception as e:
            print(f"Error scraping article: {e}")


scrape_articles()


def dismiss_cookie_banner():
    try:
        # Wait for the cookie consent banner to appear and click the "Accept" button
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button#onetrust-accept-btn-handler")
            )
        )
        accept_button.click()
        print("Cookie banner dismissed.")
    except Exception as e:
        print(f"Cookie banner not found or already dismissed: {e}")


# Dismiss the cookie banner if it exists
dismiss_cookie_banner()

# Loop for pagination or showing more content
for i in range(50):
    try:
        print(f"Page {i+1}...")

        # Wait for the "Show More" button to be clickable
        show_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.show-more-button.grid-full-width")
            )
        )

        # Click the "Show More" button to load more content
        show_more_button.click()
        time.sleep(3)  # Allow time for the new content to load

        # Scrape articles or load more content
        scrape_articles()

    except Exception as e:
        print(f"No more content to load or unable to click the 'Show More' button: {e}")
        break


df = pd.DataFrame(data)
df.to_csv(f"{source}_articles_{topic}.csv", index=False)
print("Articles scraped successfully!")


driver.quit()
