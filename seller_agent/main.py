import argparse
import json
import uvicorn
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

# --- CLI Arguments for Multi-Instance Support ---
parser = argparse.ArgumentParser(description="Protocol Zero Seller Agent")
parser.add_argument("--port", type=int, default=8000, help="Port to run the agent on")
parser.add_argument("--inventory", type=str, default="inventory/pharmacy_a.json", help="Path to inventory JSON file")
args = parser.parse_args()

# Load Inventory on Startup
try:
    with open(args.inventory, "r") as f:
        INVENTORY_DATA = json.load(f)
        print(f"Loaded inventory from {args.inventory}: {INVENTORY_DATA['store_name']}")
except FileNotFoundError:
    print(f"Error: Inventory file {args.inventory} not found.")
    exit(1)

app = FastAPI(title=f"Seller Agent: {INVENTORY_DATA['store_name']}")

# --- Gemini Configuration ---
# Note: In production, use os.environ["GEMINI_API_KEY"]
# For hackathon/demo, we assume the user provides it or we load from .env
from dotenv import load_dotenv
load_dotenv()

# We will configure Gemini dynamically inside the request if key is provided, 
# or use a default if available in env.
api_key = os.getenv("GEMINI_API_KEY") 
if api_key:
    genai.configure(api_key=api_key)

# --- Tool Definition ---
def check_inventory(product_name: str):
    """
    Search the inventory for a product by name or tag.
    Returns the product details including stock and price.
    """
    print(f"[Tool] Checking inventory for: {product_name}")
    inventory = INVENTORY_DATA["products"]
    query = product_name.lower()
    
    found_items = []
    for item in inventory:
        if query in item["name"].lower() or item["name"].lower() in query:
            found_items.append(item)
            continue
        for tag in item.get("tags", []):
             if query == tag.lower():
                 found_items.append(item)
                 break
    
    if not found_items:
        return {"status": "not_found", "message": f"No products found matching '{product_name}'"}
        
    return {"status": "found", "results": found_items}

tools_list = [check_inventory]

# --- Protocol Zero Schema ---
class NegotiationRequest(BaseModel):
    query: str # Natural language query
    quantity: int = 1

class NegotiationResponse(BaseModel):
    status: str # "available", "out_of_stock", "not_found"
    price_per_unit: float
    total_price: float
    currency: str
    agent_name: str
    message: str # Reasoning from Gemini

class OrderRequest(BaseModel):
    product_query: str
    quantity: int
    user_contact: str

class OrderResponse(BaseModel):
    status: str
    transaction_id: Optional[str] = None
    payment_link: Optional[str] = None
    message: str

