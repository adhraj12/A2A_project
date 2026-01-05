import requests
import json
import os

# Configuration
MARKETPLACE_URL = "http://localhost:3000/api/agents"
API_KEY = "zk_proto_zero_secret_key_123"

def search_marketplace_tool(category: str = None, pincode: str = None, city: str = None):
    """
    Simulated Tool Function: Searching the Marketplace.
    """
    print(f"\n[Tool Use] Calling Marketplace API...")
    print(f"  Params: category={category}, pincode={pincode}, city={city}")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    params = {}
    if category: params['category'] = category
    if pincode: params['pincode'] = pincode
    if city: params['city'] = city
    
    try:
        response = requests.get(MARKETPLACE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  [Success] Found {data['count']} agents.")
            for agent in data['agents']:
                print(f"    - {agent['name']} ({agent['category']}) in {agent['address']['city']} [{agent['address']['pincode']}]")
                print(f"      Endpoint: {agent['endpoint']}")
        elif response.status_code == 401:
            print(f"  [Error] Unauthorized: {response.text}")
        else:
            print(f"  [Error] API returned {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"  [Exception] Failed to contact marketplace: {e}")

def simulate_user_agent_flow():
    print("=== Simulating User Agent Flow ===")
    
    # Scene 1: User says "Find me medical stores in Pune"
    print("\n>>> User: 'Find medical stores in Pune (411038)'")
    search_marketplace_tool(category="healthcare", pincode="411038")
    
    # Scene 2: User says "Find grocery in Mumbai"
    print("\n>>> User: 'Find grocery in Mumbai (400001)'")
    search_marketplace_tool(category="healthcare", pincode="400001") # Testing our new agent

    # Scene 3: Unauthenticated Attack
    print("\n>>> Attacker: Trying to access without key...")
    global API_KEY
    API_KEY = "wrong_key"
    search_marketplace_tool(category="healthcare")

if __name__ == "__main__":
    simulate_user_agent_flow()
