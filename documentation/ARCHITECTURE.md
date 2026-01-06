# Protocol Zero - Architecture Explained

This document explains how Protocol Zero works in simple terms. Even if you're not deeply technical, you should be able to understand the overall system after reading this.

---

## What is Protocol Zero?

Protocol Zero is a system that allows AI agents to buy and sell products with each other on behalf of humans. Think of it like this:

- **Today:** You open Zomato, search for restaurants, compare prices, and place an order yourself.
- **With Protocol Zero:** You tell your AI "Order me dinner" and it automatically finds restaurants, compares prices, and places the order for you.

The key difference is that instead of one big app (like Zomato) controlling everything, each business has its own AI agent that can talk directly to your AI agent.

---

## The Three Main Components

Protocol Zero has three parts that work together:

```
    YOU (Human)
        |
        | "Buy me Ecosprin"
        v
+-------------------+
|   BUYER AGENT     |  <-- Your personal AI shopping assistant
+-------------------+
        |
        | "Who sells medicine nearby?"
        v
+-------------------+
|   MARKETPLACE     |  <-- Directory of all seller agents
+-------------------+
        |
        | "Here are 2 pharmacies"
        v
+-------------------+     +-------------------+
|   SELLER AGENT    |     |   SELLER AGENT    |
|   (Pune Chemist)  |     |   (City Health)   |
+-------------------+     +-------------------+
        |                         |
        v                         v
   [Inventory]               [Inventory]
   Ecosprin: ₹4.50           Ecosprin: ₹4.20
```

Let's understand each one:

---

## 1. The Buyer Agent (Your AI Assistant)

**What it is:** An AI-powered service that acts on YOUR behalf.

**What it does:**
- Understands what you want to buy from your natural language request
- Searches the marketplace for relevant sellers
- Contacts multiple sellers to check prices
- Compares options and recommends the best one
- Places the order once you confirm

**How it thinks:**
When you say "Buy me Ecosprin", the Buyer Agent doesn't just do a keyword search. It actually reasons:
1. "Ecosprin is a medicine, so I should look for healthcare/pharmacy stores"
2. "Let me search the marketplace for healthcare agents near the user"
3. "I found 2 pharmacies. Let me ask both for their price"
4. "Pune Chemist says ₹4.50, City Health says ₹4.20"
5. "City Health is cheaper. I'll recommend that to the user"

This reasoning happens automatically using Google's Gemini AI.

**Technology:** Python + FastAPI + Gemini 2.5 Flash

---

## 2. The Marketplace (The Directory)

**What it is:** A simple registry that stores information about all seller agents.

**What it does NOT do:** 
- It does NOT process transactions
- It does NOT take a commission
- It does NOT store inventory or prices

**What it DOES do:**
- Stores the name, category, and location of each seller
- Stores the URL where each seller agent can be contacted
- Allows searching by category (healthcare, food, retail) and location (pincode)

**Think of it like:** A phone directory. It tells you "Pune Chemist is a pharmacy at this address and you can call them at this number." But it doesn't make the call for you or handle your conversation.

**Why this matters:** Because the marketplace is just a directory, it doesn't become a middleman that can charge fees. Buyers and sellers talk directly to each other.

**Technology:** Next.js + JSON file (can scale to Firestore database)

---

## 3. The Seller Agent (The Store's AI Representative)

**What it is:** An AI-powered service that represents a specific business.

**Each seller agent knows:**
- What products the store has in stock
- What the prices are
- Whether they can deliver to a given location

**What it does:**
1. Receives queries from buyer agents (e.g., "Do you have Ecosprin?")
2. Uses AI to understand the query (even if phrased differently)
3. Checks its inventory
4. Responds with availability and price
5. If an order is placed, it updates the inventory and generates a payment link

**Why AI is needed here:**
A customer might ask for "blood thinner tablets" instead of "Ecosprin 75mg". A simple keyword match would fail. But because the seller agent uses Gemini AI, it understands that "blood thinner" refers to Ecosprin and returns the correct product.

**Technology:** Python + FastAPI + Gemini 2.0 Flash

---

## The Communication Protocol

For all these agents to talk to each other, they need to speak the same language. This is the "Protocol Zero" standard.

**Negotiation (checking price and availability):**

Buyer Agent sends:
```
POST /negotiate
{
    "query": "Ecosprin 75mg",
    "quantity": 1
}
```

Seller Agent responds:
```
{
    "status": "available",
    "price_per_unit": 42.50,
    "currency": "INR",
    "agent_name": "Pune Chemist"
}
```

**Ordering (placing the actual order):**

Buyer Agent sends:
```
POST /order
{
    "product_query": "Ecosprin 75mg",
    "quantity": 1,
    "delivery_address": "123 Main St, Pune",
    "phone": "9876543210",
    "email": "user@example.com"
}
```