# --- The Endpoint ---
@app.post("/negotiate", response_model=NegotiationResponse)
async def negotiate(request: NegotiationRequest):
    # If no API Key, fall back to simple logic (failsafe)
    if not api_key:
        return {
            "status": "error",
            "price_per_unit": 0,
            "total_price": 0,
            "currency": "INR",
            "agent_name": INVENTORY_DATA["store_name"],
            "message": "GEMINI_API_KEY not set. Cannot use AI reasoning."
        }

    model = genai.GenerativeModel('gemini-2.0-flash', tools=tools_list)
    chat = model.start_chat(enable_automatic_function_calling=True)

    # Prompt Engineering for the Seller Persona
    prompt = f"""
    You are the intelligent sales agent for '{INVENTORY_DATA['store_name']}'.
    Product Query: "{request.query}"
    Quantity Needed: {request.quantity}

    Task:
    1. Use the 'check_inventory' tool to find the product.
    2. Check if we have enough stock (tool returns stock).
    3. If multiple items match, pick the best fit.
    4. Return your final answer in JSON format (do not use markdown).
    
    JSON Structure:
    {{
        "status": "available" | "out_of_stock" | "not_found",
        "price_per_unit": <float>,
        "item_name": "<name>",
        "currency": "INR",
        "message": "<Polite message to customer>"
    }}
    """
    
    try:
        response = chat.send_message(prompt)
        # Parse the JSON response from Gemini
        # Note: Gemini might wrap it in ```json ... ```
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        
        result = json.loads(text)
        
        return {
            "status": result.get("status", "not_found"),
            "price_per_unit": result.get("price_per_unit", 0),
            "total_price": result.get("price_per_unit", 0) * request.quantity,
            "currency": result.get("currency", "INR"),
            "agent_name": INVENTORY_DATA["store_name"],
            "message": result.get("message", "")
        }

    except Exception as e:
        print(f"Gemini Error (Falling back to logic): {e}")
        # Fallback: Manual Logic (Same as before)
        inventory = INVENTORY_DATA["products"]
        found_item = None
        query = request.query.lower()
        
        for item in inventory:
            if query in item["name"].lower() or item["name"].lower() in query:
                found_item = item
                break
            for tag in item.get("tags", []):
                 if tag.lower() in query: # Corrected: Check if tag is inside the query sentence
                     found_item = item
                     break
            if found_item: break
        
        if found_item:
             return {
                "status": "available",
                "price_per_unit": found_item["price"],
                "total_price": found_item["price"] * request.quantity,
                "currency": found_item["currency"],
                "agent_name": INVENTORY_DATA["store_name"],
                "message": f"AI Overloaded. Found matches via fallback: {found_item['name']}"
            }
        else:
            return {
                "status": "not_found",
                "price_per_unit": 0,
                "total_price": 0,
                "currency": "INR",
                "agent_name": INVENTORY_DATA["store_name"],
                "message": f"AI Error: {str(e)[:50]}... and no local match."
            }

# --- Order Endpoint (Deterministic) ---
@app.post("/order", response_model=OrderResponse)
async def create_order(request: OrderRequest):
    # RELOAD inventory to get fresh stock (Concurrency handling start)
    try:
        with open(args.inventory, "r") as f:
            current_data = json.load(f)
    except Exception as e:
         raise HTTPException(status_code=500, detail="Inventory read failed")

    inventory = current_data["products"]
    
    # 1. Search Logic (Simple Fuzzy for Order)
    found_item = None
    item_index = -1
    query = request.product_query.lower()
    
    for idx, item in enumerate(inventory):
        if query in item["name"].lower() or item["name"].lower() in query:
            found_item = item
            item_index = idx
            break
            
    if not found_item:
        return {
            "status": "failed",
            "message": "Product not found during order processing."
        }

    # 2. Strict Stock Check
    if found_item["stock"] < request.quantity:
        return {
            "status": "failed",
            "message": f"Insufficient stock. Only {found_item['stock']} left."
        }

    # 3. Decrement Stock (The Transaction)
    current_data["products"][item_index]["stock"] -= request.quantity
    
    # 4. Persist Inventory Update
    with open(args.inventory, "w") as f:
        json.dump(current_data, f, indent=2)

    # 5. Generate Transaction
    import uuid
    tx_id = f"tx_{uuid.uuid4().hex[:8]}"
    payment_link = f"https://pay.protocolzero.com/{tx_id}"
    
    # 6. Save Order
    order_record = {
        "tx_id": tx_id,
        "product": found_item["name"],
        "qty": request.quantity,
        "amount": found_item["price"] * request.quantity,
        "contact": request.user_contact,
        "status": "PENDING_PAYMENT"
    }
    
    orders_file = args.inventory.replace(".json", "_orders.json")
    try:
        with open(orders_file, "r") as f:
            orders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        orders = []
        
    orders.append(order_record)
    
    with open(orders_file, "w") as f:
        json.dump(orders, f, indent=2)

    return {
        "status": "reserved",
        "transaction_id": tx_id,
        "payment_link": payment_link,
        "message": "Stock reserved for 10 minutes. Please complete payment."
    }

if __name__ == "__main__":
    print(f"Starting {INVENTORY_DATA['store_name']} on port {args.port}...")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
