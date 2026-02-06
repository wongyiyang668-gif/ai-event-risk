import httpx
import json
from datetime import datetime

def test_create_event():
    url = "http://127.0.0.1:8000/events"
    payload = {
        "content": "Alert: Suspicious activity detected in the network firewall logs from an unknown IP address.",
        "source": "firewall-logs-01",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Successfully received response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    # Note: This script assumes the server is running at http://127.0.0.1:8000
    test_create_event()
