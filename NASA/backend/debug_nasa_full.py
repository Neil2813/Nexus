"""Debug script to save full NASA OSDR API response"""
import requests
import json

url = "https://osdr.nasa.gov/osdr/data/search"
params = {"size": 3, "from": 0}

print("Fetching from NASA OSDR API...")

try:
    response = requests.get(url, params=params, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        # Save to file
        with open("nasa_response.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ SUCCESS! Status: {response.status_code}")
        print(f"✅ Response saved to: nasa_response.json")
        print(f"\nResponse structure:")
        print(f"  Type: {type(data)}")
        print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
        
        if isinstance(data, dict) and 'hits' in data:
            hits = data['hits']
            print(f"\n  hits type: {type(hits)}")
            if isinstance(hits, dict):
                print(f"  hits keys: {list(hits.keys())}")
                if 'total' in hits:
                    print(f"  total: {hits['total']}")
                if 'hits' in hits:
                    print(f"  hits array length: {len(hits['hits'])}")
                    if hits['hits']:
                        first_hit = hits['hits'][0]
                        print(f"\n  First hit keys: {list(first_hit.keys())}")
                        if '_source' in first_hit:
                            source = first_hit['_source']
                            print(f"  _source keys: {list(source.keys())[:10]}")
                            print(f"  Study Title: {source.get('Study Title', 'N/A')}")
                            print(f"  Study ID: {source.get('Study Identifier', first_hit.get('_id', 'N/A'))}")
        
        print(f"\n✅ Check nasa_response.json for full details")
        
    else:
        print(f"❌ ERROR: Status {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ EXCEPTION: {type(e).__name__}: {e}")
