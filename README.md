# Trade Opportunities API

A FastAPI service that analyzes market data and provides trade opportunity insights for specific sectors in India. It searches for the latest news using DuckDuckGo and synthesizes a structured Markdown report using the Groq API (`llama-3.3-70b-versatile`).

## Features

| Feature | Implementation |
|---|---|
| **Framework** | FastAPI with async request handling |
| **Data Collection** | DuckDuckGo Search (`DDGS().news()` + `.text()` fallback) |
| **AI Analysis** | Groq API – `llama-3.3-70b-versatile` |
| **Authentication** | API Key validation via `X-API-Key` header |
| **Rate Limiting** | 5 requests/minute per IP using `slowapi` |
| **Session Tracking** | In-memory session store (no database) |
| **Storage** | Fully in-memory – no external database required |
| **Logging** | Python `logging` module across all layers |

## Project Structure

```
├── main.py                  # FastAPI app, routes, rate limiter setup
├── core/
│   ├── __init__.py
│   ├── security.py          # API Key authentication dependency
│   └── session.py           # In-memory session management
├── services/
│   ├── __init__.py
│   ├── search_service.py    # DuckDuckGo web search data collection
│   └── llm_service.py       # Groq LLM analysis integration
├── requirements.txt
├── .env.example             # Template for environment variables
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Clone & Install

```bash
cd Assigmnent
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root (you can copy `.env.example`):

```env
GROQ_API_KEY=your_groq_api_key_here
APP_API_KEY=12345
```

- **`GROQ_API_KEY`** – Get a free key at [console.groq.com](https://console.groq.com)
- **`APP_API_KEY`** – The API key clients must send in the `X-API-Key` header. Set to `12345`.

### 3. Run the Application

```bash
python main.py
```

The server starts at **http://localhost:8000**. Interactive API docs are at **http://localhost:8000/docs**.

---

## API Documentation

### `GET /` – Health Check

Returns a welcome message confirming the service is running.

**Example:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Trade Opportunities API is running.",
  "docs": "/docs",
  "usage": "GET /analyze/{sector}"
}
```

---

### `GET /analyze/{sector}` – Analyze Sector

Accepts a sector name and returns a structured Markdown market analysis report.

**Headers:**

| Header | Required | Description |
|---|---|---|
| `X-API-Key` | Yes | Your API key (set in `.env` as `APP_API_KEY`) |

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `sector` | string | Sector name, e.g. `pharmaceuticals`, `technology`, `agriculture` |

**Example Request:**
```bash
curl -X GET \
  'http://localhost:8000/analyze/pharmaceuticals' \
  -H 'X-API-Key: 12345'
```

**Example Response** (Markdown):
```markdown
# Market Analysis Report: Pharmaceuticals – India

## Executive Summary
The Indian pharmaceutical industry continues to show robust growth...

## Current Market Trends
- Generic drug exports have increased by 12%...
- Government initiatives like PLI scheme...

## Key Trade Opportunities in India
1. **API Manufacturing** – India supplies 20% of global generics...
2. **Biosimilars** – Emerging opportunity worth $12B...

## Challenges & Risks
- Regulatory compliance with US FDA...
- Raw material dependency on China...

## Future Outlook
The sector is expected to reach $130B by 2030...
```

**Error Responses:**

| Status | Reason |
|---|---|
| `400` | Empty or invalid sector name |
| `401` | Missing or invalid `X-API-Key` header |
| `429` | Rate limit exceeded (max 5 requests/minute) |

---

### `GET /sessions` – List Active Sessions (Admin)

Returns all tracked in-memory sessions for monitoring.

**Headers:** `X-API-Key` required.

**Example:**
```bash
curl http://localhost:8000/sessions -H 'X-API-Key: 12345'
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "a1b2c3d4-...",
      "client_ip": "127.0.0.1",
      "created_at": 1713382450.123,
      "last_active": 1713382460.456,
      "request_count": 3,
      "sectors_queried": ["Pharmaceuticals", "Technology"]
    }
  ]
}
```

---

## Security Measures

- **Authentication**: Every request to `/analyze` and `/sessions` requires a valid `X-API-Key` header. Missing or incorrect keys return `401 Unauthorized`.
- **Rate Limiting**: Enforced at 5 requests per minute per client IP to prevent abuse. Exceeding returns `429 Too Many Requests`.
- **Input Validation**: Sector names are trimmed, length-capped (100 chars), and validated before processing.
- **No Secrets in Code**: All sensitive values loaded from environment variables via `python-dotenv`.

## Architecture

```
Client Request
      │
      ▼
┌─────────────┐
│  main.py    │  ← Rate limiter + Auth check
│  (FastAPI)  │
└──────┬──────┘
       │
  ┌────┴─────┐
  ▼          ▼
┌──────┐  ┌──────┐
│Search│  │ LLM  │
│Svc   │  │ Svc  │
└──┬───┘  └──┬───┘
   │         │
   ▼         ▼
DuckDuckGo  Groq API
```
