import requests
try:
    response = requests.get("http://127.0.0.1:8080/", timeout=5)
    print(f"Data Server Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error connecting to Data Server: {e}")
