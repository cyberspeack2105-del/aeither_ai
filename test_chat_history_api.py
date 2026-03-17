import requests
import json
import time

DATA_API_URL = "http://127.0.0.1:8080"

def test_chat_history():
    user = "test_user_history"
    chat_id = "test_chat_" + str(int(time.time()))
    
    print(f"--- Testing Chat History for user: {user} ---")
    
    # 1. Save a message
    payload = {
        "user_name": user,
        "chat_id": chat_id,
        "message": "Hello, this is a test message",
        "sender": "user"
    }
    print(f"Saving message to chat {chat_id}...")
    save_res = requests.post(f"{DATA_API_URL}/save_chat", json=payload)
    if save_res.status_code == 200:
        print("[SUCCESS] Message saved successfully")
    else:
        print(f"[ERROR] Failed to save message: {save_res.text}")
        return

    # 2. Get history
    print("Fetching user history...")
    hist_res = requests.get(f"{DATA_API_URL}/history/{user}")
    if hist_res.status_code == 200:
        history = hist_res.json()
        print(f"[SUCCESS] History retrieved. Total chats for user: {len(history)}")
        found = any(h["_id"] == chat_id for h in history)
        if found:
            print(f"[SUCCESS] Chat {chat_id} found in history sidebar data")
        else:
            print(f"[ERROR] Chat {chat_id} NOT found in history")
    else:
        print(f"[ERROR] Failed to fetch history: {hist_res.text}")

    # 3. Get specific chat messages
    print(f"Fetching messages for chat {chat_id}...")
    chat_res = requests.get(f"{DATA_API_URL}/chat/{chat_id}")
    if chat_res.status_code == 200:
        messages = chat_res.json()
        print(f"[SUCCESS] Chat messages retrieved. Total messages: {len(messages)}")
        if len(messages) > 0 and messages[0]["message"] == "Hello, this is a test message":
            print("[SUCCESS] Message content verified")
        else:
            print("[ERROR] Message content mismatch or missing")
    else:
        print(f"[ERROR] Failed to fetch chat: {chat_res.text}")

if __name__ == "__main__":
    test_chat_history()