Seller Agent responds:
```
{
    "status": "reserved",
    "transaction_id": "tx_abc123",
    "payment_link": "https://pay.protocolzero.com/tx_abc123"
}
```

---

## How a Complete Transaction Works

Let's trace through what happens when you say "Buy me Ecosprin":

**Step 1: You send a message**
You send: `{"message": "I want to buy Ecosprin"}`
This goes to the Buyer Agent at `http://localhost:8000/chat`

**Step 2: Buyer Agent searches the marketplace**
The Buyer Agent's AI decides: "Ecosprin is medicine, so category = healthcare"
It calls: `GET http://localhost:3000/api/agents?category=healthcare`
The marketplace returns: `[Pune Chemist at port 8001, City Health at port 8002]`

**Step 3: Buyer Agent contacts all sellers (in parallel)**
It sends to BOTH:
- `POST http://localhost:8001/negotiate` → {"query": "Ecosprin"}
- `POST http://localhost:8002/negotiate` → {"query": "Ecosprin"}

**Step 4: Seller Agents check their inventory**
Pune Chemist's AI reads from `pharmacy_a.json`, finds Ecosprin at ₹4.50
City Health's AI reads from `pharmacy_b.json`, finds Ecosprin at ₹4.20

**Step 5: Buyer Agent compares and responds**
The Buyer Agent receives both prices, determines City Health is cheaper, and says:
"City Health has Ecosprin for ₹4.20. Would you like to order?"

**Step 6: You confirm**
You send: `{"message": "Yes, order it"}`

**Step 7: Buyer Agent places the order**
It sends to City Health:
```
POST http://localhost:8002/order
{
    "product_query": "Ecosprin",
    "quantity": 1,
    "delivery_address": "Your address",
    "phone": "Your phone",
    "email": "Your email"
}
```

**Step 8: Seller Agent processes the order**
City Health's agent:
1. Reduces stock in `pharmacy_b.json` by 1
2. Creates a transaction record in `pharmacy_b_orders.json`
3. Generates a payment link
4. Returns the link to the Buyer Agent

**Step 9: You get the payment link**
Buyer Agent says: "Order placed! Pay here: https://pay.protocolzero.com/tx_abc123"

---

## Why This Design is Secure

You might wonder: "What if someone tricks the AI into giving a low price?"

**The Negotiation endpoint (/negotiate) uses AI** - so it can understand natural language queries. But it can only READ from the inventory. It cannot change prices.

**The Order endpoint (/order) uses pure code** - no AI is involved in the transaction logic. The price comes directly from the database, the stock is decremented by code, and the payment link is generated by code. Even if someone tried to inject a malicious prompt, the transaction logic is untouchable.

This is called a "hybrid design" - AI for flexibility where it's safe, code for security where it matters.

---

## File Structure

Here's what each folder contains:

```
A2A_project/
├── buyer_agent/           # Your personal AI shopping assistant
│   ├── main.py            # The main application
│   ├── tools.py           # Functions the AI can call
│   └── requirements.txt   # Python dependencies
│
├── seller_agent/          # Template for any store's AI agent
│   ├── main.py            # The main application
│   ├── inventory/         # Store data
│   │   ├── pharmacy_a.json    # Pune Chemist's products
│   │   └── pharmacy_b.json    # City Health's products
│   └── requirements.txt   # Python dependencies
│
├── marketplace/           # The agent directory
│   ├── app/               # Next.js application
│   │   └── api/agents/    # API endpoints
│   ├── data/agents.json   # Registry of all seller agents
│   └── package.json       # JavaScript dependencies
│
└── documentation/         # You are here!
    ├── SETUP_GUIDE.md
    └── ARCHITECTURE.md
```

---

## Key Concepts to Remember

1. **Agents talk to agents** - The Buyer Agent and Seller Agents communicate directly. The marketplace is just a directory.

2. **AI handles understanding** - Gemini AI interprets natural language so you don't need exact product names.

3. **Code handles transactions** - The actual order processing is deterministic code, not AI, for security.

4. **Protocol Zero is a standard** - Any business can create a seller agent that follows this protocol and join the network.

5. **Zero commission** - There's no middleman taking a cut. Buyers and sellers transact directly.

---

## What Makes This Different from Zomato/Amazon?

| Aspect | Zomato/Amazon | Protocol Zero |
|--------|--------------|---------------|
| Who controls the platform? | The company | No one (decentralized) |
| Commission | 25-30% | 0% |
| Who builds the AI? | The platform | Each business |
| Can any business join? | Only if approved | Yes, anyone |
| Can AI negotiate? | No | Yes |
| Who holds customer data? | The platform | The individual sellers |

Protocol Zero is more like the internet itself - an open standard that anyone can build on - rather than a proprietary platform.
