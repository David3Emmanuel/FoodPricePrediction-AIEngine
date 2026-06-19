import requests
import json

def test_prediction():
    url = "http://127.0.0.1:8000/predict"
    
    # Sample payload based on the PredictionRequest model in api/app.py
    payload = {
        "Food_Item": "maize",
        "Item_Type": "grain",
        "Category": "cereals",
        "Vendor_Type": "retail"
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("[SUCCESS]")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[FAILED] Status code: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("[CONNECTION ERROR] Is the API running? Run 'uvicorn api.app:app --reload' in another terminal.")

def test_live_prices():
    url = "http://127.0.0.1:8000/live"
    print(f"\nSending request to {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            res_json = response.json()
            print("[SUCCESS]")
            print(f"Status: {res_json.get('status')}")
            print(f"Item Count: {res_json.get('count')}")
            # Print first 3 items as a sample
            prices = res_json.get('prices', [])
            print(f"Sample prices (showing up to 3 of {len(prices)}):")
            for item in prices[:3]:
                print(f"  - {item.get('commodity_id') or 'N/A'} ({item.get('Food_Item')} {item.get('Item_Type')}): NGN {item.get('Price_NGN')} in {item.get('State')} (Year: {item.get('Year')}, Week: {item.get('Week')})")
        else:
            print(f"[FAILED] Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("[CONNECTION ERROR] Is the API running? Run 'uvicorn api.app:app --reload' in another terminal.")

if __name__ == "__main__":
    test_prediction()
    test_live_prices()
