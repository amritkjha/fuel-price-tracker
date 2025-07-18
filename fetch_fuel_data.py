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
        # The structure on goodreturns.in often involves tables.
        # We'll look for the table that contains city-wise prices and then find New Delhi's row.
        
        petrol_price = 0.0
        diesel_price = 0.0
        
        # Find the table containing "Petrol Price in Indian Metro Cities & State Capitals"
        # This might be identified by a specific heading or a class on the table/parent div.
        # Let's assume it's the first table after a certain heading or a specific class.
        
        # A more robust way: find the heading first, then look for the next table
        target_heading = soup.find('h2', text=re.compile(r'Petrol Price in Indian Metro Cities & State Capitals', re.IGNORECASE))
        price_table = None
        if target_heading:
            price_table = target_heading.find_next('table')
        
        if price_table:
            # Find all rows in the table body
            rows = price_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if cells and len(cells) > 0:
                    city_name = cells[0].get_text(strip=True)
                    if city_name == 'New Delhi':
                        # Assuming structure: City | Price | Change | City | Price | Change
                        # Petrol price is usually the 2nd cell, Diesel is the 4th cell.
                        if len(cells) >= 2: # Petrol price cell
                            petrol_price_str = cells[1].get_text(strip=True).replace('₹', '').split(' ')[0].strip()
                            petrol_price = float(petrol_price_str)
                        if len(cells) >= 4: # Diesel price cell
                            diesel_price_str = cells[3].get_text(strip=True).replace('₹', '').split(' ')[0].strip()
                            diesel_price = float(diesel_price_str)
                        break # Found New Delhi, exit loop
            
            if petrol_price == 0.0 and diesel_price == 0.0:
                print("Could not find New Delhi prices in the expected table structure.")
                return

        else:
            print("Could not find the main fuel price table on the page.")
            return

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
    except AttributeError:
        print("Scraping selectors might be outdated or data not found. Please check the website's HTML structure.")
    except ValueError as e:
        print(f"Error converting price to float: {e}. Data might be malformed or not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
