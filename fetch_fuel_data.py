# fetch_fuel_data.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re # Import regex for more robust price extraction

# Define the CSV file where fuel price data will be stored
FUEL_DATA_FILE = 'fuel_prices.csv'

def fetch_and_save_data():
    """
    Fetches daily petrol and diesel prices for New Delhi from cardekho.com/fuel-price,
    parses them, and appends them to a CSV file.
    """
    url = 'https://www.cardekho.com/fuel-price' 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        petrol_price = 0.0
        diesel_price = 0.0
        
        # --- Robust Strategy for cardekho.com/fuel-price (based on the provided HTML) ---
        # The main content is within <div class="overviewWrap">
        # Inside that, <div class="contentHold gsc_row"> contains the fuel type sections.
        # Each fuel type section is a <div data-track-section="FuelType">

        # Find the main content holder
        content_hold_div = soup.find('div', class_='contentHold gsc_row')

        if not content_hold_div:
            print("Error: Could not find the main 'contentHold gsc_row' div.")
            return

        # 1. Find Petrol Price
        # Locate the div for Petrol prices using its data-track-section attribute
        petrol_section_div = content_hold_div.find('div', attrs={'data-track-section': 'Petrol'})
        petrol_table = None
        if petrol_section_div:
            # Find the table within this petrol section
            petrol_table_div = petrol_section_div.find('div', class_='table marginTop20')
            if petrol_table_div:
                petrol_table = petrol_table_div.find('table') # Get the actual table tag

        if petrol_table:
            # Iterate through rows to find 'New Delhi'
            for row in petrol_table.find_all('tr'):
                # The city name is inside an <a> tag within the first <td>
                city_cell = row.find('td')
                if city_cell and city_cell.find('a', string='New Delhi'):
                    # The price is in the next sibling <td>
                    price_cell = city_cell.find_next_sibling('td')
                    if price_cell:
                        price_text = price_cell.get_text(strip=True).replace('₹', '').strip()
                        try:
                            petrol_price = float(price_text)
                            print(f"Found Petrol Price for New Delhi: {petrol_price}")
                        except ValueError:
                            print(f"Could not convert petrol price '{price_text}' to float for Delhi.")
                        break # Found petrol price, exit loop
        else:
            print("Petrol price table or its section not found.")


        # 2. Find Diesel Price
        # Locate the div for Diesel prices using its data-track-section attribute
        diesel_section_div = content_hold_div.find('div', attrs={'data-track-section': 'Diesel'})
        diesel_table = None
        if diesel_section_div:
            # Find the table within this diesel section
            diesel_table_div = diesel_section_div.find('div', class_='table marginTop20')
            if diesel_table_div:
                diesel_table = diesel_table_div.find('table') # Get the actual table tag

        if diesel_table:
            # Iterate through rows to find 'New Delhi'
            for row in diesel_table.find_all('tr'):
                city_cell = row.find('td')
                if city_cell and city_cell.find('a', string='New Delhi'):
                    price_cell = city_cell.find_next_sibling('td')
                    if price_cell:
                        price_text = price_cell.get_text(strip=True).replace('₹', '').strip()
                        try:
                            diesel_price = float(price_text)
                            print(f"Found Diesel Price for New Delhi: {diesel_price}")
                        except ValueError:
                            print(f"Could not convert diesel price '{price_text}' to float for Delhi.")
                        break # Found diesel price, exit loop
        else:
            print("Diesel price table or its section not found.")


        # Check if at least one price was successfully found
        if petrol_price == 0.0 and diesel_price == 0.0:
            print("Could not find any fuel prices for New Delhi on cardekho.com. Website structure might have changed or data not present.")
            return 

        today = datetime.now().strftime('%Y-%m-%d')
        
        new_data = pd.DataFrame([
            {'Date': today, 'City': 'New Delhi', 'FuelType': 'Petrol', 'Price': petrol_price},
            {'Date': today, 'City': 'New Delhi', 'FuelType': 'Diesel', 'Price': diesel_price}
        ])

        if os.path.exists(FUEL_DATA_FILE):
            existing_data = pd.read_csv(FUEL_DATA_FILE)
            existing_data['Date'] = pd.to_datetime(existing_data['Date'])

            if not existing_data[(existing_data['Date'] == pd.to_datetime(today)) & (existing_data['City'] == 'New Delhi')].empty:
                print(f"Data for {today} in New Delhi already exists. Skipping update.")
                return
            
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            updated_data = new_data
        
        updated_data.to_csv(FUEL_DATA_FILE, index=False)
        print(f"Successfully fetched and saved data for {today}")

    except requests.exceptions.RequestException as e:
        print(f"Network error during data fetch: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
