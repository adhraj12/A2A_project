# How to Run Protocol Zero - Step by Step Guide

This guide will help you set up and run the entire Protocol Zero A2A system on your local machine.

---

## Prerequisites

Before you begin, make sure you have these installed:

1. **Python 3.10 or higher** - Check by running `python --version` in terminal
2. **Node.js 18 or higher** - Check by running `node --version` in terminal
3. **Git** - Check by running `git --version` in terminal

---

## Step 1: Clone the Repository

Open a terminal (Command Prompt or PowerShell on Windows) and run:

```
git clone https://github.com/adhraj12/A2A_project.git
```

Then navigate into the project folder:

```
cd A2A_project
```

You should now see folders like `buyer_agent`, `seller_agent`, `marketplace`, etc.

---

## Step 2: Set Up the Gemini API Key

Create a file called `.env` in the root of the project (inside `A2A_project` folder):

```
GEMINI_API_KEY=replace_with_your_gemini_api_key
```

This key is used by both the Buyer Agent and Seller Agents.

---

## Step 3: Install Dependencies

You need to install dependencies for three components. Open THREE separate terminal windows.

### Terminal 1: Seller Agent Dependencies

```
cd A2A_project/seller_agent
pip install -r requirements.txt
```

You should see packages like `fastapi`, `uvicorn`, `google-generativeai` being installed.

### Terminal 2: Buyer Agent Dependencies

```
cd A2A_project/buyer_agent
pip install -r requirements.txt
```

### Terminal 3: Marketplace Dependencies

```
cd A2A_project/marketplace
npm install
```

This will take a minute. You'll see a `node_modules` folder appear when it's done.

---

## Step 4: Start All Services (4 Terminals Required)

You need to keep 4 terminal windows open, each running one service.

### Terminal 1: Start Seller Agent A (Pune Chemist)

```
cd A2A_project/seller_agent
python main.py --port 8001 --inventory inventory/pharmacy_a.json
```

**Expected output:**
```
Loaded inventory from inventory/pharmacy_a.json: Pune Chemist
Starting Pune Chemist on port 8001...
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Terminal 2: Start Seller Agent B (City Health)

```
cd A2A_project/seller_agent
python main.py --port 8002 --inventory inventory/pharmacy_b.json
```

**Expected output:**
```
Loaded inventory from inventory/pharmacy_b.json: City Health
Starting City Health on port 8002...
INFO:     Uvicorn running on http://0.0.0.0:8002
```

### Terminal 3: Start the Marketplace

```
cd A2A_project/marketplace
npm run dev
```

**Expected output:**
```
▲ Next.js 16.x.x
- Local: http://localhost:3000
✓ Starting...
```

### Terminal 4: Start the Buyer Agent

```
cd A2A_project/buyer_agent
python main.py
```

**Expected output:**
```
Starting Protocol Zero Buyer Agent...
Chat endpoint: POST http://localhost:8000/chat
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 5: Verify Everything is Running

Open a NEW terminal (Terminal 5) and run these checks:

### Check Marketplace

```
curl http://localhost:3000/api/agents?category=healthcare
```

Or in PowerShell:
```
Invoke-RestMethod -Uri "http://localhost:3000/api/agents?category=healthcare"
```

**Expected:** You should see data about Pune Chemist and City Health.

### Check Seller Agent A

```
curl http://localhost:8001/docs
```

Or open `http://localhost:8001/docs` in your browser. You should see the FastAPI documentation page.

### Check Buyer Agent

```
curl http://localhost:8000/health
```

**Expected:** `{"status": "healthy", "agent": "buyer", "model": "gemini-2.5-flash"}`

---

## Step 6: Test the Complete A2A Flow

Now for the exciting part! Send a chat request to the Buyer Agent:

### PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -ContentType "application/json" -Body '{"message": "I want to buy Ecosprin"}'
```

### Command Prompt (using curl):
```
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"I want to buy Ecosprin\"}"
```

**What happens behind the scenes:**
1. Buyer Agent receives your message
2. It searches the marketplace for healthcare agents
3. It finds Pune Chemist and City Health
4. It contacts BOTH to ask about Ecosprin
5. It compares prices and tells you the best option

**Expected response:** Something like "Pune Chemist has Ecosprin 75mg for ₹4.50" or similar.

---

## Step 7: Test with Custom User Details

To test with your own delivery address:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -ContentType "application/json" -Body '{
    "message": "Buy Ecosprin and confirm order",
    "user_details": {
        "delivery_address": "123 My Street, Pune 411038",
        "phone": "9876543210",
        "email": "myemail@example.com"
    }
}'
```

---

## Troubleshooting

### "Port already in use" error
Another process is using that port. Either:
- Kill the other process, or
- Use a different port: `python main.py --port 8003`

### "GEMINI_API_KEY not set" error
Make sure you created the `.env` file in the correct folder (same folder as `main.py`).

### Marketplace returns 401 Unauthorized
This happens if testing from outside localhost. For local testing, it should work automatically.

### "Module not found" error
You forgot to install dependencies. Go back to Step 3.

---

## Quick Start Summary

Once everything is set up, you just need to run these 4 commands in 4 terminals:

```
Terminal 1: cd seller_agent && python main.py --port 8001 --inventory inventory/pharmacy_a.json
Terminal 2: cd seller_agent && python main.py --port 8002 --inventory inventory/pharmacy_b.json
Terminal 3: cd marketplace && npm run dev
Terminal 4: cd buyer_agent && python main.py
```

Then test with:
```
POST http://localhost:8000/chat
{"message": "I want to buy Ecosprin"}
```
