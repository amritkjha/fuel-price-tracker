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
    # Changed URL to mypetrolprice.com for potentially easier static scraping
    url = 'https://www.mypetrolprice.com/' 
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

        # --- Extract prices for New Delhi from mypetrolprice.com ---
        # Based on inspection of mypetrolprice.com, prices for major cities are often
        # in specific list items or divs. We'll try to locate the "Delhi" entry.

        petrol_price = 0.0
        diesel_price = 0.0
        found_prices = False

        # Find the main container for petrol prices
        petrol_block = soup.find('div', class_='fuel-price-card', string=re.compile(r'Petrol Prices', re.IGNORECASE))
        if petrol_block:
            # Look for the specific list item or div containing Delhi's petrol price
            # This selector needs to be precise based on the actual HTML
            delhi_petrol_entry = petrol_block.find('li', string=re.compile(r'Delhi', re.IGNORECASE))
            if delhi_petrol_entry:
                # Extract price using regex, as it might be mixed with other text/symbols
                price_match = re.search(r'₹\s*([\d.]+)', delhi_petrol_entry.get_text(strip=True))
                if price_match:
                    try:
                        petrol_price = float(price_match.group(1))
                        found_prices = True
                    except ValueError:
                        print(f"Could not convert petrol price '{price_match.group(1)}' to float.")

        # Find the main container for diesel prices
        diesel_block = soup.find('div', class_='fuel-price-card', string=re.compile(r'Diesel Prices', re.IGNORECASE))
        if diesel_block:
            # Look for the specific list item or div containing Delhi's diesel price
            delhi_diesel_entry = diesel_block.find('li', string=re.compile(r'Delhi', re.IGNORECASE))
            if delhi_diesel_entry:
                # Extract price using regex
                price_match = re.search(r'₹\s*([\d.]+)', delhi_diesel_entry.get_text(strip=True))
                if price_match:
                    try:
                        diesel_price = float(price_match.group(1))
                        found_prices = True # Set to True if at least one price is found
                    except ValueError:
                        print(f"Could not convert diesel price '{price_match.group(1)}' to float.")
        
        if not found_prices:
            print("Could not find New Delhi prices on mypetrolprice.com. Website structure might have changed or data not present.")
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
