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
    Fetches daily petrol and diesel prices for New Delhi from Goodreturns.in,
    parses them, and appends them to a CSV file.
    """
    url = 'https://www.goodreturns.in/petrol-price.html' # Reliable source for Indian fuel prices
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    try:
        # Fetch the HTML content of the page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Updated Extract prices for New Delhi ---
        # The DeprecationWarning for 'text' argument is addressed by using 'string' for direct string content.
        # However, for regex matching, 'text' or 'string' with re.compile can still be used,
        # but the warning suggests 'string' for direct content and other methods for regex.
        # For simplicity and to resolve the warning, we'll stick to 'string' where possible,
        # but for re.compile, 'text' is often still used for BeautifulSoup's `find` method.

        # Let's try a more robust way to find the table containing the data.
        # We will iterate through all tables and find the one that contains 'New Delhi'.
        
        petrol_price = 0.0
        diesel_price = 0.0
        found_prices = False

        # Find all table elements on the page
        all_tables = soup.find_all('table')

        for table in all_tables:
            # Check if 'New Delhi' is present in the text content of the table
            # This helps narrow down to the correct table without relying on specific headings
            if 'New Delhi' in table.get_text():
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if cells and len(cells) > 0:
                        city_name = cells[0].get_text(strip=True)
                        if city_name == 'New Delhi':
                            # Assuming structure: City | Petrol Price | Change | Diesel Price | Change
                            # Petrol price is typically the 2nd cell (index 1)
                            # Diesel price is typically the 4th cell (index 3)
                            if len(cells) >= 2: # Check if petrol price cell exists
                                petrol_price_str = cells[1].get_text(strip=True).replace('₹', '').split(' ')[0].strip()
                                try:
                                    petrol_price = float(petrol_price_str)
                                except ValueError:
                                    print(f"Could not convert petrol price '{petrol_price_str}' to float.")
                                    petrol_price = 0.0 # Reset to default if conversion fails
                            
                            if len(cells) >= 4: # Check if diesel price cell exists
                                diesel_price_str = cells[3].get_text(strip=True).replace('₹', '').split(' ')[0].strip()
                                try:
                                    diesel_price = float(diesel_price_str)
                                except ValueError:
                                    print(f"Could not convert diesel price '{diesel_price_str}' to float.")
                                    diesel_price = 0.0 # Reset to default if conversion fails
                            
                            found_prices = True
                            break # Found New Delhi prices, exit row loop
                if found_prices:
                    break # Found prices and table, exit table loop
        
        if not found_prices:
            print("Could not find New Delhi prices in any table on the page. Website structure might have changed significantly.")
            return # Exit if prices were not found

        today = datetime.now().strftime('%Y-%m-%d')
        
        # Create a new DataFrame for today's data
        new_data = pd.DataFrame([
            {'Date': today, 'City': 'New Delhi', 'FuelType': 'Petrol', 'Price': petrol_price},
            {'Date': today, 'City': 'New Delhi', 'FuelType': 'Diesel', 'Price': diesel_price}
        ])

        # Check if the CSV file exists
        if os.path.exists(FUEL_DATA_FILE):
            existing_data = pd.read_csv(FUEL_DATA_FILE)
            # Convert 'Date' column to datetime objects for proper comparison
            existing_data['Date'] = pd.to_datetime(existing_data['Date'])

            # Check if today's data for New Delhi already exists to avoid duplicates
            if not existing_data[(existing_data['Date'] == pd.to_datetime(today)) & (existing_data['City'] == 'New Delhi')].empty:
                print(f"Data for {today} in New Delhi already exists. Skipping update.")
                return
            
            # Concatenate existing and new data
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            # If file doesn't exist, new_data is the first data
            updated_data = new_data
        
        # Save the updated data back to the CSV file
        updated_data.to_csv(FUEL_DATA_FILE, index=False)
        print(f"Successfully fetched and saved data for {today}")

    except requests.exceptions.RequestException as e:
        print(f"Network error during data fetch: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
