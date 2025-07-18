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
        found_petrol = False
        found_diesel = False

        # --- Strategy for cardekho.com/fuel-price ---
        # Based on inspection, prices are often found within specific tables or divs
        # that list prices for major cities. We'll look for a table or a div
        # that contains city-wise data.

        # Cardekho's fuel price page often lists major cities directly.
        # We'll try to find the specific elements for "Delhi".
        
        # Look for the main container that holds the fuel price cards for cities.
        # This might be a div with a class like 'fuel-price-cities' or similar.
        # Then, find the specific card for 'Delhi'.

        # Example selector based on common patterns for such sites:
        # Find the div containing city-wise price cards
        city_price_container = soup.find('div', class_='gsc_col-md-12') # This is a common large container
        
        if city_price_container:
            # Within this container, look for individual city price cards/rows
            # These might be divs with classes like 'fuel-price-card-item' or 'fuel-price-city-row'
            # Or, they might be directly in a table. Let's try finding the "Delhi" row.
            
            # Search for the specific city block for Delhi
            # Cardekho often uses `div` elements with class `fuel-price-widget` or similar
            # and then `li` elements for each city.
            
            # Let's try to find the specific city name and then its price siblings.
            # The structure might be:
            # <div class="city-name-class">Delhi</div>
            # <div class="petrol-price-class">₹XX.YY</div>
            # <div class="diesel-price-class">₹XX.YY</div>

            # A common pattern is to have a list of cities with their prices.
            # We'll look for the specific city name and then its associated prices.

            # Find the main table or list that contains the city prices
            # On cardekho, it seems prices are displayed in a structured way, often in tables or lists.
            # Let's try to find the specific elements for Delhi.

            # Attempt to find the row/div for Delhi
            # This is a common pattern: find an element with specific text, then navigate its siblings/parents
            
            # Find the 'New Delhi' city name within a <span> or <div>
            delhi_petrol_span = soup.find('span', text=re.compile(r'Delhi Petrol Price', re.IGNORECASE))
            delhi_diesel_span = soup.find('span', text=re.compile(r'Delhi Diesel Price', re.IGNORECASE))

            if delhi_petrol_span:
                # Assuming the price is in a sibling element or a child of a common parent
                # This needs careful inspection. Let's assume price is in a <b> tag next to it.
                price_element = delhi_petrol_span.find_next_sibling('b')
                if price_element:
                    price_match = re.search(r'([\d.]+)', price_element.get_text(strip=True))
                    if price_match:
                        try:
                            petrol_price = float(price_match.group(1))
                            found_petrol = True
                        except ValueError:
                            print(f"Could not convert petrol price '{price_match.group(1)}' to float for Delhi.")
            
            if delhi_diesel_span:
                price_element = delhi_diesel_span.find_next_sibling('b')
                if price_element:
                    price_match = re.search(r'([\d.]+)', price_element.get_text(strip=True))
                    if price_match:
                        try:
                            diesel_price = float(price_match.group(1))
                            found_diesel = True
                        except ValueError:
                            print(f"Could not convert diesel price '{price_match.group(1)}' to float for Delhi.")

        if not (found_petrol or found_diesel):
            print("Could not find New Delhi prices on cardekho.com. Website structure might have changed or data not present.")
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
