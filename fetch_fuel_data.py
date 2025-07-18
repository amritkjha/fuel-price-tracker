# fetch_fuel_data.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# Define the CSV file where fuel price data will be stored
FUEL_DATA_FILE = 'fuel_prices.csv'

def fetch_and_save_data():
    """
    Fetches daily petrol and diesel prices for New Delhi from Goodreturns.in,
    parses them, and appends them to a CSV file.
    """
    url = 'https://www.goodreturns.in/petrol-price.html' # Reliable source for Indian fuel prices
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Fetch the HTML content of the page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Extract prices for New Delhi ---
        # These selectors are based on the structure of goodreturns.in as of July 2025.
        # **IMPORTANT:** These selectors may change if the website updates its structure.
        # You might need to inspect the page manually using browser developer tools
        # (right-click -> Inspect) to find the correct `<td>` elements or classes.

        # Find the row for New Delhi. Assuming the city name is in a <td> tag.
        # Then navigate to its siblings to find petrol and diesel prices.
        
        delhi_row = None
        # Look for the table that contains city-wise prices
        # This might require finding a specific table or a parent div
        tables = soup.find_all('table')
        for table in tables:
            if "New Delhi" in table.get_text(): # Simple check to find the right table
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if cells and cells[0].get_text(strip=True) == 'New Delhi':
                        delhi_row = cells
                        break
            if delhi_row:
                break

        petrol_price = 0.0
        diesel_price = 0.0

        if delhi_row and len(delhi_row) >= 4: # Assuming at least 4 columns: City, Petrol Price, Change, Diesel Price
            # Petrol price is typically the second column (index 1)
            petrol_price_str = delhi_row[1].get_text(strip=True).replace('₹', '').strip()
            petrol_price = float(petrol_price_str)

            # Diesel price is typically the fourth column (index 3)
            diesel_price_str = delhi_row[3].get_text(strip=True).replace('₹', '').strip()
            diesel_price = float(diesel_price_str)
        else:
            print("Could not find New Delhi prices or table structure changed.")
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
        print(f"Error converting price to float: {e}. Data might be malformed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
