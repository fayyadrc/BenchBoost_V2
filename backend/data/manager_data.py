import requests
import json

class FPLDataFetcher:
    def __init__(self, manager_id=None, league_id=None, element_id=None, event_id=None, cookie=None):
        """
        Initialize the fetcher with necessary IDs and Authentication.
        
        :param manager_id: ID of the manager (team) to fetch.
        :param league_id: ID of the league to fetch.
        :param element_id: ID of a specific player (footballer).
        :param event_id: Gameweek number.
        :param cookie: Authentication cookie string (required for 'me', 'my-team', 'transfers-latest').
        """
        self.base_url = "https://fantasy.premierleague.com/api/"
        self.manager_id = manager_id
        self.league_id = league_id
        self.element_id = element_id
        self.event_id = event_id
        
        # Session setup
        self.session = requests.Session()
        # User-Agent is often required to mimic a browser and avoid 403 errors
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
        if cookie:
            self.session.headers.update({"Cookie": cookie})

    def _get(self, endpoint, params=None):
        """Helper method to perform GET requests."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return {}

    # --- GENERAL & FIXTURES ---

    def get_general_info(self):
        """1. General Information (Teams, Players, Settings)."""
        return self._get("bootstrap-static/")

    def get_all_fixtures(self):
        """2. All Fixtures for the season."""
        return self._get("fixtures/")

    def get_gameweek_fixtures(self):
        """3. Fixtures for a specific Gameweek."""
        if not self.event_id: return {}
        return self._get(f"fixtures/?event={self.event_id}")

    def get_event_status(self):
        """14. Status of the current Gameweek."""
        return self._get("event-status/")

    # --- PLAYER & GAMEWEEK DATA ---

    def get_player_detail(self):
        """4. Detailed data on a specific player."""
        if not self.element_id: return {}
        return self._get(f"element-summary/{self.element_id}/")

    def get_gameweek_live_stats(self):
        """5. Live stats for all players in a Gameweek."""
        if not self.event_id: return {}
        return self._get(f"event/{self.event_id}/live/")

    def get_dream_team(self):
        """15. Dream Team for a specific Gameweek."""
        if not self.event_id: return {}
        return self._get(f"dream-team/{self.event_id}/")

    # --- MANAGER DATA ---

    def get_manager_summary(self):
        """6. Basic summary of a Manager."""
        if not self.manager_id: return {}
        return self._get(f"entry/{self.manager_id}/")

    def get_manager_history(self):
        """7. History of a Manager (past seasons & current season stats)."""
        if not self.manager_id: return {}
        return self._get(f"entry/{self.manager_id}/history/")

    def get_manager_transfers(self):
        """8. All transfers made by a Manager."""
        if not self.manager_id: return {}
        return self._get(f"entry/{self.manager_id}/transfers/")

    def get_manager_picks(self):
        """13. Players picked by a Manager for a Gameweek."""
        if not self.manager_id or not self.event_id: return {}
        return self._get(f"entry/{self.manager_id}/event/{self.event_id}/picks/")

    # --- AUTHENTICATED MANAGER DATA (Requires Cookie) ---

    def get_manager_latest_transfers(self):
        """9. Transfers for the latest completed Gameweek."""
        if not self.manager_id: return {}
        return self._get(f"entry/{self.manager_id}/transfers-latest/")

    def get_my_team(self):
        """12. Current team info (chips, transfers) for Authenticated User."""
        if not self.manager_id: return {}
        return self._get(f"my-team/{self.manager_id}/")

    def get_my_personal_data(self):
        """17. Personal data for the Authenticated User."""
        return self._get("me/")

    # --- LEAGUES ---

    def get_classic_league_standings(self):
        """10. Standings for a Classic League."""
        if not self.league_id: return {}
        return self._get(f"leagues-classic/{self.league_id}/standings/")

    def get_h2h_league_standings(self):
        """11. Standings for a H2H League."""
        if not self.league_id: return {}
        return self._get(f"leagues-h2h-matches/league/{self.league_id}/")

    def get_league_cup_status(self):
        """18. Cup status for a League."""
        if not self.league_id: return {}
        return self._get(f"league/{self.league_id}/cup-status/")

    # --- MISCELLANEOUS ---

    def get_set_piece_notes(self):
        """16. Set piece takers notes."""
        return self._get("team/set-piece-notes/")

    def get_most_valuable_teams(self):
        """19. Top 5 most valuable teams."""
        return self._get("stats/most-valuable-teams/")

    def get_best_classic_leagues(self):
        """20. Best classic leagues by average score."""
        return self._get("stats/best-classic-leagues/")


# -----------------------------
# SHARED HELPER FUNCTIONS
# -----------------------------

def get_manager_squad_data(entry_id: int, event_id: int = None) -> dict:
    """
    Get a manager's full squad with enriched player details.
    
    This is a shared function used by both the API endpoint and agent tools
    to avoid code duplication.
    
    Args:
        entry_id: Manager's FPL entry ID
        event_id: Gameweek number (defaults to current GW if None)
    
    Returns:
        Dict with starting_xi, bench, and player details
    """
    from . import api_client, cache
    from .utils import get_player_full_name, get_position_name
    
    # Get current gameweek if not specified
    if event_id is None:
        current_gw = cache.get_current_gameweek()
        if not current_gw:
            return {"error": "Could not determine current gameweek"}
        event_id = current_gw.get("id")
    
    # Get the manager's picks for the gameweek
    picks_data = api_client.gameweek_picks(entry_id, event_id)
    
    if not picks_data or "picks" not in picks_data:
        return {"error": f"No team data found for manager {entry_id} in gameweek {event_id}"}
    
    picks = picks_data.get("picks", [])
    entry_history = picks_data.get("entry_history", {})
    active_chip = picks_data.get("active_chip")
    automatic_subs = picks_data.get("automatic_subs", [])
    
    # Get live data for the gameweek to get actual points
    live_data = api_client.event_live(event_id)
    live_elements = {e["id"]: e for e in live_data.get("elements", [])}
    
    # Enrich picks with player details from cache
    enriched_picks = []
    
    for pick in picks:
        element_id = pick.get("element")
        player = cache.get_player_by_id(element_id)
        live_player = live_elements.get(element_id, {})
        live_stats = live_player.get("stats", {})
        
        if player:
            team = cache.get_team_by_id(player.get("team"))
            
            # Get base points from live stats
            base_points = live_stats.get("total_points", 0)
            multiplier = pick.get("multiplier", 1)
            
            # For bench players (multiplier=0), show base_points
            # For starting XI, show actual points (with captain multiplier if applicable)
            if multiplier == 0:
                display_points = base_points
            else:
                display_points = base_points * multiplier
            
            enriched_picks.append({
                "element": element_id,
                "position": pick.get("position"),  # Squad position 1-15
                "is_captain": pick.get("is_captain", False),
                "is_vice_captain": pick.get("is_vice_captain", False),
                "multiplier": multiplier,
                "player_name": player.get("web_name", "Unknown"),
                "full_name": get_player_full_name(player),
                "team_name": team.get("name", "Unknown") if team else "Unknown",
                "team_short": team.get("short_name", "UNK") if team else "UNK",
                "element_type": player.get("element_type"),
                "position_name": get_position_name(player.get("element_type", 0)),
                "points": display_points,
                "base_points": base_points,
                "price": player.get("now_cost", 0) / 10,
                "form": player.get("form", "0"),
                "points_per_game": player.get("points_per_game", "0"),
                "total_points": player.get("total_points", 0),
                "selected_by_percent": player.get("selected_by_percent", "0"),
                "news": player.get("news", ""),
                "chance_of_playing": player.get("chance_of_playing_next_round"),
                "photo": player.get("photo", ""),
            })
        else:
            enriched_picks.append({
                "element": element_id,
                "position": pick.get("position"),
                "is_captain": pick.get("is_captain", False),
                "is_vice_captain": pick.get("is_vice_captain", False),
                "multiplier": pick.get("multiplier", 1),
                "player_name": "Unknown",
                "points": live_stats.get("total_points", 0) * pick.get("multiplier", 1),
            })
    
    # Separate starting XI (positions 1-11) and bench (positions 12-15)
    starting_xi = [p for p in enriched_picks if p.get("position", 0) <= 11]
    bench = [p for p in enriched_picks if p.get("position", 0) > 11]
    
    return {
        "entry_id": entry_id,
        "event": event_id,
        "active_chip": active_chip,
        "points": entry_history.get("points", 0),
        "total_points": entry_history.get("total_points", 0),
        "rank": entry_history.get("rank"),
        "overall_rank": entry_history.get("overall_rank"),
        "bank": entry_history.get("bank", 0) / 10,
        "value": entry_history.get("value", 0) / 10,
        "event_transfers": entry_history.get("event_transfers", 0),
        "event_transfers_cost": entry_history.get("event_transfers_cost", 0),
        "starting_xi": starting_xi,
        "bench": bench,
        "automatic_subs": automatic_subs,
        "current_captain": next((p["player_name"] for p in enriched_picks if p.get("is_captain")), None),
        "current_vice_captain": next((p["player_name"] for p in enriched_picks if p.get("is_vice_captain")), None),
    }


if __name__ == "__main__":
    # ---------------- CONFIGURATION ----------------
    # Replace these with real IDs to test specific endpoints
    MY_MANAGER_ID = 123456       # Your Manager ID
    TARGET_LEAGUE_ID = 314       # A League ID (e.g., the Overall league or a private league)
    TARGET_PLAYER_ID = 14        # A Player ID (e.g., Haaland, Salah - find in bootstrap-static)
    TARGET_GAMEWEEK = 1          # The Gameweek number you want data for
    
    # AUTHENTICATION (Optional - Leave empty if only fetching public data)
    # Copy from browser DevTools -> Network -> Request Headers -> 'cookie'
    MY_COOKIE = "" 
    # -----------------------------------------------

    print("Initializing FPL Fetcher...")
    fpl = FPLDataFetcher(
        manager_id=MY_MANAGER_ID,
        league_id=TARGET_LEAGUE_ID,
        element_id=TARGET_PLAYER_ID,
        event_id=TARGET_GAMEWEEK,
        cookie=MY_COOKIE
    )

    print("Fetching data into separate dictionaries...")

    # --- 1. General & Fixtures ---
    dict_general_info = fpl.get_general_info()
    dict_all_fixtures = fpl.get_all_fixtures()
    dict_gameweek_fixtures = fpl.get_gameweek_fixtures()
    dict_event_status = fpl.get_event_status()

    # --- 2. Player & Gameweek ---
    dict_player_detail = fpl.get_player_detail()
    dict_gameweek_live = fpl.get_gameweek_live_stats()
    dict_dream_team = fpl.get_dream_team()

    # --- 3. Manager Data (Public) ---
    dict_manager_summary = fpl.get_manager_summary()
    dict_manager_history = fpl.get_manager_history()
    dict_manager_transfers = fpl.get_manager_transfers()
    dict_manager_picks = fpl.get_manager_picks()

    # --- 4. Manager Data (Authenticated) ---
    # These will return empty dicts or errors if MY_COOKIE is not provided
    dict_manager_latest_transfers = fpl.get_manager_latest_transfers()
    dict_my_team = fpl.get_my_team()
    dict_my_personal_data = fpl.get_my_personal_data()

    # --- 5. Leagues ---
    dict_classic_league = fpl.get_classic_league_standings()
    dict_h2h_league = fpl.get_h2h_league_standings()
    dict_league_cup = fpl.get_league_cup_status()

    # --- 6. Misc ---
    dict_set_piece_notes = fpl.get_set_piece_notes()
    dict_most_valuable_teams = fpl.get_most_valuable_teams()
    dict_best_leagues = fpl.get_best_classic_leagues()

    # --- EXAMPLE OUTPUT ---
    print("\n--- Data Fetch Complete ---")
    
    # Example: Print the name of the player we fetched details for
    if 'first_name' in dict_player_detail:
        print(f"Player Fetched: {dict_player_detail.get('first_name')} {dict_player_detail.get('second_name')}")
    
    # Example: Print total players in the game from bootstrap-static
    if 'total_players' in dict_general_info:
        print(f"Total FPL Managers: {dict_general_info['total_players']}")

    # Example: Print fixture difficulty for the first fixture in the list
    if dict_all_fixtures:
        first_fixture = dict_all_fixtures[0]
        print(f"First Fixture Difficulty (Home/Away): {first_fixture.get('team_h_difficulty')}/{first_fixture.get('team_a_difficulty')}")