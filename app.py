# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Define the CSV file where fuel price data is stored
FUEL_DATA_FILE = 'fuel_prices.csv'

@st.cache_data # Cache data loading to improve performance
def load_data():
    """
    Loads fuel price data from the CSV file.
    Returns an empty DataFrame if the file does not exist.
    """
    if os.path.exists(FUEL_DATA_FILE):
        try:
            df = pd.read_csv(FUEL_DATA_FILE)
            df['Date'] = pd.to_datetime(df['Date']) # Convert 'Date' column to datetime objects
            return df.sort_values('Date').reset_index(drop=True) # Sort by date and reset index
        except Exception as e:
            st.error(f"Error loading data from {FUEL_DATA_FILE}: {e}")
            return pd.DataFrame(columns=['Date', 'City', 'FuelType', 'Price'])
    return pd.DataFrame(columns=['Date', 'City', 'FuelType', 'Price'])

def analyze_trend(df, city, fuel_type, days=7):
    """
    Analyzes the price trend for a given city and fuel type over the last 'days'.
    Generates a human-readable summary and a refueling suggestion.
    """
    # Filter data for the specific city and fuel type, and take the last 'days' entries
    filtered_df = df[(df['City'] == city) & (df['FuelType'] == fuel_type)].tail(days)
    
    if len(filtered_df) < 2:
        return "Not enough historical data for a meaningful trend analysis. Please check back later."

    # Calculate price change from the first to the last available day in the window
    start_price = filtered_df.iloc[0]['Price']
    end_price = filtered_df.iloc[-1]['Price']
    price_change = end_price - start_price

    # Calculate average price change per day
    avg_daily_change = price_change / (len(filtered_df) - 1) if len(filtered_df) > 1 else 0

    # Determine trend and suggestion based on price change thresholds
    trend_summary = ""
    refuel_suggestion = ""

    if price_change > 0.50: # Significant increase threshold
        trend_summary = f"{fuel_type} prices in {city} increased by ₹{price_change:.2f} over the last {days} days."
        refuel_suggestion = "It's advisable to refuel soon as prices are likely to continue rising."
    elif price_change < -0.50: # Significant decrease threshold
        trend_summary = f"{fuel_type} prices in {city} decreased by ₹{-price_change:.2f} over the last {days} days."
        refuel_suggestion = "Prices might drop further. Consider waiting a bit before refueling in bulk."
    else:
        trend_summary = f"{fuel_type} prices in {city} remained relatively stable over the last {days} days."
        refuel_suggestion = "Prices are stable. Refuel as needed without urgency."
    
    # Add a note about daily change if significant
    if abs(avg_daily_change) > 0.05: # Threshold for noticeable daily change
        if avg_daily_change > 0:
            trend_summary += f" (Average daily increase: ₹{avg_daily_change:.2f})"
        else:
            trend_summary += f" (Average daily decrease: ₹{-avg_daily_change:.2f})"

    return f"{trend_summary}\n\n**Refueling Suggestion:** {refuel_suggestion}"

# --- Streamlit UI Configuration ---
st.set_page_config(
    page_title="Local Fuel Price Tracker",
    layout="wide", # Use wide layout for better chart visibility
    initial_sidebar_state="expanded"
)

st.title("⛽ Local Fuel Price Tracker & Analyzer")

# Load data when the app runs
df_fuel = load_data()

if df_fuel.empty:
    st.warning("No fuel price data available. The daily update script needs to run first or the data file is empty/corrupt.")
    st.info("Please ensure your `fuel_prices.csv` is populated or the GitHub Action has run successfully.")
else:
    # Get unique cities and fuel types from the loaded data
    cities = df_fuel['City'].unique().tolist()
    fuel_types = df_fuel['FuelType'].unique().tolist()

    # Sidebar for user selection
    st.sidebar.header("Select Options")
    selected_city = st.sidebar.selectbox("Select City", cities)
    selected_fuel_type = st.sidebar.selectbox("Select Fuel Type", fuel_types)

    st.header(f"Current Price in {selected_city} ({selected_fuel_type})")
    
    # Filter for the latest price of the selected city and fuel type
    current_price_df = df_fuel[(df_fuel['City'] == selected_city) & (df_fuel['FuelType'] == selected_fuel_type)].tail(1)
    
    if not current_price_df.empty:
        latest_price = current_price_df.iloc[0]['Price']
        latest_date = current_price_df.iloc[0]['Date'].strftime('%Y-%m-%d')
        st.success(f"### ₹{latest_price:.2f} as of {latest_date}")
    else:
        st.info("No current data available for this city and fuel type combination.")

    st.header("Historical Trend (Last 30 Days)")
    # Filter data for charting
    chart_data = df_fuel[(df_fuel['City'] == selected_city) & (df_fuel['FuelType'] == selected_fuel_type)]
    
    if not chart_data.empty:
        # Ensure only relevant columns for the chart and set 'Date' as index
        chart_data_for_plot = chart_data.set_index('Date')['Price'].tail(30) # Show last 30 days for clarity
        st.line_chart(chart_data_for_plot)
    else:
        st.info("No sufficient historical data for charting.")

    st.header("Trend Analysis & Refueling Suggestion")
    # Generate and display the trend analysis
    summary = analyze_trend(df_fuel, selected_city, selected_fuel_type)
    st.markdown(summary)

st.markdown("---")
st.markdown("This app fetches daily fuel prices and provides insights into trends. Data updates daily via GitHub Actions.")

