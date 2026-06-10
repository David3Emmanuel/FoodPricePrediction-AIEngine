import pandas as pd
from pathlib import Path
from typing import Any, Optional

from agri_price import utils
from agri_price import news

import sqlite3

def load_data(path: str, table_name: str = "historical_data") -> tuple[pd.DataFrame, pd.Series, list[str]]:
    # Load the latest dataset (from CSV or SQL)
    if path.endswith('.db'):
        conn = sqlite3.connect(path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
    else:
        df = pd.read_csv(path)

    # 1. DYNAMICALLY auto-detect all text/categorical columns! 
    # This grabs 'state', 'food_item', and any future text columns you add.
    cat_features = df.select_dtypes(include=['object', 'string']).columns.tolist()

    # Ensure categorical columns are perfectly clean strings
    for col in cat_features:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()

    # Use our precise 1-Month target
    # Check if we have the standardized name or the CSV variant
    if 'Target_Price_Change_1M_Percent' in df.columns:
        target_col = 'Target_Price_Change_1M_Percent'
    elif 'TARGET_Price_Change_1M' in df.columns:
        target_col = 'TARGET_Price_Change_1M'
    else:
        # Fallback or error
        target_col = [col for col in df.columns if 'TARGET' in col.upper()][0]

    X = df.drop(columns=['Year', 'Month', 'Week', target_col], errors='ignore')
    y = df[target_col]

    return X, y, cat_features

def build_combined_dataset(
    news_path: str,
    insecurity_path: str,
    weather_path: str,
    food_path: str,
    diesel_path: str,
    crude_oil_path: str,
    exchange_rate_path: str,
    inflation_path: str
) -> pd.DataFrame:
    """
    Combines all the processed datasets into a single weekly dataset.
    All paths should point to the relevant raw Excel or CSV files.
    """
    
    # 1. News Sentiment
    print("Processing News...")
    df_news_raw = pd.read_excel(news_path)
    # Filter valid IDs as per preprocessing.py
    df_news_raw = df_news_raw[pd.to_numeric(df_news_raw['id'], errors='coerce').notna()].reset_index(drop=True)
    df_news = news.process_news_dataframe(df_news_raw)

    # 2. Insecurity (ACLED)
    print("Processing Insecurity...")
    df_ins_raw = pd.read_excel(insecurity_path, sheet_name='Data')
    df_ins_raw = df_ins_raw[['Admin1', 'Month', 'Year', 'Events', 'Fatalities']]
    df_ins_raw['Month'] = df_ins_raw['Month'].apply(utils.month_to_num)
    df_ins_monthly = df_ins_raw.groupby(['Admin1', 'Year', 'Month'])[['Events', 'Fatalities']].sum().reset_index()
    df_ins_monthly.rename(columns={'Admin1': 'State'}, inplace=True)
    
    # State-level monthly to weekly
    ins_dfs = []
    for state in df_ins_monthly['State'].unique():
        state_df = df_ins_monthly[df_ins_monthly['State'] == state].drop(columns=['State'])
        weekly = utils.monthly_to_weekly(state_df, value_columns=['Events', 'Fatalities'], mode='sum')
        weekly['State'] = state
        ins_dfs.append(weekly)
    df_insecurity = pd.concat(ins_dfs, ignore_index=True)
    df_insecurity.rename(columns={'Events': 'Regional_Events_Count', 'Fatalities': 'Regional_Fatalities_Count'}, inplace=True)

    # 3. Weather
    print("Processing Weather...")
    # Assumes weather is already a combined CSV as fetched in preprocessing.py
    df_weather_raw = pd.read_csv(weather_path)
    df_weather_raw['Date'] = pd.to_datetime(df_weather_raw['Date_Raw'], format='%Y%m%d')
    df_weather_raw['Year'] = df_weather_raw['Date'].dt.year
    df_weather_raw['Week'] = df_weather_raw['Date'].dt.strftime('%W').astype(int)
    df_weather = df_weather_raw.groupby(['State', 'Year', 'Week']).agg(
        Precipitation_mm=('Precipitation_mm', 'sum'),
        Avg_Temperature_C=('Avg_Temperature_C', 'mean'),
        Solar_Radiation_MJ=('Solar_Radiation_MJ', 'mean'),
    ).reset_index()

    # 4. Food Prices
    print("Processing Food Prices...")
    df_food_raw = pd.read_excel(food_path, sheet_name='Sheet1')
    df_food_raw.sort_values(by='date', inplace=True)
    df_food_raw['year'] = df_food_raw['date'].dt.year
    df_food_raw['week'] = df_food_raw['date'].dt.strftime('%W').astype(int)
    df_food_raw['location'] = utils.coords_to_region(df_food_raw['location'])
    df_food = (
        df_food_raw.drop(columns=['date'])
        .groupby(['year', 'week', 'food_item', 'location'])
        .agg(Price_NGN=('price', 'mean'), Item_Type=('item_type', 'first'), Category=('category', 'first'))
        .reset_index()
        .rename(columns={'year': 'Year', 'week': 'Week', 'location': 'State', 'food_item': 'Food_Item'})
    )

    # 5. Diesel
    print("Processing Diesel...")
    df_diesel_raw = pd.read_excel(diesel_path, sheet_name='Automotive Gas Oil (Diesel) Pri', header=6)
    df_diesel_raw = df_diesel_raw[df_diesel_raw['State'] != 'Nigeria'].drop(columns=['Units'])
    df_diesel_melted = df_diesel_raw.melt(id_vars=['State'], var_name='Date', value_name='Diesel_Price_NGN')
    df_diesel_melted['Date'] = pd.to_datetime(df_diesel_melted['Date'], format='%b %Y')
    df_diesel_melted['Year'] = df_diesel_melted['Date'].dt.year
    df_diesel_melted['Month'] = df_diesel_melted['Date'].dt.month
    df_diesel_monthly = df_diesel_melted.drop(columns=['Date']).dropna(subset=['Diesel_Price_NGN'])
    
    diesel_dfs = []
    for state in df_diesel_monthly['State'].unique():
        state_df = df_diesel_monthly[df_diesel_monthly['State'] == state].drop(columns=['State'])
        weekly = utils.monthly_to_weekly(state_df, value_columns=['Diesel_Price_NGN'], mode='mean')
        weekly['State'] = state
        diesel_dfs.append(weekly)
    df_diesel = pd.concat(diesel_dfs, ignore_index=True)

    # 6. Crude Oil
    print("Processing Crude Oil...")
    df_crude_raw = pd.read_excel(crude_oil_path)
    df_crude_raw.columns = ['Date', 'Crude_Oil_Price_USD']
    df_crude_raw['Date'] = pd.to_datetime(df_crude_raw['Date'], dayfirst=True)
    df_crude_raw['Year'] = df_crude_raw['Date'].dt.year
    df_crude_raw['Week'] = df_crude_raw['Date'].dt.strftime('%W').astype(int)
    df_crude = df_crude_raw.groupby(['Year', 'Week'])['Crude_Oil_Price_USD'].mean().reset_index()

    # 7. Exchange Rate
    print("Processing Exchange Rates...")
    df_ex_raw = pd.read_excel(exchange_rate_path)
    df_ex_raw['Date'] = pd.to_datetime(df_ex_raw['ratedate'], format='%B-%d-%Y')
    df_ex_raw['Year'] = df_ex_raw['Date'].dt.year
    df_ex_raw['Week'] = df_ex_raw['Date'].dt.strftime('%W').astype(int)
    df_exchange = df_ex_raw.groupby(['Year', 'Week']).agg(Exchange_Rate_NGN_USD=('weightedAvgRate', 'mean')).reset_index()

    # 8. Inflation
    print("Processing Inflation...")
    df_inf_raw = pd.read_excel(inflation_path)
    df_inf_monthly = df_inf_raw.rename(columns={
        'tyear': 'Year',
        'tmonth': 'Month',
        'foodYearOn': 'Food_Inflation_Rate_Percent',
        'allItemsLessFrmProdYearOn': 'General_Inflation_Rate_Percent',
    })[['Year', 'Month', 'Food_Inflation_Rate_Percent', 'General_Inflation_Rate_Percent']]
    df_inflation = utils.monthly_to_weekly(df_inf_monthly, mode='mean')

    # Final Merge
    print("Merging all sources...")
    combined = (
        df_food
        .merge(df_weather, on=['State', 'Year', 'Week'], how='left')
        .merge(df_news, on=['Year', 'Week'], how='left')
        .merge(df_insecurity, on=['State', 'Year', 'Week'], how='left')
        .merge(df_diesel, on=['State', 'Year', 'Week'], how='left')
        .merge(df_crude, on=['Year', 'Week'], how='left')
        .merge(df_exchange, on=['Year', 'Week'], how='left')
        .merge(df_inflation, on=['Year', 'Week'], how='left')
    )

    return combined
