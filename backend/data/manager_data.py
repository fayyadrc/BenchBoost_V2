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