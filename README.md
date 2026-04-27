# BenchBoost

> An AI-powered Fantasy Premier League assistant that gives you real-time insights, squad analysis, and personalised transfer advice — all through a conversational interface.

---

## Overview

BenchBoost is a full-stack RAG (Retrieval-Augmented Generation) chatbot designed specifically for FPL managers. Instead of manually digging through stats sites, you simply ask questions in plain English and get intelligent, data-driven answers about players, gameweeks, your squad, and the broader FPL landscape.

**Example queries:**
- *"How many points does Salah have this gameweek?"*
- *"Should I take a hit to bring in Haaland?"*
- *"What are the latest injury updates for my squad?"*
- *"Who are the best differential picks for the next two gameweeks?"*

---

## Features

- **Conversational AI** — Powered by Google Gemini 2.5 Flash via LangChain, enabling natural multi-turn dialogue
- **Live FPL Data** — Pulls real-time player stats, gameweek live points, and fixture data directly from the official FPL API and LiveFPL
- **Squad-Aware** — Enter your FPL Manager ID and the assistant analyses your personal team, transfers, and captain choices
- **Knowledge Base (RAG)** — MongoDB Atlas Vector Search lets the assistant answer qualitative questions about FPL rules, news, and strategy
- **Persistent Chat History** — Sessions are stored in MongoDB so your conversation context is never lost
- **Modern Frontend** — Responsive React 19 SPA with dark/light theme support and session management

---


### Data Flow

```
User Query
    │
    ▼
React Frontend  ──────────────────────────────────────────────────────►  Display Response
    │                                                                           ▲
    │  POST /api/query (+ manager_id)                                           │
    ▼                                                                           │
FastAPI (middleware/api.py)                                                     │
    │  • Fetches chat history from MongoDB                                      │
    │  • Prepends Manager ID to query context                                   │
    ▼                                                                           │
LangChain AgentExecutor (agent/agent.py)                                        │
    │  • Gemini 2.5 Flash reasons over tools                                    │
    ▼                                                                           │
Tools (agent/tools.py)                                                          │
    │  • In-memory cache           • MongoDB Vector Store (RAG)                 │
    │  • Official FPL API          • LiveFPL API                                │
    ▼                                                                           │
Synthesised Response  ──────────────────────────────────────────────────────────┘
    (saved to MongoDB)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (with Vector Search enabled)
- Google AI API key (Gemini)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/fayyadrc/benchboost-v2.git
cd benchboost-v2/backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Fill in your GOOGLE_API_KEY, MONGODB_URI, and other secrets

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`.

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key from Google AI Studio |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DB_NAME` | Name of the database to use |
| `FPL_API_BASE_URL` | Base URL for the FPL API (default: `https://fantasy.premierleague.com/api`) |

---

## 🤖 How the Agent Works

1. **Session Retrieval** — On each request, the backend fetches the existing chat history from MongoDB to maintain conversational context.
2. **Context Injection** — If a Manager ID is provided, it is silently prepended to the query (`[User's FPL Team ID: XXXXX]`), allowing the LLM to pass it to manager-specific tools automatically.
3. **Tool Selection** — The LangChain agent inspects the user's intent and dispatches to the most relevant tool(s) from `tools.py` (e.g., `get_player_stats`, `get_manager_squad`, `search_knowledge_base`).
4. **Data Hydration** — Squad data is enriched with live gameweek stats, including captain point multipliers.
5. **Synthesis** — Gemini processes all tool outputs and generates a natural language response, which is persisted to MongoDB.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS 4 |
| **Backend** | FastAPI, Python 3.11 |
| **AI / LLM** | Google Gemini 2.5 Flash, LangChain |
| **Database** | MongoDB Atlas (chat history + vector store) |
| **Data Sources** | Official FPL API, LiveFPL |

---

## Known Issues & Limitations

- **Manager Points Calculation** — Transfer hit costs are not yet subtracted from displayed gameweek points. Vice-captain logic is not fully implemented when the captain records 0 minutes.
- **Synchronous Tools** — Underlying API calls use `requests` (synchronous), which limits concurrent throughput. Planned migration to `httpx` with async tools.
- **In-Memory Agent Cache** — Agent instances are cached per session in memory. Long-running deployments with many unique sessions may see increased memory usage over time.

---

## Next Steps

- [ ] Fix GW points calculation (subtract transfer hit costs)
- [ ] Implement full vice-captain fallback logic
- [ ] Migrate API clients from `requests` to `httpx` for async support
- [ ] Add rate limiting middleware
- [ ] Migrate to `@tanstack/react-query` for frontend data fetching
- [ ] Consolidate `api_client.py` and `manager_data.py` into a unified FPL service layer

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
