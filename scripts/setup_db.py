import sqlite3

def setup_db():
    conn = sqlite3.connect('data/feature_store.db')
    cursor = conn.cursor()
    
    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_market_state (
            id INTEGER PRIMARY KEY,
            General_Inflation_Rate_Percent REAL,
            Price_Change_1M_Percent REAL,
            Price_Change_3M_Percent REAL,
            Price_Change_6M_Percent REAL,
            Price_Change_1Y_Percent REAL,
            Avg_Temperature_C REAL,
            Precipitation_mm REAL,
            Solar_Radiation_MJ REAL,
            Month_Num REAL,
            Season TEXT
        )
    ''')
    
    # Inserting MOCK data (You'll need to get real data)
    cursor.execute('''
        INSERT OR REPLACE INTO current_market_state 
        (id, General_Inflation_Rate_Percent, Price_Change_1M_Percent, Price_Change_3M_Percent, Price_Change_6M_Percent, Price_Change_1Y_Percent, Avg_Temperature_C, Precipitation_mm, Solar_Radiation_MJ, Month_Num, Season)
        VALUES (1, 32.7, 5.2, -16.19, 12.4, 135.17, 25.93, 29.17, 15.2, 9.0, 'Dry')
    ''')
    
    conn.commit()
    conn.close()
    print("Local SQLite Feature Store created successfully!")

if __name__ == "__main__":
    setup_db()