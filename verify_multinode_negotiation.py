import requests
import json

AGENTS = [
    {"name": "Pharmacy A", "url": "http://localhost:8000/negotiate"},
    {"name": "Pharmacy B", "url": "http://localhost:8001/negotiate"}
]

def check_price(product_query, qty=1):
    print(f"\n--- Negotiating for '{product_query}' (Qty: {qty}) ---")
    
    best_offer = None
    
    for agent in AGENTS:
        try:
            payload = {
                "intent": "inquiry",
                "product_query": product_query,
                "quantity": qty
            }
            
            resp = requests.post(agent["url"], json=payload)
            data = resp.json()
            
            print(f"[{agent['name']}] Status: {data['status']} | Price: {data['price_per_unit']} {data['currency']}")
            
            if data["status"] == "available":
                if best_offer is None or data["price_per_unit"] < best_offer["price"]:
                    best_offer = {
                        "agent": agent["name"],
                        "price": data["price_per_unit"],
                        "currency": data["currency"]
                    }
                    
        except Exception as e:
            print(f"[{agent['name']}] Connection Failed: {e}")

    if best_offer:
        print(f"\n>>> DECISION: Best deal is {best_offer['agent']} at {best_offer['price']} {best_offer['currency']}")
    else:
        print("\n>>> DECISION: No deal found.")

if __name__ == "__main__":
    check_price("Ecosprin 75mg")
    check_price("Dolo 650")
    check_price("NonExistent Medicine")
