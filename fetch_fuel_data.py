# fetch_fuel_data.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re
import time

# Define the CSV file where fuel price data will be stored
FUEL_DATA_FILE = 'fuel_prices.csv'

def scrape_goodreturns():
    """
    Try to scrape from goodreturns.in - seems to have clean structure
    """
    print("Trying goodreturns.in...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        # Try petrol price
        petrol_url = 'https://www.goodreturns.in/petrol-price-in-new-delhi.html'
        response = requests.get(petrol_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        petrol_price = None
        # Look for price patterns in the page
        price_elements = soup.find_all(string=re.compile(r'₹.*?\d+\.?\d*'))
        for element in price_elements:
            price_match = re.search(r'₹\s*(\d+\.?\d*)', element)
            if price_match:
                potential_price = float(price_match.group(1))
                # Reasonable range for petrol prices (₹80-120)
                if 80 <= potential_price <= 120:
                    petrol_price = potential_price
                    print(f"Found petrol price from goodreturns: ₹{petrol_price}")
                    break
        
        time.sleep(1)  # Be respectful to the server
        
        # Try diesel price
        diesel_url = 'https://www.goodreturns.in/diesel-price-in-new-delhi.html'
        response = requests.get(diesel_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        diesel_price = None
        price_elements = soup.find_all(string=re.compile(r'₹.*?\d+\.?\d*'))
        for element in price_elements:
            price_match = re.search(r'₹\s*(\d+\.?\d*)', element)
            if price_match:
                potential_price = float(price_match.group(1))
                # Reasonable range for diesel prices (₹70-110)
                if 70 <= potential_price <= 110:
                    diesel_price = potential_price
                    print(f"Found diesel price from goodreturns: ₹{diesel_price}")
                    break
        
        return petrol_price, diesel_price
        
    except Exception as e:
        print(f"Error scraping goodreturns: {e}")
        return None, None

def scrape_acko():
    """
    Try to scrape from acko.com - alternative source
    """
    print("Trying acko.com...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        # Try diesel price from Acko (they seem to have good data)
        diesel_url = 'https://www.acko.com/fuel/diesel-price-in-new-delhi/'
        response = requests.get(diesel_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        diesel_price = None
        # Look for the main price display
        page_text = soup.get_text()
        
        # Find patterns like "₹87.67 per litre" or "87.67/Ltr"
        price_patterns = [
            r'₹(\d+\.?\d*)\s*per\s*litre',
            r'₹(\d+\.?\d*)/[Ll]tr',
            r'₹(\d+\.?\d*)\s*per\s*liter',
            r'stands at ₹(\d+\.?\d*)',
            r'₹\s*(\d+\.?\d*)\s*per\s*litre'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                if 70 <= potential_price <= 110:  # Reasonable diesel price range
                    diesel_price = potential_price
                    print(f"Found diesel price from acko: ₹{diesel_price}")
                    break
            if diesel_price:
                break
        
        # Try petrol from a different URL or source
        # For now, return what we found
        return None, diesel_price
        
    except Exception as e:
        print(f"Error scraping acko: {e}")
        return None, None

def scrape_bankbazaar():
    """
    Try to scrape from bankbazaar.com
    """
    print("Trying bankbazaar.com...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        petrol_url = 'https://www.bankbazaar.com/fuel/petrol-price-delhi.html'
        response = requests.get(petrol_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        petrol_price = None
        # Look for price in various formats
        page_text = soup.get_text()
        
        price_patterns = [
            r'₹\s*(\d+\.?\d*)\s*per\s*litre',
            r'Rs\.?\s*(\d+\.?\d*)\s*per\s*litre',
            r'₹\s*(\d+\.?\d*)/[Ll]itre',
            r'Rs\.?\s*(\d+\.?\d*)/[Ll]itre'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                if 80 <= potential_price <= 120:  # Reasonable petrol price range
                    petrol_price = potential_price
                    print(f"Found petrol price from bankbazaar: ₹{petrol_price}")
                    break
            if petrol_price:
                break
        
        return petrol_price, None
        
    except Exception as e:
        print(f"Error scraping bankbazaar: {e}")
        return None, None

def scrape_iocl():
    """
    Try to scrape from iocl.com (Indian Oil Corporation)
    """
    print("Trying iocl.com...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        url = 'https://iocl.com/petrol-diesel-price'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for Delhi prices
        page_text = soup.get_text().lower()
        
        petrol_price = None
        diesel_price = None
        
        # Find Delhi section
        delhi_section = re.search(r'delhi.*?(?=mumbai|chennai|kolkata|bangalore|\n\n)', page_text, re.DOTALL)
        if delhi_section:
            delhi_text = delhi_section.group()
            prices = re.findall(r'(\d+\.?\d*)', delhi_text)
            
            if len(prices) >= 2:
                # First price usually petrol, second diesel
                potential_petrol = float(prices[0])
                potential_diesel = float(prices[1])
                
                if 80 <= potential_petrol <= 120:
                    petrol_price = potential_petrol
                    print(f"Found petrol price from iocl: ₹{petrol_price}")
                
                if 70 <= potential_diesel <= 110:
                    diesel_price = potential_diesel
                    print(f"Found diesel price from iocl: ₹{diesel_price}")
        
        return petrol_price, diesel_price
        
    except Exception as e:
        print(f"Error scraping iocl: {e}")
        return None, None

def fetch_and_save_data():
    """
    Fetches daily petrol and diesel prices for New Delhi using multiple sources
    """
    print("Starting fuel price fetch process...")
    print("=" * 50)
    
    petrol_price = None
    diesel_price = None
    
    # Try multiple sources until we get both prices
    sources = [
        scrape_goodreturns,
        scrape_acko,
        scrape_bankbazaar,
        scrape_iocl
    ]
    
    for source_func in sources:
        if petrol_price is None or diesel_price is None:
            try:
                p_price, d_price = source_func()
                
                if p_price is not None and petrol_price is None:
                    petrol_price = p_price
                
                if d_price is not None and diesel_price is None:
                    diesel_price = d_price
                
                # Small delay between requests to be respectful
                time.sleep(1)
                
            except Exception as e:
                print(f"Error with {source_func.__name__}: {e}")
                continue
        
        # If we have both prices, we can stop
        if petrol_price is not None and diesel_price is not None:
            break
    
    print("=" * 50)
    
    # Check what we found
    if petrol_price is None and diesel_price is None:
        print("ERROR: Could not fetch any fuel prices from any source.")
        print("All websites may be down or have changed their structure.")
        return
    
    if petrol_price is None:
        print("WARNING: Could not fetch petrol price, setting to 0.0")
        petrol_price = 0.0
    
    if diesel_price is None:
        print("WARNING: Could not fetch diesel price, setting to 0.0") 
        diesel_price = 0.0
    
    print(f"Final prices - Petrol: ₹{petrol_price}, Diesel: ₹{diesel_price}")
    
    # Save data to CSV
    today = datetime.now().strftime('%Y-%m-%d')
    
    new_data = pd.DataFrame([
        {'Date': today, 'City': 'New Delhi', 'FuelType': 'Petrol', 'Price': petrol_price},
        {'Date': today, 'City': 'New Delhi', 'FuelType': 'Diesel', 'Price': diesel_price}
    ])
    
    # Handle CSV file operations with proper error handling
    if os.path.exists(FUEL_DATA_FILE):
        try:
            existing_data = pd.read_csv(FUEL_DATA_FILE)
            
            # Check if the CSV file is empty or has no columns
            if existing_data.empty or len(existing_data.columns) == 0:
                print("Existing CSV file is empty or corrupted, creating new one.")
                updated_data = new_data
            else:
                existing_data['Date'] = pd.to_datetime(existing_data['Date']).dt.strftime('%Y-%m-%d')
                
                # Check if today's data already exists
                today_exists = existing_data[
                    (existing_data['Date'] == today) & 
                    (existing_data['City'] == 'New Delhi')
                ]
                
                if not today_exists.empty:
                    print(f"Data for {today} in New Delhi already exists. Skipping update.")
                    return
                
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        
        except (pd.errors.EmptyDataError, pd.errors.ParserError, KeyError) as e:
            print(f"Error reading existing CSV file: {e}")
            print("Creating new CSV file.")
            updated_data = new_data
    else:
        print("Creating new CSV file.")
        updated_data = new_data
    
    # Save to CSV
    updated_data.to_csv(FUEL_DATA_FILE, index=False)
    print(f"Successfully saved data for {today} to {FUEL_DATA_FILE}")
    
    # Show what was saved
    print("\nData saved:")
    print(new_data.to_string(index=False))

if __name__ == "__main__":
    fetch_and_save_data()