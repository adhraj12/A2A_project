import requests
import json

URL = "http://localhost:8013/negotiate" # Pharmacy B (City Health)

def test_ai_reasoning():
    print("=== Testing AI Seller Reasoning ===\n")
    
    # Query that requires 'understanding' (Fever -> Dolo)
    query = "I have a high fever and body pain. Do you have anything?"
    
    print(f">>> Customer: '{query}'")
    
    payload = {
        "query": query,
        "quantity": 1
    }
    
    try:
        resp = requests.post(URL, json=payload)
        data = resp.json()
        
        print("\n>>> Seller Agent Response:")
        print(f"Status: {data['status']}")
        print(f"Item: {data.get('item_name', 'N/A')}")
        print(f"Price: {data['price_per_unit']} {data['currency']}")
        print(f"Message: {data['message']}")
        
        if data['status'] == 'available' and 'Dolo' in data.get('item_name', ''):
            print("\n[SUCCESS] AI correctly mapped 'fever' to 'Dolo 650'.")
        else:
            print("\n[PARTIAL/FAILED] See response above.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ai_reasoning()
