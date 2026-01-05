import requests
import json
import time

AGENT_URL = "http://localhost:8000" # Pharmacy A

def run_transaction_flow():
    print("=== Transaction Simulation Phase ===\n")
    
    # 1. Check Initial Stock (using /negotiate to peak)
    # Note: Negotiate doesn't show stock, so we rely on what we know (it started with 50)
    
    # 2. Place Order
    print(">>> User: 'I want to buy 5 Ecosprin'")
    payload = {
        "product_query": "Ecosprin 75mg",
        "quantity": 5,
        "user_contact": "alice@example.com"
    }
    
    try:
        resp = requests.post(f"{AGENT_URL}/order", json=payload)
        data = resp.json()
        print(f"Server Response: {json.dumps(data, indent=2)}")
        
        if data["status"] == "reserved":
            print("[SUCCESS] Order Placed and Stock Reserved.")
            print(f"Transaction ID: {data['transaction_id']}")
            print(f"Payment Link: {data['payment_link']}")
        else:
            print(f"[FAILED] {data['message']}")
            
    except Exception as e:
        print(f"Error: {e}")

    # 3. Verify Stock Depletion (Simulating a second user trying to empty stock)
    print("\n>>> User B: 'I want to buy 50 Ecosprin (Everything)'")
    payload["quantity"] = 50 
    # Logic: Should fail because 50 - 5 = 45 left.
    
    try:
        resp = requests.post(f"{AGENT_URL}/order", json=payload)
        data = resp.json()
        print(f"Server Response: {json.dumps(data, indent=2)}")
        
        if data["status"] == "failed":
            print("[SUCCESS] Stock Logic Verified. Order correctly rejected.")
        else:
            print("[FAILED] Double Spending Detected! Stock did not update.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_transaction_flow()
