"""
Protocol Zero - Buyer Agent
The intelligent client that orchestrates marketplace discovery and seller negotiation.
Uses Gemini 2.5 Flash with Function Calling in a ReAct loop.
"""
import json
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

from tools import TOOLS, search_marketplace, contact_seller, place_order

load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY", "Put your API key here")
genai.configure(api_key=API_KEY)

app = FastAPI(title="Protocol Zero - Buyer Agent")

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request/Response Models ---
class ChatRequest(BaseModel):
    message: str
    user_location: Optional[str] = "411038"  # Default pincode
    user_contact: Optional[str] = "user@demo.com"  # For order placement

class ChatResponse(BaseModel):
    response: str
    actions_taken: List[str]
    order_details: Optional[Dict[str, Any]] = None

# --- System Prompt for Buyer Agent ---
SYSTEM_PROMPT = """You are an intelligent shopping assistant for Protocol Zero, a decentralized agent marketplace.
Your job is to help users find and purchase products from autonomous seller agents.

You have access to these tools:
1. search_marketplace(category, pincode) - Find seller agents by category (healthcare, food, retail) and location
2. contact_seller(agent_url, product_query, quantity) - Check price and availability with a specific seller
3. place_order(agent_url, product_query, quantity, user_contact) - Complete a purchase after user confirms

WORKFLOW:
1. When user wants to buy something, first determine the category (medicine=healthcare, food=food, etc.)
2. Search the marketplace to find relevant sellers
3. Contact ALL found sellers in parallel to compare prices
4. Present the best options to the user
5. If user confirms, place the order and provide the payment link

IMPORTANT RULES:
- Always compare prices from multiple sellers before recommending
- Never place an order without explicit user confirmation (they must say "yes", "confirm", "order", etc.)
- Be concise but friendly in your responses
- If no sellers are found or all are unreachable, inform the user clearly

User's location pincode: {pincode}
User's contact: {contact}
"""

# --- The Agentic Loop ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint implementing the ReAct (Reason + Act) pattern.
    Gemini will Think -> Call Tool -> Get Result -> Think -> Repeat until done.
    """
    actions_log = []
    order_result = None
    
    # Initialize model with tools
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        tools=TOOLS,
        system_instruction=SYSTEM_PROMPT.format(
            pincode=request.user_location,
            contact=request.user_contact
        )
    )
    
    # Start chat with automatic function calling enabled
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    try:
        # Send user message - Gemini will automatically call tools as needed
        response = chat.send_message(request.message)
        
        # Log any tool calls that were made
        for content in chat.history:
            if hasattr(content, 'parts'):
                for part in content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        actions_log.append(f"Called {fc.name}({dict(fc.args)})")
                    if hasattr(part, 'function_response') and part.function_response:
                        fr = part.function_response
                        # Check if it was an order
                        if fr.name == 'place_order':
                            try:
                                order_result = dict(fr.response)
                            except:
                                pass
        
        return ChatResponse(
            response=response.text,
            actions_taken=actions_log,
            order_details=order_result
        )
        
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Health Check ---
@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "buyer", "model": "gemini-2.5-flash"}


# --- Conversation Session Endpoint (for multi-turn) ---
class ConversationState:
    """Simple in-memory conversation store for demo purposes"""
    conversations: Dict[str, Any] = {}

conversation_store = ConversationState()

class MultiTurnChatRequest(BaseModel):
    session_id: str
    message: str
    user_location: Optional[str] = "411038"
    user_contact: Optional[str] = "user@demo.com"

@app.post("/chat/session", response_model=ChatResponse)
async def chat_session(request: MultiTurnChatRequest):
    """
    Multi-turn chat endpoint that maintains conversation history.
    Use this for complete order flows where user confirms after seeing prices.
    """
    actions_log = []
    order_result = None
    
    # Get or create chat session
    if request.session_id not in conversation_store.conversations:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=TOOLS,
            system_instruction=SYSTEM_PROMPT.format(
                pincode=request.user_location,
                contact=request.user_contact
            )
        )
        chat = model.start_chat(enable_automatic_function_calling=True)
        conversation_store.conversations[request.session_id] = chat
    else:
        chat = conversation_store.conversations[request.session_id]
    
    try:
        response = chat.send_message(request.message)
        
        # Log tool calls from this turn
        for content in chat.history[-4:]:  # Check recent history
            if hasattr(content, 'parts'):
                for part in content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        actions_log.append(f"Called {fc.name}")
                    if hasattr(part, 'function_response') and part.function_response:
                        fr = part.function_response
                        if fr.name == 'place_order':
                            try:
                                order_result = dict(fr.response)
                            except:
                                pass
        
        return ChatResponse(
            response=response.text,
            actions_taken=actions_log,
            order_details=order_result
        )
        
    except Exception as e:
        print(f"Error in session chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting Protocol Zero Buyer Agent...")
    print("Chat endpoint: POST http://localhost:8000/chat")
    print("Session chat:  POST http://localhost:8000/chat/session")
    uvicorn.run(app, host="0.0.0.0", port=8000)
