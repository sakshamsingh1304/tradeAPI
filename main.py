from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import logging

from core.security import get_api_key
from core.session import record_request, get_all_sessions
from services.search_service import get_sector_news
from services.llm_service import analyze_market_data

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate Limiter – 5 requests per minute per client IP (in-memory)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Trade Opportunities API",
    description=(
        "Analyzes market data and provides trade opportunity insights "
        "for specific sectors in India. Powered by DuckDuckGo search "
        "and the Groq LLM API."
    ),
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def read_root():
    """Health-check / welcome endpoint."""
    return {
        "message": "Trade Opportunities API is running.",
        "docs": "/docs",
        "usage": "GET /analyze/{sector}",
    }


@app.get("/analyze/{sector}", response_class=PlainTextResponse, tags=["Analysis"])
@limiter.limit("5/minute")
async def analyze_sector(
    request: Request,
    sector: str,
    api_key: str = Depends(get_api_key),
):
    """
    Accepts a sector name (e.g. *pharmaceuticals*, *technology*, *agriculture*)
    and returns a structured **Markdown** market-analysis report with current
    trade opportunities in India.

    **Headers required:** `X-API-Key`

    **Rate limit:** 5 requests / minute per IP.
    """
    # --- Input validation ---------------------------------------------------
    sector_clean = sector.strip()
    if not sector_clean:
        raise HTTPException(status_code=400, detail="Sector parameter cannot be empty.")
    if len(sector_clean) > 100:
        raise HTTPException(status_code=400, detail="Sector name is too long (max 100 chars).")
    sector_clean = sector_clean.title()

    # --- Session tracking ----------------------------------------------------
    client_ip = get_remote_address(request)
    session = record_request(client_ip, sector_clean)
    logger.info(
        f"Session {session['session_id']} | Analyzing sector: {sector_clean} "
        f"(total requests: {session['request_count']})"
    )

    # --- Step 1: Collect data via web search ---------------------------------
    search_context = await get_sector_news(sector_clean)

    # --- Step 2: Analyze with LLM -------------------------------------------
    markdown_report = await analyze_market_data(sector_clean, search_context)

    return markdown_report


@app.get("/sessions", tags=["Admin"])
async def list_sessions(api_key: str = Depends(get_api_key)):
    """
    Returns all active in-memory sessions.
    Useful for debugging and monitoring API usage.
    """
    return {"sessions": get_all_sessions()}


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
