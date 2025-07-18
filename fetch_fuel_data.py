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
    Fetches daily petrol and diesel prices for New Delhi from mypetrolprice.com,
    parses them, and appends them to a CSV file.
    """
    url = 'https://www.mypetrolprice.com/' 
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
        found_petrol = False
        found_diesel = False

        # --- Revised strategy for mypetrolprice.com ---
        # Look for the main container that holds city-wise prices for Petrol and Diesel.
        # These are usually within a div with a specific class, and then individual city items.

        # Find the Petrol Prices section
        # The structure often has a heading like <h2>Petrol Prices</h2> followed by the actual prices
        # Or a specific div that contains the list of cities and their prices.
        
        # Strategy 1: Find the main city-wise price container (common pattern on this site)
        # Assuming prices are within a div with class 'CityWisePrice' or similar,
        # and each city is an item within it.
        
        # Find the main container for Petrol prices
        petrol_main_div = soup.find('div', class_='fuel-price-card') # This div contains the heading and city list
        if petrol_main_div:
            # Find the <h2> tag with "Petrol Prices" text inside this div
            petrol_heading = petrol_main_div.find('h2', string=re.compile(r'Petrol Prices', re.IGNORECASE))
            if petrol_heading:
                # The actual list of cities is usually in a sibling div or a child div of the parent
                # Let's try to find the list of cities (e.g., ul or div with city items)
                # A common structure is <div class="CityWisePrice">...</div>
                # Let's assume the actual list of cities is in a div with class 'CityWisePrice'
                # which is a sibling to the 'fuel-price-card' or a child within it.
                
                # More direct approach: Find all elements that represent a city's petrol price
                # On mypetrolprice.com, it seems to be in a structure like:
                # <div class="CityWisePrice-item">
                #   <div class="CityWisePrice-city">Delhi</div>
                #   <div class="CityWisePrice-price">₹94.77</div>
                # </div>
                
                # Find all city price items within the petrol section
                petrol_city_items = petrol_main_div.find_all('div', class_='CityWisePrice-item')
                for item in petrol_city_items:
                    city_div = item.find('div', class_='CityWisePrice-city')
                    if city_div and city_div.get_text(strip=True) == 'Delhi':
                        price_div = item.find('div', class_='CityWisePrice-price')
                        if price_div:
                            price_match = re.search(r'₹\s*([\d.]+)', price_div.get_text(strip=True))
                            if price_match:
                                try:
                                    petrol_price = float(price_match.group(1))
                                    found_petrol = True
                                except ValueError:
                                    print(f"Could not convert petrol price '{price_match.group(1)}' to float for Delhi.")
                                break # Found Delhi petrol price, exit loop
            
        # Find the main container for Diesel prices
        # Similar logic for diesel, assuming it's in a separate but similar structure
        diesel_main_div = soup.find('div', class_='fuel-price-card', string=re.compile(r'Diesel Prices', re.IGNORECASE)) # Re-evaluating this selector
        # The previous `string=re.compile` on `fuel-price-card` might be the issue.
        # Let's find the diesel block by its heading, then look for its parent/sibling container
        
        # A safer way to get the diesel block: Find all 'fuel-price-card' and check their h2 children
        all_fuel_price_cards = soup.find_all('div', class_='fuel-price-card')
        diesel_prices_section = None
        for card in all_fuel_price_cards:
            if card.find('h2', string=re.compile(r'Diesel Prices', re.IGNORECASE)):
                diesel_prices_section = card
                break

        if diesel_prices_section:
            diesel_city_items = diesel_prices_section.find_all('div', class_='CityWisePrice-item')
            for item in diesel_city_items:
                city_div = item.find('div', class_='CityWisePrice-city')
                if city_div and city_div.get_text(strip=True) == 'Delhi':
                    price_div = item.find('div', class_='CityWisePrice-price')
                    if price_div:
                        price_match = re.search(r'₹\s*([\d.]+)', price_div.get_text(strip=True))
                        if price_match:
                            try:
                                diesel_price = float(price_match.group(1))
                                found_diesel = True
                            except ValueError:
                                print(f"Could not convert diesel price '{price_match.group(1)}' to float for Delhi.")
                            break # Found Delhi diesel price, exit loop

        if not (found_petrol or found_diesel):
            print("Could not find New Delhi prices on mypetrolprice.com. Website structure might have changed or data not present.")
            # If neither petrol nor diesel prices for Delhi were found, return.
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
