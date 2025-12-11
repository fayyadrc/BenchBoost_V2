"""
FPL Authentication module - handles official Fantasy Premier League login.
This provides authenticated access to private FPL API endpoints like:
- /api/my-team/{entry_id}/ - Current team with transfer info
- /api/me/ - Personal account data
- /api/entry/{entry_id}/transfers-latest/ - Latest transfers

Supports:
- Email/password login
- Google OAuth login (via browser-based flow)
"""
import requests
from typing import Dict, Any, Optional


def login_to_fpl(email: str, password: str) -> Dict[str, Any]:
    """
    Log in to FPL with email/password and return the authentication cookie string.
    
    Args:
        email: FPL account email
        password: FPL account password
        
    Returns:
        Dict with either:
        - {"cookie": "...", "cookie_dict": {...}} on success
        - {"error": "..."} on failure
    """
    session = requests.Session()
    login_url = "https://users.premierleague.com/accounts/login/"
    
    # Standard headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Referer": "https://fantasy.premierleague.com/",
        "Origin": "https://fantasy.premierleague.com",
    }
    session.headers.update(headers)
    
    payload = {
        "login": email,
        "password": password,
        "app": "plfpl-web",
        "redirect_uri": "https://fantasy.premierleague.com/"
    }
    
    try:
        response = session.post(login_url, data=payload)
        response.raise_for_status()
        
        # Check if login was successful - the key cookie is 'pl_profile'
        if 'pl_profile' not in session.cookies:
            # Try to extract error message from response
            return {"error": "Login failed. Please check your email and password."}
        
        # Convert cookie jar to the string format FPL expects
        cookie_dict = session.cookies.get_dict()
        cookie_string = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        
        return {
            "cookie": cookie_string,
            "cookie_dict": cookie_dict,
        }
        
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error during login: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error during login: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error during login: {str(e)}"}


def login_to_fpl_google(headless: bool = False, timeout: int = 120000) -> Dict[str, Any]:
    """
    Log in to FPL via Google OAuth using a browser window.
    Opens a browser for the user to complete Google sign-in, then captures cookies.
    
    Args:
        headless: If False (default), shows browser for user interaction
        timeout: Max time to wait for login completion in ms (default: 2 minutes)
        
    Returns:
        Dict with either:
        - {"cookie": "...", "cookie_dict": {...}} on success
        - {"error": "..."} on failure
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        return {"error": "Playwright not installed. Run: pip install playwright && playwright install chromium"}
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()
            
            # Go to FPL login page
            page.goto("https://users.premierleague.com/accounts/login/")
            
            # Click the "Log in with Google" button
            google_button = page.locator("button:has-text('Google'), a:has-text('Google'), [data-provider='google']").first
            if google_button.count() == 0:
                # Try alternative selector
                google_button = page.get_by_role("button", name="Google").or_(
                    page.get_by_role("link", name="Google")
                ).first
            
            if google_button.count() > 0:
                google_button.click()
            else:
                # User will need to manually click Google login
                pass
            
            # Wait for the user to complete Google sign-in and redirect back
            # The success indicator is reaching fantasy.premierleague.com with pl_profile cookie
            try:
                page.wait_for_url("**/fantasy.premierleague.com/**", timeout=timeout)
            except PlaywrightTimeout:
                browser.close()
                return {"error": "Login timed out. Please try again."}
            
            # Also wait a moment for cookies to be fully set
            page.wait_for_timeout(2000)
            
            # Extract cookies
            cookies = context.cookies()
            cookie_dict = {}
            for cookie in cookies:
                if "premierleague.com" in cookie.get("domain", ""):
                    cookie_dict[cookie["name"]] = cookie["value"]
            
            browser.close()
            
            if "pl_profile" not in cookie_dict:
                return {"error": "Login appeared to succeed but authentication cookie not found."}
            
            cookie_string = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
            
            return {
                "cookie": cookie_string,
                "cookie_dict": cookie_dict,
            }
            
        except Exception as e:
            return {"error": f"Google login failed: {str(e)}"}


def validate_cookie_from_string(cookie_string: str) -> Dict[str, Any]:
    """
    Validate a cookie string provided directly by the user.
    Useful when users extract cookies manually from their browser.
    
    Args:
        cookie_string: Cookie string (e.g., "pl_profile=xxx; other=yyy")
        
    Returns:
        Dict with validation result and user info if valid
    """
    if not cookie_string or "pl_profile" not in cookie_string:
        return {"valid": False, "error": "Cookie string must contain 'pl_profile'"}
    
    result = get_me_authenticated(cookie_string)
    
    if "error" in result:
        return {"valid": False, "error": result["error"]}
    
    player_data = result.get("player", {})
    return {
        "valid": True,
        "entry_id": player_data.get("entry"),
        "player_name": f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip(),
        "team_name": player_data.get("entry_name", ""),
    }


def get_authenticated_session(cookie_string: str) -> requests.Session:
    """
    Create a requests session with FPL authentication cookies.
    
    Args:
        cookie_string: Cookie string from login_to_fpl()
        
    Returns:
        Configured requests.Session with auth cookies
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Referer": "https://fantasy.premierleague.com/",
    })
    
    # Parse cookie string and set cookies
    for cookie in cookie_string.split("; "):
        if "=" in cookie:
            key, value = cookie.split("=", 1)
            session.cookies.set(key, value, domain=".premierleague.com")
    
    return session


def get_my_team_authenticated(entry_id: int, cookie_string: str) -> Dict[str, Any]:
    """
    Get the authenticated user's current team data.
    This endpoint provides more data than the public endpoint, including:
    - Current transfers made this GW
    - Available chips
    - Transfer cost
    
    Args:
        entry_id: FPL manager entry ID
        cookie_string: Authentication cookie string
        
    Returns:
        Dict with team data or error
    """
    session = get_authenticated_session(cookie_string)
    url = f"https://fantasy.premierleague.com/api/my-team/{entry_id}/"
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return {"error": "Authentication expired. Please log in again."}
        return {"error": f"HTTP error: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch team: {str(e)}"}


def get_me_authenticated(cookie_string: str) -> Dict[str, Any]:
    """
    Get the authenticated user's personal FPL data.
    Returns the user's entry_id, name, and other account info.
    
    Args:
        cookie_string: Authentication cookie string
        
    Returns:
        Dict with user data or error
    """
    session = get_authenticated_session(cookie_string)
    url = "https://fantasy.premierleague.com/api/me/"
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return {"error": "Authentication expired. Please log in again."}
        return {"error": f"HTTP error: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch user data: {str(e)}"}


def validate_cookie(cookie_string: str) -> bool:
    """
    Check if a cookie string is still valid for FPL authentication.
    
    Args:
        cookie_string: Authentication cookie string to validate
        
    Returns:
        True if cookie is valid, False otherwise
    """
    result = get_me_authenticated(cookie_string)
    return "error" not in result
