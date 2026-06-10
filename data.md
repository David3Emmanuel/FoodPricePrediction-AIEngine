# Data & Feature Manifest

This document defines the standardized feature names, their sources, and the processing pipeline used across the AI engine.

## Lag Intervals
Certain features include historical "lags" or "deltas" to capture trends. These are indicated by the following suffixes:
- `_1W`: 1-Week change/value
- `_1M`: 1-Month change/value
- `_3M`: 3-Month change/value
- `_6M`: 6-Month change/value
- `_1Y`: 1-Year change/value

---

## 1. Feature Definitions

### Categorical Features (User/Dashboard Inputs)
- `Food_Item`: Specific crop (e.g., "maize", "rice").
- `Item_Type`: Sub-type (e.g., "white", "local").
- `Category`: Broad group (e.g., "cereals", "vegetables").
- `Vendor_Type`: Level of trade ("retail", "wholesale").
- `State`: Geographic region (mapped via reverse geocoding).

### Market & Price Features
- `Price_NGN` (plus lag): The base unit price of the commodity.
- `Target_Price_Change_1M_Percent`: The prediction target (% change in price 1 month into the future).

### Macroeconomic Features
- `General_Inflation_Rate_Percent` (plus lag): Headline inflation index.
- `Food_Inflation_Rate_Percent` (plus lag): Specific food inflation index.
- `Exchange_Rate_NGN_USD` (plus lag): NGN/USD weighted average rate.
- `Diesel_Price_NGN` (plus lag): Fuel/transportation cost index.
- `Crude_Oil_Price_USD` (plus lag): Global oil market price.

### Environmental & Narrative
- `Avg_Temperature_C`: Average weekly temperature.
- `Precipitation_mm`: Total weekly rainfall.
- `Solar_Radiation_MJ`: Sunlight exposure/solar radiation.
- `Weekly_Econ_Sentiment_Score`: Derived from news headlines via FinBERT.

### Conflict & Stability
- `Regional_Events_Count` (plus lag): Number of insecurity events in the state (ACLED).
- `Regional_Fatalities_Count` (plus lag): Total fatalities from insecurity events.

### Temporal & Contextual
- `Year`: Calendar year.
- `Month`: Calendar month.
- `Week`: ISO week number (%W).
- `Month_Num`: 1–12 numeric representation.
- `Seasonality_Month`: Sine/Cosine or categorical indicator of harvest/seasonal cycles.

---

## 2. Data Sources & Pipeline

| Feature Group | Current Source | Raw Frequency | Additional Processing |
| :--- | :--- | :--- | :--- |
| **Market Prices** | Market Surveys (Excel) | Daily | Reverse Geocoding (Lat/Lon to State) |
| **News Sentiment** | Web/News API (Excel) | Daily | **FinBERT** Sentiment Classification |
| **Insecurity** | ACLED (API/Excel) | Monthly/Weekly | Sum aggregation for events/fatalities |
| **Weather** | NASA POWER (API) | Daily | Mean/Sum aggregation by State |
| **Inflation** | National Bureau of Stats (Excel) | Monthly | Mean interpolation to weekly |
| **Diesel Price** | National Bureau of Stats (Excel) | Monthly | Mean interpolation by State |
| **Crude Oil** | Global Markets (Excel) | Daily | Mean aggregation |
| **Exchange Rate** | Central Bank (Excel) | Daily | Weighted Average Mean aggregation |

---

## 3. Standard Processing Steps
1. **Geospatial Mapping:** All point-data (Lat/Lon) is converted to State names using the `reverse_geocoder` library.
2. **Temporal Resampling:** Monthly data is converted to Weekly (`%W`) granularity using a day-weighted proportional distribution logic.
3. **Sentiment Scoring:** Raw news text is processed through the `ProsusAI/finbert` model. Scores are calculated as `(positive_confidence - negative_confidence)`.
