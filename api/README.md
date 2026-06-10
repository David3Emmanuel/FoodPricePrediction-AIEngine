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
python scripts/setup_db.py
```

### 2. Run the API
From the project root:
```bash
uvicorn api.app:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can view the interactive documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## Endpoints

### `POST /predict`
Predicts the 1-month price change for a specific commodity.

**Request Body:**
```json
{
  "Food_Item": "maize",
  "Item_Type": "grain",
  "Category": "cereals",
  "Vendor_Type": "retail"
}
```

**Response:**
Returns the predicted percentage change and a SHAP-based explanation of the top driving features.
