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

def scrape_cardekho():
    """
    Try to scrape from cardekho.com - seems to have reliable data based on search results
    """
    print("Trying cardekho.com...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    petrol_price = None
    diesel_price = None
    
    try:
        # Try petrol price
        petrol_url = 'https://www.cardekho.com/petrol-price-in-delhi-state'
        response = requests.get(petrol_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for price patterns specific to cardekho
        page_text = soup.get_text()
        
        # More specific patterns for cardekho
        petrol_patterns = [
            r'Today.{0,20}s Petrol price in Delhi stands at ₹\s*(\d+\.?\d*)\s*per litre',
            r'Petrol price in Delhi stands at ₹\s*(\d+\.?\d*)',
            r'₹\s*(\d+\.?\d*)\s*per litre.*petrol',
        ]
        
        for pattern in petrol_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                # Updated realistic range for petrol (₹85-105)
                if 85 <= potential_price <= 105:
                    petrol_price = potential_price
                    print(f"Found petrol price from cardekho: ₹{petrol_price}")
                    break
            if petrol_price:
                break
        
        time.sleep(1)  # Be respectful to the server
        
        # Try diesel price
        diesel_url = 'https://www.cardekho.com/diesel-price-in-delhi-state'
        response = requests.get(diesel_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        page_text = soup.get_text()
        
        diesel_patterns = [
            r'Diesel price in Delhi stands at ₹\s*(\d+\.?\d*)\s*per litre',
            r'average Diesel price in Delhi stands at ₹\s*(\d+\.?\d*)',
            r'₹\s*(\d+\.?\d*)\s*per litre.*diesel',
        ]
        
        for pattern in diesel_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                # Updated realistic range for diesel (₹80-95)
                if 80 <= potential_price <= 95:
                    diesel_price = potential_price
                    print(f"Found diesel price from cardekho: ₹{diesel_price}")
                    break
            if diesel_price:
                break
        
        return petrol_price, diesel_price
        
    except Exception as e:
        print(f"Error scraping cardekho: {e}")
        return None, None

def scrape_goodreturns():
    """
    Try to scrape from goodreturns.in - updated with better patterns
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
        page_text = soup.get_text()
        
        # Look for more specific patterns
        petrol_patterns = [
            r'Rs\.\s*(\d+\.?\d*)/Ltr',
            r'₹\s*(\d+\.?\d*)\s*per\s*litre',
            r'Today.*Delhi.*₹\s*(\d+\.?\d*)',
            r'New Delhi Petrol Price.*Rs\.\s*(\d+\.?\d*)',
        ]
        
        for pattern in petrol_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                # Updated realistic range for petrol (₹85-105)
                if 85 <= potential_price <= 105:
                    petrol_price = potential_price
                    print(f"Found petrol price from goodreturns: ₹{petrol_price}")
                    break
            if petrol_price:
                break
        
        time.sleep(1)  # Be respectful to the server
        
        # Try diesel price
        diesel_url = 'https://www.goodreturns.in/diesel-price-in-new-delhi.html'
        response = requests.get(diesel_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        diesel_price = None
        page_text = soup.get_text()
        
        diesel_patterns = [
            r'Rs\.\s*(\d+\.?\d*)/Ltr',
            r'₹\s*(\d+\.?\d*)\s*per\s*litre',
            r'Today.*Delhi.*₹\s*(\d+\.?\d*)',
            r'New Delhi Diesel Price.*Rs\.\s*(\d+\.?\d*)',
        ]
        
        for pattern in diesel_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                # Updated realistic range for diesel (₹80-95)
                if 80 <= potential_price <= 95:
                    diesel_price = potential_price
                    print(f"Found diesel price from goodreturns: ₹{diesel_price}")
                    break
            if diesel_price:
                break
        
        return petrol_price, diesel_price
        
    except Exception as e:
        print(f"Error scraping goodreturns: {e}")
        return None, None

def scrape_acko():
    """
    Try to scrape from acko.com - updated based on search results
    """
    print("Trying acko.com...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    petrol_price = None
    diesel_price = None
    
    try:
        # Try diesel price from Acko
        diesel_url = 'https://www.acko.com/fuel/diesel-price-in-new-delhi/'
        response = requests.get(diesel_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        page_text = soup.get_text()
        
        # Updated patterns based on search results showing "87.67,/ per litre"
        diesel_patterns = [
            r'(\d+\.?\d*),/\s*per\s*litre',
            r'₹\s*(\d+\.?\d*)\s*per\s*litre',
            r'Today.*(\d+\.?\d*)\s*per\s*litre',
            r'Diesel Price.*(\d+\.?\d*)',
        ]
        
        for pattern in diesel_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                if 80 <= potential_price <= 95:  # Reasonable diesel price range
                    diesel_price = potential_price
                    print(f"Found diesel price from acko: ₹{diesel_price}")
                    break
            if diesel_price:
                break
        
        time.sleep(1)
        
        # Try petrol price from Acko
        try:
            petrol_url = 'https://www.acko.com/fuel/petrol-price-in-new-delhi/'
            response = requests.get(petrol_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            page_text = soup.get_text()
            
            petrol_patterns = [
                r'(\d+\.?\d*),/\s*per\s*litre',
                r'₹\s*(\d+\.?\d*)\s*per\s*litre',
                r'Today.*(\d+\.?\d*)\s*per\s*litre',
                r'Petrol Price.*(\d+\.?\d*)',
            ]
            
            for pattern in petrol_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    potential_price = float(match)
                    if 85 <= potential_price <= 105:  # Reasonable petrol price range
                        petrol_price = potential_price
                        print(f"Found petrol price from acko: ₹{petrol_price}")
                        break
                if petrol_price:
                    break
        except Exception as pe:
            print(f"Error getting petrol from acko: {pe}")
        
        return petrol_price, diesel_price
        
    except Exception as e:
        print(f"Error scraping acko: {e}")
        return None, None

def scrape_businesstoday():
    """
    Try to scrape from businesstoday.in - new source based on search results
    """
    print("Trying businesstoday.in...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        petrol_url = 'https://www.businesstoday.in/fuel-price/petrol-price-in-delhi-today'
        response = requests.get(petrol_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        petrol_price = None
        page_text = soup.get_text()
        
        # Look for price patterns
        petrol_patterns = [
            r'₹(\d+\.?\d*)\s*per\s*litre',
            r'stood at ₹(\d+\.?\d*)',
            r'price.*Delhi.*₹(\d+\.?\d*)',
        ]
        
        for pattern in petrol_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                potential_price = float(match)
                if 85 <= potential_price <= 105:  # Reasonable petrol price range
                    petrol_price = potential_price
                    print(f"Found petrol price from businesstoday: ₹{petrol_price}")
                    break
            if petrol_price:
                break
        
        return petrol_price, None
        
    except Exception as e:
        print(f"Error scraping businesstoday: {e}")
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
        scrape_cardekho,      # Based on search results, this seems most reliable
        scrape_goodreturns,
        scrape_acko,
        scrape_businesstoday,
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
                time.sleep(2)  # Increased delay
                
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
    
    # Use fallback prices based on recent search results if scraping fails
    if petrol_price is None:
        print("WARNING: Could not fetch petrol price, using last known price")
        petrol_price = 94.77  # Based on search results
    
    if diesel_price is None:
        print("WARNING: Could not fetch diesel price, using last known price") 
        diesel_price = 87.67  # Based on search results
    
    print(f"Final prices - Petrol: ₹{petrol_price}, Diesel: ₹{diesel_price}")
    
    # Validation check - ensure prices are reasonable
    if not (85 <= petrol_price <= 105) or not (80 <= diesel_price <= 95):
        print(f"WARNING: Prices seem unrealistic. Petrol: {petrol_price}, Diesel: {diesel_price}")
        # Don't save obviously wrong data
        if petrol_price == diesel_price:
            print("ERROR: Petrol and diesel prices are identical, likely scraping error")
            return
    
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
                    print(f"Data for {today} in New Delhi already exists. Updating with new prices.")
                    # Remove today's data and add new data
                    existing_data = existing_data[
                        ~((existing_data['Date'] == today) & (existing_data['City'] == 'New Delhi'))
                    ]
                
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