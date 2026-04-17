"""
In-memory session management for tracking API usage per client.
No database is used; all state is lost on server restart.
"""
import time
import uuid
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# In-memory session store: maps session_id -> session data
_sessions: dict[str, dict] = {}

# Maps IP address -> session_id for automatic session association
_ip_session_map: dict[str, str] = {}


def get_or_create_session(client_ip: str) -> dict:
    """
    Retrieves or creates a session for the given client IP.
    Each session tracks:
      - session_id: unique identifier
      - created_at: timestamp of first request
      - last_active: timestamp of most recent request
      - request_count: total number of analyze requests made
      - sectors_queried: list of sectors queried in this session
    """
    if client_ip in _ip_session_map:
        session_id = _ip_session_map[client_ip]
        session = _sessions[session_id]
        session["last_active"] = time.time()
        return session

    # Create a new session
    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "client_ip": client_ip,
        "created_at": time.time(),
        "last_active": time.time(),
        "request_count": 0,
        "sectors_queried": [],
    }
    _sessions[session_id] = session
    _ip_session_map[client_ip] = session_id
    logger.info(f"New session created: {session_id} for IP: {client_ip}")
    return session


def record_request(client_ip: str, sector: str) -> dict:
    """Records an analysis request against the client's session."""
    session = get_or_create_session(client_ip)
    session["request_count"] += 1
    session["last_active"] = time.time()
    if sector not in session["sectors_queried"]:
        session["sectors_queried"].append(sector)
    logger.info(
        f"Session {session['session_id']}: request #{session['request_count']} for sector '{sector}'"
    )
    return session


def get_all_sessions() -> list[dict]:
    """Returns all active sessions (for admin/debug purposes)."""
    return list(_sessions.values())
