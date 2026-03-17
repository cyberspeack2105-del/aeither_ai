import requests
import json

def test_ai():
    url = "http://127.0.0.1:8000/ask"
    payload = {
        "prompt": "Explain what is Gravity in Physics",
        "language": "English"
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing AI Backend at {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] AI response received successfully!")
            print("-" * 30)
            print(result.get("answer", "No answer found in response"))
            print("-" * 30)
        else:
            print(f"[ERROR] AI request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Error during AI verification: {e}")

if __name__ == "__main__":
    test_ai()
