# AgriPrice Scenario Simulator

This directory contains the Streamlit-based dashboard for the AgriPrice Prediction Engine. It provides an interactive interface for users to simulate market shocks (e.g., inflation spikes, weather changes) and observe predicted price fluctuations.

## Features
- **Interactive Scenarios:** Use sliders to simulate macroeconomic and environmental shocks.
- **Dynamic Filtering:** Select crops and vendor types to see specific forecasts.
- **Visual XAI:** Interactive SHAP charts explaining model decisions in real-time.
- **Baseline Comparison:** Uses historical data as a baseline for simulations.

## Setup & Running

### Prerequisites
- Ensure the root project dependencies are installed (see root `README.md`).

### Run the Dashboard
From the project root:
```bash
streamlit run dashboard/app.py
```
The dashboard will open in your default web browser (usually at `http://localhost:8501`).

## Usage
1. **Select Crop & Vendor:** Choose the commodity you want to analyze.
2. **Simulate Shocks:** Adjust the sliders in the sidebar for Inflation, Temperature, and Precipitation.
3. **Analyze Results:** View the predicted 1-month price change and the SHAP explanation chart to understand which factors had the most impact.
