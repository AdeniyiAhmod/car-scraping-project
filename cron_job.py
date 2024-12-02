from scrape_hrefs import scrape_car_hrefs
from scrape_data import scrape_car_data
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import logging

# Set up logging
logger = logging.getLogger('scraping')
logger.setLevel(logging.INFO)

# File handler for logging to file
file_handler = logging.FileHandler('scraping.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Stream handler for logging to console (HTML display)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter('%(asctime)s - %(message)s')
stream_handler.setFormatter(stream_formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Add headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")

# Specify the path to the ChromeDriver executable
chrome_driver_path = "C:/webDrivers/chromedriver.exe"
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Initialize the WebDriver
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

stop_scraping_flag = False

def main():
    global stop_scraping_flag
    logger.info("Starting scraping process")

    # Check if car_hrefs.csv exists
    if os.path.exists("car_hrefs.csv"):
        df_hrefs = pd.read_csv("car_hrefs.csv")
        existing_hrefs = df_hrefs["Car_Href"].tolist()
    else:
        existing_hrefs = []

    # Check if car_data.csv exists
    if os.path.exists("car_data.csv"):
        df_data = pd.read_csv("car_data.csv")
        if "Href" not in df_data.columns:
            df_data["Href"] = ""
        existing_data_hrefs = df_data["Href"].tolist()
    else:
        existing_data_hrefs = []

    # Scrape car hrefs
    new_hrefs = scrape_car_hrefs(driver)
    logger.info(f"Scraped {len(new_hrefs)} hrefs")

    # Save new hrefs to CSV
    all_hrefs = existing_hrefs + new_hrefs
    df = pd.DataFrame({"Car_Href": all_hrefs})
    df.to_csv("car_hrefs.csv", index=False)

    # Scrape car data for hrefs not in car_data.csv
    for href in all_hrefs:
        if href not in existing_data_hrefs:
            if stop_scraping_flag:
                logger.info("Scraping stopped by user")
                break
            scrape_car_data(driver, [href])
            logger.info(f"Scraped data for {href}")

    # Close the WebDriver
    driver.quit()

    logger.info("Scraping completed")

if __name__ == "__main__":
    main()
