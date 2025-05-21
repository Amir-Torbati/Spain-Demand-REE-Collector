# scripts/test_esios_token.py

import os
import requests
import json
from datetime import datetime

# Set up
TOKEN = os.getenv("API_TOKEN")
HEADERS = {
    "Accept": "application/json; application/vnd.esios-api-v1+json",
    "Content-Type": "application/json",
    "Authorization": f"Token token={TOKEN}"
}

# Test: Demand on March 1, 2023 (valid date, available data)
test_date = "2023-03-01"
url = f"https://api.esios.ree.es/indicators/600?start_date={test_date}T00:00:00Z&end_date={test_date}T23:59:59Z&time_trunc=hour"

try:
    print(f"🔍 Testing ESIOS API for {test_date}...")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    print(f"✅ Success! Fetched {len(data['indicator']['values'])} records.")
    print("🔸 Sample:", json.dumps(data['indicator']['values'][:2], indent=2))  # show first 2 records

except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e} | Status Code: {response.status_code}")
except Exception as e:
    print(f"❌ General Error: {e}")
