import logging
import sqlite3
from argparse import ArgumentParser
from datetime import datetime

import requests

from .state_coords import state_coords

# 1. Setup Logging (Crucial for Cron Jobs so we know if it failed early)
logging.basicConfig(
    filename='feature_store_updates.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DEFAULT_STATE = 'Lagos'


def get_state_coordinates(state: str) -> tuple[float, float]:
    if state not in state_coords:
        logging.warning("Unknown state '%s'; falling back to %s.", state, DEFAULT_STATE)
        state = DEFAULT_STATE

    return state_coords[state]


def fetch_live_weather(state: str = DEFAULT_STATE):
    """Fetches real, live weather data for a Nigerian state using the free Open-Meteo API."""
    try:
        lat, lon = get_state_coordinates(state)
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            "&current=temperature_2m,precipitation,shortwave_radiation&timezone=Africa%2FLagos"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Convert W/m^2 to MJ for the last hour
        watts_per_sq_meter = data['current']['shortwave_radiation']
        joules_per_sq_meter = watts_per_sq_meter * 3600  # 3600 seconds in an hour
        megajoules_per_sq_meter = joules_per_sq_meter / 1_000_000
        
        return {
            "Avg_Temperature_C": data['current']['temperature_2m'],
            "Precipitation_mm": data['current']['precipitation'],
            "Solar_Radiation_MJ": megajoules_per_sq_meter
        }
    except Exception as e:
        logging.error(f"Weather API failed: {e}")
        return None  # Return None so we know to use graceful degradation

def fetch_macro_economics():
    """
    Fetches the latest inflation rate. 
    (TODO: Replace with actual CBN API call, TradingEconomics, or web scraper)
    """
    try:
        # Mocking the live API call
        return {"General_Inflation_Rate_Percent": 33.20}
    except Exception as e:
        logging.error(f"Macro API failed: {e}")
        return None

def fetch_market_price_lags():
    """
    Calculates the 1M, 3M, 6M, and 1Y lags.
    (TODO: Connect this to your live production SQL database where daily vendor prices drop)
    """
    try:
        # Mocking the calculation from your raw vendor database
        return {
            "Price_Change_1M_Percent": 5.2,
            "Price_Change_3M_Percent": -16.19,
            "Price_Change_6M_Percent": 12.4,
            "Price_Change_1Y_Percent": 135.17
        }
    except Exception as e:
        logging.error(f"Market DB query failed: {e}")
        return None

def get_season(month: int) -> str:
    """Determines the Nigerian season from the month."""
    if 4 <= month <= 10:
        return "Wet"
    return "Dry"

def main(state: str = DEFAULT_STATE):
    logging.info("Starting nightly feature store update...")
    
    # 1. Gather all live data
    now = datetime.now()
    weather = fetch_live_weather(state)
    macro = fetch_macro_economics()
    market = fetch_market_price_lags()
    current_month = now.month
    current_season = get_season(current_month)

    # 2. Connect to the local SQLite Feature Store
    conn = sqlite3.connect('feature_store.db')
    cursor = conn.cursor()

    # 3. Graceful Degradation Logic
    # We first pull yesterday's data. If any API failed today, we fallback to yesterday's number.
    cursor.execute("SELECT * FROM current_market_state WHERE id = 1")
    yesterday_data = cursor.fetchone()
    
    if yesterday_data is None:
        logging.warning("Feature store is empty. Forcing update with available data.")
        # Create a blank slate if the DB is completely empty (matches the 11 columns we created)
        yesterday_data = (1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, current_month, "Unknown")

    # 4. Construct the Final Update Payload
    # Format: id, Inflation, 1M, 3M, 6M, 1Y, Temp, Precip, Solar, Month, Season
    updated_values = (
        1,
        macro['General_Inflation_Rate_Percent'] if macro else yesterday_data[1],
        market['Price_Change_1M_Percent'] if market else yesterday_data[2],
        market['Price_Change_3M_Percent'] if market else yesterday_data[3],
        market['Price_Change_6M_Percent'] if market else yesterday_data[4],
        market['Price_Change_1Y_Percent'] if market else yesterday_data[5],
        weather['Avg_Temperature_C'] if weather else yesterday_data[6],
        weather['Precipitation_mm'] if weather else yesterday_data[7],
        weather['Solar_Radiation_MJ'] if weather else yesterday_data[8],
        current_month,
        current_season
    )

    # 5. Push to Database
    cursor.execute('''
        INSERT OR REPLACE INTO current_market_state 
        (id, General_Inflation_Rate_Percent, Price_Change_1M_Percent, Price_Change_3M_Percent, Price_Change_6M_Percent, Price_Change_1Y_Percent, Avg_Temperature_C, Precipitation_mm, Solar_Radiation_MJ, Month_Num, Season)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', updated_values)

    conn.commit()
    conn.close()
    
    logging.info("Feature store update completed successfully.")
    print("Feature store updated successfully! Check feature_store_updates.log for details.")

if __name__ == "__main__":
    parser = ArgumentParser(description='Update the feature store for a specific state.')
    parser.add_argument('--state', default=DEFAULT_STATE, help='State to fetch weather for')
    args = parser.parse_args()
    main(args.state)