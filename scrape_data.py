from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_car_data(driver, car_hrefs):
    car_data = []

    for href in car_hrefs:
        url = f"https://autochek.africa{href}"
        retries = 3
        while retries > 0:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "car-name"))
                )
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                price_element = soup.select_one('div.MuiStack-root.css-k4n1v7 p.MuiTypography-root') or soup.select_one('div.MuiStack-root.css-1abzdwk p.MuiTypography-root')
                price = price_element.text.strip() if price_element else ''
                
                car_name = soup.select_one('h5#car-name').text.strip()
                car_type = soup.select_one('div.MuiChip-root.css-f1a4rn span.MuiChip-label').text.strip()
                mileage = soup.select_one('div.MuiChip-root.css-1uau0i1 span.MuiChip-label').text.strip()
                
                details = {}
                for li in soup.select('ul.MuiList-root li'):
                    key = li.select_one('div.MuiListItemText-root span.MuiTypography-root').text.strip()
                    value = li.select_one('div.MuiListItemSecondaryAction-root p.MuiTypography-root').text.strip()
                    details[key] = value
                
                engine = details.get('Engine', '')
                transmission = details.get('Transmission', '')
                fuel_type = details.get('Fuel Type', '')
                interior_color = details.get('Interior Color', '')
                exterior_color = details.get('Exterior Color', '')
                vin = details.get('VIN', '')
                vehicle_id = details.get('Vehicle ID:', '')
                
                features = [chip.text.strip() for chip in soup.select('div.MuiGrid-root div.MuiChip-root span.MuiChip-label')]
                features = ', '.join(features)
                
                car_id_location = soup.select_one('div#state-city')
                car_id = car_id_location.select('span')[0].text.replace('Vehicle ID: ', '').strip() if car_id_location else ''
                location = car_id_location.select('span')[1].text.strip() if car_id_location and len(car_id_location.select('span')) > 1 else ''
                
                car_data.append({
                    'Href': href,
                    'Price': price,
                    'Car Name': car_name,
                    'Type': car_type,
                    'Mileage': mileage,
                    'Engine': engine,
                    'Transmission': transmission,
                    'Fuel Type': fuel_type,
                    'Interior Color': interior_color,
                    'Exterior Color': exterior_color,
                    'VIN': vin,
                    'Vehicle ID': vehicle_id,
                    'Location': location,
                    'Features': features
                })
                
                # Save data incrementally
                if os.path.exists("car_data.csv"):
                    df_existing = pd.read_csv("car_data.csv")
                    df_new = pd.DataFrame(car_data)
                    df_combined = pd.concat([df_existing, df_new])
                    df_combined.to_csv("car_data.csv", index=False)
                else:
                    df_cars = pd.DataFrame(car_data)
                    df_cars.to_csv("car_data.csv", index=False)
                
                break
            
            except (TimeoutException, WebDriverException) as e:
                print(f"Error: {e}. Retrying...")
                retries -= 1
                time.sleep(5)

    return car_data
