"""
Protocol Zero - Buyer Agent Tools
These functions are called by the Gemini model via Function Calling.
"""
import requests
from typing import List, Dict, Any

# Configuration
MARKETPLACE_URL = "http://localhost:3000/api/agents"

def search_marketplace(category: str, pincode: str = None) -> Dict[str, Any]:
    """
    Search the Protocol Zero marketplace for available seller agents.
    
    Args:
        category: The type of store to search for (e.g., 'healthcare', 'food', 'retail')
        pincode: Optional pincode to filter by location
    
    Returns:
        A dictionary with 'agents' list containing name, endpoint, and description of each agent.
    """
    print(f"[Tool] Searching marketplace: category={category}, pincode={pincode}")
    
    try:
        params = {"category": category}
        if pincode:
            params["pincode"] = pincode
            
        response = requests.get(MARKETPLACE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Simplify the response for the AI
        agents = []
        for agent in data.get("agents", []):
            agents.append({
                "name": agent["name"],
                "endpoint": agent["endpoint"],
                "description": agent.get("description", ""),
                "city": agent.get("address", {}).get("city", "Unknown"),
                "pincode": agent.get("address", {}).get("pincode", "")
            })
        
        return {
            "status": "success",
            "count": len(agents),
            "agents": agents
        }
        
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to reach marketplace: {str(e)}",
            "agents": []
        }


def contact_seller(agent_url: str, product_query: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Contact a seller agent to check product availability and price.
    
    Args:
        agent_url: The endpoint URL of the seller agent (from marketplace search)
        product_query: The product name or description to search for
        quantity: Number of units needed
    
    Returns:
        A dictionary with status, price, and agent response.
    """
    print(f"[Tool] Contacting seller: {agent_url} for '{product_query}' x{quantity}")
    
    # Normalize URL - ensure it ends with /negotiate
    negotiate_url = agent_url.rstrip('/')
    if not negotiate_url.endswith('/negotiate'):
        negotiate_url = f"{negotiate_url}/negotiate"
    
    try:
        payload = {
            "query": product_query,
            "quantity": quantity
        }
        
        response = requests.post(negotiate_url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        return {
            "status": data.get("status", "unknown"),
            "agent_name": data.get("agent_name", "Unknown Store"),
            "price_per_unit": data.get("price_per_unit", 0),
            "total_price": data.get("total_price", 0),
            "currency": data.get("currency", "INR"),
            "message": data.get("message", ""),
            "endpoint": agent_url
        }
        
    except requests.RequestException as e:
        return {
            "status": "unreachable",
            "agent_name": "Unknown",
            "message": f"Could not contact seller: {str(e)}",
            "endpoint": agent_url
        }


def place_order(
    agent_url: str, 
    product_query: str, 
    quantity: int, 
    delivery_address: str,
    phone: str,
    email: str
) -> Dict[str, Any]:
    """
    Place an order with a seller agent after user confirmation.
    
    Args:
        agent_url: The endpoint URL of the seller agent
        product_query: The product to order
        quantity: Number of units to order
        delivery_address: Full delivery address (street, city, pincode)
        phone: User's phone number for delivery updates
        email: User's email for order confirmation
    
    Returns:
        A dictionary with transaction ID and payment link.
    """
    print(f"[Tool] Placing order at {agent_url}: {product_query} x{quantity}")
    print(f"[Tool] Delivery to: {delivery_address}, Phone: {phone}, Email: {email}")
    
    # Normalize URL - ensure it ends with /order
    order_url = agent_url.rstrip('/')
    if not order_url.endswith('/order'):
        order_url = f"{order_url}/order"
    
    try:
        payload = {
            "product_query": product_query,
            "quantity": quantity,
            "delivery_address": delivery_address,
            "phone": phone,
            "email": email
        }
        
        response = requests.post(order_url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        return {
            "status": data.get("status", "unknown"),
            "transaction_id": data.get("transaction_id"),
            "payment_link": data.get("payment_link"),
            "message": data.get("message", "")
        }
        
    except requests.RequestException as e:
        return {
            "status": "failed",
            "message": f"Order failed: {str(e)}"
        }


# Tool list for Gemini
TOOLS = [search_marketplace, contact_seller, place_order]
