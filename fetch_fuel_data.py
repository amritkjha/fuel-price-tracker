# fetch_fuel_data.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Define the CSV file where fuel price data will be stored
FUEL_DATA_FILE = 'fuel_prices.csv'

def try_requests_scraping():
    """
    Try scraping with requests + BeautifulSoup first (faster method)
    """
    url = 'https://www.cardekho.com/fuel-price'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    try:
        print("Attempting to scrape with requests...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Print the page structure to understand current layout
        print("Page title:", soup.title.string if soup.title else "No title found")
        
        # Multiple strategies to find fuel prices
        petrol_price, diesel_price = None, None
        
        # Strategy 1: Look for tables containing price data
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on the page")
        
        for i, table in enumerate(tables):
            print(f"Examining table {i+1}...")
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                
                # Look for Delhi/New Delhi in the row
                if any(city in row_text.lower() for city in ['delhi', 'new delhi']):
                    print(f"Found Delhi row: {row_text}")
                    
                    # Extract price using regex
                    price_matches = re.findall(r'₹?\s*(\d+\.?\d*)', row_text)
                    if price_matches:
                        price = float(price_matches[0])
                        
                        # Determine if this is petrol or diesel based on context
                        if 'petrol' in row_text.lower() or (petrol_price is None and diesel_price is not None):
                            petrol_price = price
                            print(f"Found petrol price: ₹{price}")
                        elif 'diesel' in row_text.lower() or (diesel_price is None and petrol_price is not None):
                            diesel_price = price
                            print(f"Found diesel price: ₹{price}")
        
        # Strategy 2: Look for specific div structures (your original approach)
        content_hold_div = soup.find('div', class_='contentHold gsc_row')
        if content_hold_div:
            print("Found contentHold gsc_row div - using original strategy")
            # Your original code logic here
            petrol_section_div = content_hold_div.find('div', attrs={'data-track-section': 'Petrol'})
            # ... rest of your original logic
        
        # Strategy 3: Look for any div/section containing fuel prices
        if petrol_price is None or diesel_price is None:
            print("Trying alternative search strategies...")
            
            # Look for price patterns in the entire page
            page_text = soup.get_text()
            
            # Find Delhi prices using regex
            delhi_section = re.search(r'delhi.*?(?=\n.*?(?:mumbai|chennai|kolkata|bangalore))', page_text, re.IGNORECASE | re.DOTALL)
            if delhi_section:
                delhi_text = delhi_section.group()
                prices = re.findall(r'₹\s*(\d+\.?\d*)', delhi_text)
                if len(prices) >= 2:
                    petrol_price = float(prices[0]) if petrol_price is None else petrol_price
                    diesel_price = float(prices[1]) if diesel_price is None else diesel_price
                    print(f"Found prices in text: Petrol ₹{petrol_price}, Diesel ₹{diesel_price}")
        
        return petrol_price, diesel_price
    
    except requests.exceptions.RequestException as e:
        print(f"Requests error: {e}")
        return None, None
    except Exception as e:
        print(f"Parsing error with requests method: {e}")
        return None, None

def try_selenium_scraping():
    """
    Fallback method using Selenium for JavaScript-heavy pages
    """
    print("Attempting to scrape with Selenium...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.cardekho.com/fuel-price')
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        # Get page source after JavaScript execution
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        petrol_price, diesel_price = None, None
        
        # Look for tables or specific elements containing fuel prices
        # Try to find elements containing Delhi and price information
        elements = soup.find_all(text=re.compile(r'delhi', re.IGNORECASE))
        
        for element in elements:
            parent = element.parent
            if parent:
                # Look at the parent and surrounding elements for prices
                parent_text = parent.get_text(strip=True)
                
                # Also check siblings and nearby elements
                extended_text = parent_text
                if parent.parent:
                    extended_text = parent.parent.get_text(strip=True)
                
                price_matches = re.findall(r'₹\s*(\d+\.?\d*)', extended_text)
                
                if price_matches and 'delhi' in extended_text.lower():
                    # If we find multiple prices in the same section, likely petrol and diesel
                    if len(price_matches) >= 2:
                        if petrol_price is None:
                            petrol_price = float(price_matches[0])
                            print(f"Found petrol price with Selenium: ₹{petrol_price}")
                        if diesel_price is None:
                            diesel_price = float(price_matches[1])
                            print(f"Found diesel price with Selenium: ₹{diesel_price}")
                    else:
                        # Single price - determine type by context
                        price = float(price_matches[0])
                        
                        if 'petrol' in extended_text.lower() and petrol_price is None:
                            petrol_price = price
                            print(f"Found petrol price with Selenium: ₹{price}")
                        elif 'diesel' in extended_text.lower() and diesel_price is None:
                            diesel_price = price
                            print(f"Found diesel price with Selenium: ₹{price}")
                        elif petrol_price is None:
                            # Assume first price found is petrol if no context
                            petrol_price = price
                            print(f"Found petrol price with Selenium (assumed): ₹{price}")
                        elif diesel_price is None:
                            # Assume second price found is diesel if no context
                            diesel_price = price
                            print(f"Found diesel price with Selenium (assumed): ₹{price}")
        
        return petrol_price, diesel_price
        
    except (TimeoutException, WebDriverException) as e:
        print(f"Selenium error: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error with Selenium: {e}")
        return None, None
    finally:
        if driver:
            driver.quit()

def fetch_and_save_data():
    """
    Fetches daily petrol and diesel prices for New Delhi using multiple strategies
    """
    print("Starting fuel price fetch process...")
    
    # Try requests first (faster)
    petrol_price, diesel_price = try_requests_scraping()
    
    # If requests failed, try Selenium
    if petrol_price is None or diesel_price is None:
        print("Requests method didn't find all prices, trying Selenium...")
        selenium_petrol, selenium_diesel = try_selenium_scraping()
        
        petrol_price = petrol_price or selenium_petrol
        diesel_price = diesel_price or selenium_diesel
    
    # Check if we got valid prices
    if petrol_price is None and diesel_price is None:
        print("ERROR: Could not fetch any fuel prices. The website structure may have changed significantly.")
        print("Please check the website manually and update the scraping logic.")
        return
    
    if petrol_price is None:
        print("WARNING: Could not fetch petrol price")
        petrol_price = 0.0
    
    if diesel_price is None:
        print("WARNING: Could not fetch diesel price") 
        diesel_price = 0.0
    
    print(f"Final prices - Petrol: ₹{petrol_price}, Diesel: ₹{diesel_price}")
    
    # Save data to CSV
    today = datetime.now().strftime('%Y-%m-%d')
    
    new_data = pd.DataFrame([
        {'Date': today, 'City': 'New Delhi', 'FuelType': 'Petrol', 'Price': petrol_price},
        {'Date': today, 'City': 'New Delhi', 'FuelType': 'Diesel', 'Price': diesel_price}
    ])
    
    if os.path.exists(FUEL_DATA_FILE):
        try:
            existing_data = pd.read_csv(FUEL_DATA_FILE)
            # Check if the CSV file is empty or corrupted
            if existing_data.empty or len(existing_data.columns) == 0:
                print("Existing CSV file is empty or corrupted, creating new one.")
                updated_data = new_data
            else:
                existing_data['Date'] = pd.to_datetime(existing_data['Date'])
                
                if not existing_data[(existing_data['Date'] == pd.to_datetime(today)) & (existing_data['City'] == 'New Delhi')].empty:
                    print(f"Data for {today} in New Delhi already exists. Skipping update.")
                    return
                
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            print(f"Error reading existing CSV file: {e}")
            print("Creating new CSV file.")
            updated_data = new_data
    else:
        updated_data = new_data
    
    updated_data.to_csv(FUEL_DATA_FILE, index=False)
    print(f"Successfully saved data for {today} to {FUEL_DATA_FILE}")

if __name__ == "__main__":
    fetch_and_save_data()