# FoodPricePrediction-AIEngine

An AI-powered predictive engine designed to forecast national agricultural commodity prices. This project utilizes CatBoost for high-accuracy regression and SHAP (SHapley Additive exPlanations) to provide transparency into model decisions.

It integrates granular macroeconomic data from the **World Bank Data360 API**, real-time weather from Open Meteo, and conflict data from ACLED to provide a comprehensive view of market drivers.

## Project Structure
- `agri_price/`: Core Python package containing model prediction logic, data loading, and feature engineering.
- `api/`: FastAPI backend for serving model predictions via REST.
- `dashboard/`: Streamlit interactive dashboard for "what-if" scenario simulation.
- `data/`: Directory for datasets and the local SQLite feature store.
- `models/`: Storage for trained CatBoost model files (`.cbm`).
- `scripts/`: Utility scripts for database setup and model training.

## Quick Start

### 1. Environment Setup
We recommend using [uv](https://github.com/astral-sh/uv) for fast dependency management.

```bash
# Install dependencies
uv sync
```

### 2. Initialize the Feature Store
The API requires a local SQLite database to provide market context.
```bash
python scripts/setup_db.py
```

### 3. Launch the Services
You can run the API and the Dashboard independently:

- **Launch API:** `uvicorn api.app:app --reload` (See [api/README.md](api/README.md))
- **Launch Dashboard:** `streamlit run dashboard/app.py` (See [dashboard/README.md](dashboard/README.md))

## Documentation
- [API Documentation](api/README.md)
- [Dashboard Documentation](dashboard/README.md)
