from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os

def scrape_car_hrefs(driver):
    driver.get("https://autochek.africa/ng/cars-for-sale")
    all_car_hrefs = []

    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "MuiBox-root"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for box in soup.select('div.MuiBox-root.css-1jke4yk'):
            car_link = box.find('a', href=True)
            if car_link and not car_link['href'].startswith('https://api.whatsapp.com'):
                all_car_hrefs.append(car_link['href'])

        next_page_button = driver.find_element(By.XPATH, '//button[@aria-label="Go to next page"]')
        if next_page_button.is_enabled():
            driver.execute_script("arguments[0].click();", next_page_button)
        else:
            break

    # Save hrefs incrementally
    if os.path.exists("car_hrefs.csv"):
        df_existing = pd.read_csv("car_hrefs.csv")
        existing_hrefs = df_existing["Car_Href"].tolist()
    else:
        existing_hrefs = []

    new_hrefs = [href for href in all_car_hrefs if href not in existing_hrefs]
    if new_hrefs:
        df_new = pd.DataFrame({"Car_Href": new_hrefs})
        df_combined = pd.concat([df_existing, df_new])
        df_combined.to_csv("car_hrefs.csv", index=False)

    return new_hrefs
