# AgriPrice Prediction API

This directory contains the FastAPI-based backend for the AgriPrice Prediction Engine. It serves machine learning predictions via a RESTful interface, integrating real-time market state from a local feature store with the trained CatBoost model.

## Features
- **FastAPI Backend:** High-performance async API.
- **Model Integration:** Direct loading of CatBoost models for inference.
- **XAI (Explainable AI):** Returns SHAP values to explain the drivers behind each prediction.
- **Feature Store Integration:** Automatically pulls macroeconomic and weather context from a local SQLite database.

## Setup & Running

### Prerequisites
- Ensure the root project dependencies are installed (see root `README.md`).
- Initialize the local feature store database.

### 1. Initialize the Feature Store
From the project root:
```bash
uv run scripts/02_database/setup_db.py
```

### 2. Run the API
From the project root:
```bash
uvicorn api.app:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can view the interactive documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## Endpoints

### `POST /predict`
Predicts the 1-month price change for a specific commodity based on the current market/weather context in the Feature Store.

**Request Body:**
You can request predictions by either providing a simplified `commodity_id` string, or by specifying the raw granular details:

```json
{
  "commodity_id": "beans-brown"
}
```

*OR*

```json
{
  "Food_Item": "beans",
  "Item_Type": "brown",
  "Category": "1000 g",
  "Vendor_Type": "government"
}
```

**Response:**
Returns the predicted percentage change and a SHAP-based explanation showcasing exactly the top **8** driving features.
```json
{
  "metadata": {
    "commodity_id": "beans-brown",
    "Food_Item": "beans",
    "Vendor_Type": "government"
  },
  "forecast_horizon": "1_Month",
  "predicted_price_change_percent": 0.7,
  "xai_explanation": {
    "base_market_trend": 4.0,
    "top_driving_features": [
      {
        "feature": "Food_Inflation_Rate",
        "current_value": 0.0,
        "impact_percentage": -0.88,
        "direction": "decrease"
      }
      // ... up to 8 top features
    ]
  }
}
```

---

### `POST /simulate`
Simulates a prediction based on historical macro-economic and weather data for a specific year and month.

**Request Body:**
Includes the commodity selector (either `commodity_id` or the granular details) plus the target `Year` and `Month` to simulate:

```json
{
  "commodity_id": "beans-brown",
  "Year": 2024,
  "Month": 10
}
```

**Response:**
```json
{
  "metadata": {
    "commodity_id": "beans-brown",
    "Food_Item": "beans",
    "Vendor_Type": "government",
    "Year": 2024,
    "Month": 10,
    "exact_match_found": true
  },
  "forecast_horizon": "1_Month",
  "predicted_price_change_percent": 0.7,
  "actual_price_change_percent": 0.5,
  "error_delta_percent": 0.2,
  "xai_explanation": {
    "base_market_trend": 4.0,
    "top_driving_features": [
      {
        "feature": "Food_Inflation_Rate",
        "current_value": 0.0,
        "impact_percentage": -0.88,
        "direction": "decrease"
      }
      // ... up to 8 top features
    ]
  }
}
```

---

## Supported Commodities (`commodity_id` mappings)
The engine maps standard frontend names and all 29 official NBS food items from the audit database case-insensitively:
- **Frontend Aliases:** `tomatoes`, `rice-imported`, `scotch-bonnet`, `yam`, `white-garri`, `brown-beans`, `onions`, `eggs`
- **Standard NBS Mappings:**
  - Beans: `beans-brown`, `beans-white-black-eye`
  - Beef: `beef-bone-in`, `beef-boneless`
  - Bread: `bread-sliced`, `bread-unsliced`
  - Chicken: `chicken-feet`, `chicken-frozen`, `chicken-wings`
  - Eggs: `eggs-agric-1pcs`, `eggs-agric-12pcs`
  - Fish: `fish-catfish-smoked`, `fish-fish`, `fish-mudfish`
  - Garri: `garri-white`, `garri-yellow`
  - Milk: `milk-evaporated-tin`
  - Oil: `oil-groundnut`, `oil-palm`, `oil-vegetable`
  - Potato: `potato-irish`, `potato-sweet`
  - Rice: `rice-agric`, `rice-imported`, `rice-local`, `rice-medium-grained`, `rice-ofada`
  - Tomato: `tomato-tomato`
  - Yam: `yam-tuber`

