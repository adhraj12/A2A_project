# Protocol Zero: The Serverless, Headless Agent Economy

> **Current Status**: Prototype / MVP (Hackathon Phase)
> **Goal**: A decentralized marketplace where AI Buyer Agents negotiate with AI Seller Agents without middlemen.

## Project Structure

```
A2A_project/
├── buyer_agent/           # 🤖 Python + FastAPI + Gemini 2.5 Flash
│   ├── main.py            # Core ReAct loop, /chat endpoint (API Only)
│   ├── tools.py           # Tools: search_marketplace, contact_seller, place_order
│   └── requirements.txt   # Dependencies
│
├── seller_agent/          # 🏪 Python + FastAPI + Gemini 2.0 Flash
│   ├── main.py            # /negotiate (AI) and /order (Deterministic) endpoints
│   ├── inventory/         # Local JSON inventory files (pharmacy_a.json, etc.)
│   └── requirements.txt   # Dependencies
│
├── marketplace/           # 🌐 Next.js (React) Registry
│   ├── app/page.tsx       # Live directory UI (Registration + List)
│   ├── api/agents/        # Registry API endpoints
│   └── data/agents.json   # Flat-file database of registered agents
│
├── documentation/         # 📚 Project Docs
│   ├── ARCHITECTURE.md    # High-level system design
│   ├── SETUP_GUIDE.md     # How to run locally
│   └── CONTRIBUTING.md    # Dev guidelines
│
└── mobile_app/            # 📱 Legacy/Broken Code (To be replaced by PWA)
```

## Remaining Tasks & Missing Features

following items are incomplete or require changes for the final presentation.

### 1. Buyer Agent "Wrap Up" (Chatbot UI)
- **Current State**: The Buyer Agent is currently a **terminal-based API** (`POST /chat`). There is no visual interface for the end-user.
- **Requirement**: "Show project like a chatbot... just like ChatGPT or Gemini app."
- **Action Item**:
    - [ ] **Develop a Web-based Chat Interface (PWA)**: Create a clean, modern chat UI (HTML/JS or React) that connects to `http://localhost:8000/chat`.
    - [ ] **PWA Features**: Add `manifest.json` and service workers to make it installable on mobile devices, replacing the broken Flutter app.
    - [ ] **Conversation History**: UI should display the "Thinking..." steps (ReAct loop logs) to show the "AI Magic" to the judges.

### 2. Seller Agent Inventory (Google Sheets Integration)
- **Current State**: Inventory is hardcoded in local JSON files (`inventory/pharmacy_a.json`).
- **Requirement**: "Seller agent uses json... we will need google sheets." This allows non-technical shop owners to manage stock easily.
- **Action Item**:
    - [ ] **Google Sheets Connect**: Implement a function in `seller_agent` to fetch inventory from a live Google Sheet.
    - [ ] **Apps Script (Optional/Alternative)**: Script to push JSON from Sheets to the Agent, OR Agent pulls from published CSV/JSON URL of the Sheet.

### 3. Mobile App Fix
- **Current State**: The `mobile_app` folder contains code that is reported as "not working".
- **Action Item**: **Abandon native mobile app** in favor of the **Buyer Agent Web Client (PWA)** mentioned above. This ensures cross-platform compatibility and faster development for the presentation.

### 4. Final Presentation Polish
- [ ] **Run Script**: A single script to launch all 3 terminals (Marketplace, Seller 1, Seller 2, Buyer Agent) for smooth demo.
- [ ] **Seed Data**: Ensure Google Sheets (or JSONs) are populated with realistic "Demo Day" data (e.g., specific medicines, prices matching the script).

---

## Technical Implementation Details for "Wrap Up"

### A. Implementing the Buyer Chatbot (PWA)
We will build a **Single Page Application (SPA)** served by the Buyer Agent (or standalone) that acts as the chat interface.

**Tech Stack**: HTML5, Vanilla JS (for simplicity) or React, TailwindCSS.

**Features**:
1.  **Chat Bubble UI**: User messages right, AI messages left.
2.  **"Thought Process" Accordion**: When the agent calls `search_marketplace` or `contact_seller`, show these as collapsible logs so judges see the *Agentic Behavior*.
3.  **Markdown Rendering**: Render the AI's final response (tables, lists) nicely.

### B. Implementing Google Sheets Inventory
The Seller Agent needs to replace `json.load()` with a remote fetch.

**Approach**:
1.  **Public Approach (Easiest)**: Publish Google Sheet to Web as CSV.
2.  **Python Implementation**:
    ```python
    import pandas as pd
    
    def load_inventory_from_sheet(sheet_id):
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(url)
        # Convert to existing JSON structure
        return {"products": df.to_dict(orient='records'), "store_name": "Synced Store"}
    ```
3.  This allows the store owner to update price on their phone (Google Sheets App) and the Agent updates instantly.
