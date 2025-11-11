"""FPL API client - handles all HTTP requests to the Fantasy Premier League API"""

from typing import Any, Dict, Optional
import requests


BASE_URL = "https://fantasy.premierleague.com/api"
DEFAULT_TIMEOUT = 10.0


def _get(
    path: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    cookies: Optional[Dict[str, Any]] = None,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Internal helper to GET and return JSON with basic error handling.

    Args:
        path: API path relative to BASE_URL (no leading slash required).
        params: Optional query parameters.
        cookies: Optional cookies for private endpoints.
        session: Optional requests.Session to reuse connections.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as a dict.

    Raises:
        requests.HTTPError: if the response status is not successful.
    """
    url = f"{BASE_URL}/{path.lstrip('/')}/"
    req = session or requests
    resp = req.get(url, params=params, cookies=cookies, timeout=timeout)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        # Attach response content for easier debugging
        raise requests.HTTPError(
            f"GET {url} failed: {resp.status_code} - {resp.text}"
        )
    return resp.json()


def bootstrap_static(
    session: Optional[requests.Session] = None, timeout: float = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """Get bootstrap-static data (events, elements, teams, settings, etc.)."""
    return _get("bootstrap-static", session=session, timeout=timeout)


def event_live(
    event_id: int,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get live event data for a specific gameweek (event_id)."""
    return _get(f"event/{int(event_id)}/live", session=session, timeout=timeout)


def my_team(
    entry_id: int,
    cookies: Optional[Dict[str, Any]] = None,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get the authenticated manager's team selection for the current GW.

    Note: This endpoint requires authentication cookies (pass `cookies`).
    """
    return _get(
        f"my-team/{int(entry_id)}", cookies=cookies, session=session, timeout=timeout
    )


def entry_details(
    cookies: Optional[Dict[str, Any]] = None,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get details about the authenticated entry (me).

    Requires authentication cookie.
    """
    return _get("me", cookies=cookies, session=session, timeout=timeout)


def entry_summary(
    entry_id: int,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get an entry's season summary."""
    return _get(f"entry/{int(entry_id)}", session=session, timeout=timeout)


def entry_history(
    entry_id: int,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get an entry's historical season and GW statistics."""
    return _get(f"entry/{int(entry_id)}/history", session=session, timeout=timeout)


def transfers_history(
    entry_id: int,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get transfer transactions for an entry."""
    return _get(f"entry/{int(entry_id)}/transfers", session=session, timeout=timeout)


def gameweek_picks(
    entry_id: int,
    event_id: int,
    cookies: Optional[Dict[str, Any]] = None,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get a manager's picks for a specified gameweek (requires auth cookie)."""
    return _get(
        f"entry/{int(entry_id)}/event/{int(event_id)}/picks",
        cookies=cookies,
        session=session,
        timeout=timeout,
    )


def fixtures(
    event: Optional[int] = None,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get fixtures. Optionally filter by event (gameweek)."""
    params = {"event": int(event)} if event is not None else None
    return _get("fixtures", params=params, session=session, timeout=timeout)


def element_summary(
    element_id: int,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get a player's (element) summary and history."""
    return _get(f"element-summary/{int(element_id)}", session=session, timeout=timeout)


def league_standings(
    league_id: int,
    page_standings: int = 1,
    phase: Optional[int] = None,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Get classic league standings with optional pagination and phase.

    Args:
        league_id: League id (e.g. 314 for Overall).
        page_standings: Page number for pagination (50 entries per page).
        phase: Optional phase filter.
    """
    params: Dict[str, Any] = {"page_standings": int(page_standings)}
    if phase is not None:
        params["phase"] = int(phase)
    return _get(
        f"leagues-classic/{int(league_id)}/standings",
        params=params,
        session=session,
        timeout=timeout,
    )


def fetch_public_data(
    entry_id: Optional[int] = None,
    event_id: Optional[int] = None,
    element_id: Optional[int] = None,
    league_id: Optional[int] = None,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
    persist: bool = True,
) -> Dict[str, Any]:
    """
    Fetch a useful set of public FPL endpoints and return as a dict.

    This function does NOT run automatically on import. Call it from another
    script (for example an AI layer) to fetch and receive a single dictionary
    containing the requested pieces of data. If `persist` is True the result
    will also be stored in the module-level `latest_data` variable.

    Inputs (all optional except as noted):
      - entry_id: manager entry id (calls `entry_summary` if provided)
      - event_id: gameweek id (calls `event_live` and `fixtures` for that event)
      - element_id: player id (calls `element_summary` if provided)
      - league_id: league id (calls `league_standings` if provided)

    Returns:
      Dict with keys for each fetched endpoint (always includes `bootstrap_static`).
    """
    from .cache import latest_data

    result: Dict[str, Any] = {}

    result["bootstrap_static"] = bootstrap_static(session=session, timeout=timeout)

    if entry_id is not None:
        result["entry_summary"] = entry_summary(
            entry_id, session=session, timeout=timeout
        )

    if event_id is not None:
        result["event_live"] = event_live(event_id, session=session, timeout=timeout)
        result["fixtures_event"] = fixtures(
            event=event_id, session=session, timeout=timeout
        )
    else:
        result["fixtures_all"] = fixtures(session=session, timeout=timeout)

    if element_id is not None:
        result["element_summary"] = element_summary(
            element_id, session=session, timeout=timeout
        )

    if league_id is not None:
        result["league_standings"] = league_standings(
            league_id, session=session, timeout=timeout
        )

    if persist:
        latest_data.clear()
        latest_data.update(result)

    return result
