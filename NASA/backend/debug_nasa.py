"""Debug script to test NASA OSDR API and see actual response"""
import requests
import json

url = "https://osdr.nasa.gov/osdr/data/search"
params = {"size": 5, "from": 0}

print("Testing NASA OSDR API...")
print(f"URL: {url}")
print(f"Params: {params}\n")

try:
    response = requests.get(url, params=params, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS! Response structure:")
        print(json.dumps(data, indent=2)[:2000])
    else:
        print(f"ERROR: {response.text[:500]}")
        
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")
