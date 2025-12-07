"""
Standardized Data Models for FPL Data

Provides consistent data structures across all tools and methods.
All tools should return data using these models for LLM consistency.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class Position(Enum):
    """Player position types."""
    GKP = 1
    DEF = 2
    MID = 3
    FWD = 4
    
    @classmethod
    def from_id(cls, element_type: int) -> "Position":
        """Convert element_type ID to Position enum."""
        for pos in cls:
            if pos.value == element_type:
                return pos
        return cls.FWD  # Default
    
    @classmethod
    def from_name(cls, name: str) -> Optional["Position"]:
        """Convert position name to Position enum."""
        name_map = {
            "GKP": cls.GKP, "GK": cls.GKP, "GOALKEEPER": cls.GKP,
            "DEF": cls.DEF, "DEFENDER": cls.DEF,
            "MID": cls.MID, "MIDFIELDER": cls.MID,
            "FWD": cls.FWD, "FORWARD": cls.FWD, "STR": cls.FWD, "STRIKER": cls.FWD
        }
        return name_map.get(name.upper())


class AvailabilityStatus(Enum):
    """Player availability status codes from FPL API."""
    AVAILABLE = "a"           # Available
    DOUBTFUL = "d"            # Doubtful (25-75% chance)
    INJURED = "i"             # Injured (low chance)
    SUSPENDED = "s"           # Suspended
    NOT_AVAILABLE = "n"       # Not available
    UNAVAILABLE = "u"         # Transferred out of league
    
    @classmethod
    def from_code(cls, code: str) -> "AvailabilityStatus":
        """Convert status code to enum."""
        for status in cls:
            if status.value == code.lower():
                return status
        return cls.AVAILABLE


class ChipType(Enum):
    """FPL chip types."""
    WILDCARD = "wildcard"
    FREE_HIT = "freehit"
    BENCH_BOOST = "bboost"
    TRIPLE_CAPTAIN = "3xc"


class FixtureDifficulty(Enum):
    """Fixture difficulty ratings."""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5
    
    @property
    def display_name(self) -> str:
        return self.name.replace("_", " ").title()


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class DataMeta:
    """Metadata for data freshness and source tracking."""
    fetched_at: datetime = field(default_factory=datetime.now)
    source: str = "fpl_api"
    cache_ttl_seconds: Optional[int] = None
    is_cached: bool = False
    
    @property
    def age_seconds(self) -> float:
        """Get age of data in seconds."""
        return (datetime.now() - self.fetched_at).total_seconds()
    
    @property
    def is_stale(self) -> bool:
        """Check if data has exceeded TTL."""
        if self.cache_ttl_seconds is None:
            return False
        return self.age_seconds > self.cache_ttl_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fetched_at": self.fetched_at.isoformat(),
            "source": self.source,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "is_cached": self.is_cached,
            "age_seconds": round(self.age_seconds, 1),
            "is_stale": self.is_stale
        }


@dataclass
class ExpectedStats:
    """Expected statistics (xG, xA) for underlying performance analysis."""
    expected_goals: float = 0.0
    expected_assists: float = 0.0
    expected_goal_involvements: float = 0.0
    expected_goals_conceded: float = 0.0
    
    # Performance vs expected
    goals_vs_xg: float = 0.0          # Actual goals - xG (positive = overperforming)
    assists_vs_xa: float = 0.0        # Actual assists - xA
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DerivedStats:
    """Calculated statistics for value analysis."""
    points_per_90: float = 0.0
    points_per_million: float = 0.0
    points_per_game_per_million: float = 0.0
    points_per_million_per_90: float = 0.0
    bonus_per_90: float = 0.0
    goals_per_90: float = 0.0
    assists_per_90: float = 0.0
    appearances_90: float = 0.0       # 90-minute equivalents played
    minutes_percent: float = 0.0      # % of available minutes played
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TransferInfo:
    """Transfer trend information for a player."""
    transfers_in_event: int = 0       # Transfers in this GW
    transfers_out_event: int = 0      # Transfers out this GW
    net_transfers: int = 0            # Net transfers this GW
    transfers_in_total: int = 0       # Total season transfers in
    transfers_out_total: int = 0      # Total season transfers out
    price_change_event: float = 0.0   # Price change this GW (in millions)
    price_change_start: float = 0.0   # Price change since season start
    
    @property
    def transfer_trend(self) -> str:
        """Get transfer trend indicator."""
        if self.net_transfers > 50000:
            return "🔥 Very Hot"
        elif self.net_transfers > 20000:
            return "📈 Rising"
        elif self.net_transfers < -50000:
            return "📉 Falling Fast"
        elif self.net_transfers < -20000:
            return "⬇️ Dropping"
        else:
            return "➡️ Stable"
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["transfer_trend"] = self.transfer_trend
        return result


@dataclass
class UpcomingFixture:
    """Simplified fixture information for player/team context."""
    gameweek: int
    opponent: str                     # Short name (e.g., "ARS")
    opponent_full: str                # Full name (e.g., "Arsenal")
    is_home: bool
    difficulty: int                   # 1-5 scale
    kickoff_time: Optional[str] = None
    
    @property
    def difficulty_text(self) -> str:
        """Get human-readable difficulty."""
        try:
            return FixtureDifficulty(self.difficulty).display_name
        except ValueError:
            return "Unknown"
    
    @property
    def venue(self) -> str:
        return "H" if self.is_home else "A"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gameweek": self.gameweek,
            "opponent": self.opponent,
            "opponent_full": self.opponent_full,
            "is_home": self.is_home,
            "venue": self.venue,
            "difficulty": self.difficulty,
            "difficulty_text": self.difficulty_text,
            "kickoff_time": self.kickoff_time
        }


@dataclass
class PlayerData:
    """
    Standardized player data model.
    
    All tools returning player information should use this model
    to ensure consistency for the LLM.
    """
    # Core identifiers
    id: int
    web_name: str
    full_name: str
    
    # Team & Position
    team_id: int
    team_name: str
    team_short: str
    position: str                     # "GKP", "DEF", "MID", "FWD"
    element_type: int                 # 1-4
    
    # Pricing
    price: float                      # Current price in millions
    price_change_event: float = 0.0   # Price change this GW
    price_change_start: float = 0.0   # Price change since season start
    
    # Core Stats
    total_points: int = 0
    points_per_game: float = 0.0
    form: float = 0.0
    minutes: int = 0
    
    # Scoring Stats
    goals_scored: int = 0
    assists: int = 0
    clean_sheets: int = 0
    goals_conceded: int = 0
    
    # Bonus & BPS
    bonus: int = 0
    bps: int = 0
    
    # ICT Index
    influence: float = 0.0
    creativity: float = 0.0
    threat: float = 0.0
    ict_index: float = 0.0
    
    # Ownership & Selection
    selected_by_percent: float = 0.0
    
    # Availability
    status: str = "a"                 # a=available, d=doubtful, i=injured, s=suspended, u=unavailable
    news: str = ""
    chance_of_playing_next: Optional[int] = None
    chance_of_playing_this: Optional[int] = None
    
    # Additional stats
    yellow_cards: int = 0
    red_cards: int = 0
    own_goals: int = 0
    penalties_saved: int = 0
    penalties_missed: int = 0
    saves: int = 0
    
    # Nested data (optional)
    expected_stats: Optional[ExpectedStats] = None
    derived_stats: Optional[DerivedStats] = None
    transfer_info: Optional[TransferInfo] = None
    upcoming_fixtures: List[UpcomingFixture] = field(default_factory=list)
    
    # Metadata
    meta: Optional[DataMeta] = None
    
    @property
    def availability_status(self) -> AvailabilityStatus:
        return AvailabilityStatus.from_code(self.status)
    
    @property
    def is_available(self) -> bool:
        return self.status == "a"
    
    @property
    def is_flagged(self) -> bool:
        """Check if player has any availability concerns."""
        return self.status != "a" or bool(self.news)
    
    @property
    def ownership_tier(self) -> str:
        """Categorize ownership level."""
        if self.selected_by_percent >= 40:
            return "template"      # Must-have
        elif self.selected_by_percent >= 20:
            return "popular"       # Common pick
        elif self.selected_by_percent >= 5:
            return "differential"  # Good differential
        else:
            return "punt"          # High-risk punt
    
    def to_dict(self, include_nested: bool = True) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "web_name": self.web_name,
            "full_name": self.full_name,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "team_short": self.team_short,
            "position": self.position,
            "element_type": self.element_type,
            "price": self.price,
            "price_change_event": self.price_change_event,
            "price_change_start": self.price_change_start,
            "total_points": self.total_points,
            "points_per_game": self.points_per_game,
            "form": self.form,
            "minutes": self.minutes,
            "goals_scored": self.goals_scored,
            "assists": self.assists,
            "clean_sheets": self.clean_sheets,
            "goals_conceded": self.goals_conceded,
            "bonus": self.bonus,
            "bps": self.bps,
            "influence": self.influence,
            "creativity": self.creativity,
            "threat": self.threat,
            "ict_index": self.ict_index,
            "selected_by_percent": self.selected_by_percent,
            "status": self.status,
            "news": self.news,
            "chance_of_playing_next": self.chance_of_playing_next,
            "chance_of_playing_this": self.chance_of_playing_this,
            "yellow_cards": self.yellow_cards,
            "red_cards": self.red_cards,
            "own_goals": self.own_goals,
            "penalties_saved": self.penalties_saved,
            "penalties_missed": self.penalties_missed,
            "saves": self.saves,
            # Computed properties
            "is_available": self.is_available,
            "is_flagged": self.is_flagged,
            "ownership_tier": self.ownership_tier,
        }
        
        if include_nested:
            if self.expected_stats:
                result["expected_stats"] = self.expected_stats.to_dict()
            if self.derived_stats:
                result["derived_stats"] = self.derived_stats.to_dict()
            if self.transfer_info:
                result["transfer_info"] = self.transfer_info.to_dict()
            if self.upcoming_fixtures:
                result["upcoming_fixtures"] = [f.to_dict() for f in self.upcoming_fixtures]
            if self.meta:
                result["_meta"] = self.meta.to_dict()
        
        return result
    
    def to_summary(self) -> str:
        """Generate concise text summary for LLM context."""
        lines = [
            f"{self.web_name} ({self.team_short}, {self.position}) - £{self.price:.1f}m",
            f"  Points: {self.total_points} | Form: {self.form} | Owned: {self.selected_by_percent}%"
        ]
        
        if self.goals_scored or self.assists:
            lines.append(f"  Goals: {self.goals_scored} | Assists: {self.assists}")
        
        if self.expected_stats:
            xg_diff = self.expected_stats.goals_vs_xg
            perf = "overperforming" if xg_diff > 0.5 else "underperforming" if xg_diff < -0.5 else "on track"
            lines.append(f"  xG: {self.expected_stats.expected_goals:.2f} ({perf})")
        
        if self.is_flagged:
            lines.append(f"  ⚠️ {self.news or 'Flagged'}")
        
        if self.upcoming_fixtures:
            fixtures_str = ", ".join(
                f"GW{f.gameweek}: {f.opponent}({f.venue})" 
                for f in self.upcoming_fixtures[:3]
            )
            lines.append(f"  Fixtures: {fixtures_str}")
        
        return "\n".join(lines)


@dataclass
class TeamData:
    """Standardized team data model."""
    id: int
    name: str
    short_name: str
    
    # Strength ratings
    strength: int = 0
    strength_overall_home: int = 0
    strength_overall_away: int = 0
    strength_attack_home: int = 0
    strength_attack_away: int = 0
    strength_defence_home: int = 0
    strength_defence_away: int = 0
    
    # League position
    position: Optional[int] = None
    
    # Stats
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    
    # Upcoming fixtures
    upcoming_fixtures: List[UpcomingFixture] = field(default_factory=list)
    
    # Metadata
    meta: Optional[DataMeta] = None
    
    @property
    def fixture_difficulty_rating(self) -> float:
        """Average difficulty of upcoming fixtures."""
        if not self.upcoming_fixtures:
            return 3.0  # Medium default
        return sum(f.difficulty for f in self.upcoming_fixtures) / len(self.upcoming_fixtures)
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["fixture_difficulty_rating"] = round(self.fixture_difficulty_rating, 2)
        if self.meta:
            result["_meta"] = self.meta.to_dict()
        if self.upcoming_fixtures:
            result["upcoming_fixtures"] = [f.to_dict() for f in self.upcoming_fixtures]
        return result


@dataclass
class GameweekData:
    """Standardized gameweek data model."""
    id: int
    name: str
    deadline_time: str
    
    # Status
    is_current: bool = False
    is_next: bool = False
    finished: bool = False
    data_checked: bool = False
    
    # Stats (available after GW finishes)
    average_score: Optional[int] = None
    highest_score: Optional[int] = None
    most_selected: Optional[int] = None      # Player ID
    most_transferred_in: Optional[int] = None
    most_captained: Optional[int] = None
    
    # Chip usage stats
    chip_plays: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    meta: Optional[DataMeta] = None
    
    @property
    def status(self) -> str:
        if self.finished:
            return "Finished"
        elif self.is_current:
            return "In Progress"
        else:
            return "Upcoming"
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["status"] = self.status
        if self.meta:
            result["_meta"] = self.meta.to_dict()
        return result


@dataclass
class Recommendation:
    """Standardized recommendation with confidence score."""
    recommendation: str               # The actual recommendation
    confidence: float                 # 0.0 to 1.0
    reasoning: List[str]              # List of reasons supporting the recommendation
    alternatives: List[str] = field(default_factory=list)  # Alternative options
    risks: List[str] = field(default_factory=list)         # Potential downsides
    
    # Metadata
    meta: Optional[DataMeta] = None
    
    @property
    def confidence_level(self) -> str:
        """Human-readable confidence level."""
        if self.confidence >= 0.8:
            return "High"
        elif self.confidence >= 0.6:
            return "Medium-High"
        elif self.confidence >= 0.4:
            return "Medium"
        elif self.confidence >= 0.2:
            return "Low-Medium"
        else:
            return "Low"
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["confidence_level"] = self.confidence_level
        if self.meta:
            result["_meta"] = self.meta.to_dict()
        return result
    
    def to_summary(self) -> str:
        """Generate text summary for LLM."""
        lines = [
            f"**{self.recommendation}** (Confidence: {self.confidence_level} - {self.confidence:.0%})",
            "",
            "Reasoning:"
        ]
        for reason in self.reasoning:
            lines.append(f"  • {reason}")
        
        if self.risks:
            lines.append("")
            lines.append("Risks:")
            for risk in self.risks:
                lines.append(f"  ⚠️ {risk}")
        
        if self.alternatives:
            lines.append("")
            lines.append(f"Alternatives: {', '.join(self.alternatives)}")
        
        return "\n".join(lines)


@dataclass
class ToolResponse:
    """
    Standardized wrapper for all tool responses.
    
    Ensures consistent structure with data, metadata, and error handling.
    """
    success: bool
    data: Any                         # The actual response data
    message: Optional[str] = None     # Human-readable message
    error: Optional[str] = None       # Error message if success=False
    meta: DataMeta = field(default_factory=DataMeta)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": self.success,
            "message": self.message,
            "_meta": self.meta.to_dict()
        }
        
        if self.success:
            # Serialize data appropriately
            if hasattr(self.data, "to_dict"):
                result["data"] = self.data.to_dict()
            elif isinstance(self.data, list):
                result["data"] = [
                    item.to_dict() if hasattr(item, "to_dict") else item 
                    for item in self.data
                ]
            else:
                result["data"] = self.data
        else:
            result["error"] = self.error
        
        return result


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_player_from_api(
    element: Dict[str, Any],
    team: Optional[Dict[str, Any]] = None,
    fixtures: Optional[List[Dict[str, Any]]] = None,
    include_expected: bool = True,
    include_derived: bool = True,
    include_transfers: bool = True,
) -> PlayerData:
    """
    Create PlayerData from raw FPL API element dict.
    
    This is the canonical way to create player objects from API data.
    
    Args:
        element: Raw player dict from bootstrap_static['elements']
        team: Optional team dict for team info
        fixtures: Optional list of fixture dicts for upcoming matches
        include_expected: Include expected stats (xG, xA)
        include_derived: Include derived stats (PPM, etc.)
        include_transfers: Include transfer information
        
    Returns:
        Standardized PlayerData object
    """
    from .constants import POSITION_ID_TO_NAME
    
    # Base data
    player = PlayerData(
        id=element.get("id", 0),
        web_name=element.get("web_name", "Unknown"),
        full_name=f"{element.get('first_name', '')} {element.get('second_name', '')}".strip(),
        team_id=element.get("team", 0),
        team_name=team.get("name", "Unknown") if team else "Unknown",
        team_short=team.get("short_name", "UNK") if team else "UNK",
        position=POSITION_ID_TO_NAME.get(element.get("element_type", 0), "UNK"),
        element_type=element.get("element_type", 0),
        price=element.get("now_cost", 0) / 10,
        price_change_event=element.get("cost_change_event", 0) / 10,
        price_change_start=element.get("cost_change_start", 0) / 10,
        total_points=element.get("total_points", 0),
        points_per_game=float(element.get("points_per_game", 0) or 0),
        form=float(element.get("form", 0) or 0),
        minutes=element.get("minutes", 0),
        goals_scored=element.get("goals_scored", 0),
        assists=element.get("assists", 0),
        clean_sheets=element.get("clean_sheets", 0),
        goals_conceded=element.get("goals_conceded", 0),
        bonus=element.get("bonus", 0),
        bps=element.get("bps", 0),
        influence=float(element.get("influence", 0) or 0),
        creativity=float(element.get("creativity", 0) or 0),
        threat=float(element.get("threat", 0) or 0),
        ict_index=float(element.get("ict_index", 0) or 0),
        selected_by_percent=float(element.get("selected_by_percent", 0) or 0),
        status=element.get("status", "a"),
        news=element.get("news", ""),
        chance_of_playing_next=element.get("chance_of_playing_next_round"),
        chance_of_playing_this=element.get("chance_of_playing_this_round"),
        yellow_cards=element.get("yellow_cards", 0),
        red_cards=element.get("red_cards", 0),
        own_goals=element.get("own_goals", 0),
        penalties_saved=element.get("penalties_saved", 0),
        penalties_missed=element.get("penalties_missed", 0),
        saves=element.get("saves", 0),
    )
    
    # Add expected stats
    if include_expected:
        xg = float(element.get("expected_goals", 0) or 0)
        xa = float(element.get("expected_assists", 0) or 0)
        xgi = float(element.get("expected_goal_involvements", 0) or 0)
        xgc = float(element.get("expected_goals_conceded", 0) or 0)
        
        player.expected_stats = ExpectedStats(
            expected_goals=xg,
            expected_assists=xa,
            expected_goal_involvements=xgi,
            expected_goals_conceded=xgc,
            goals_vs_xg=round(player.goals_scored - xg, 2),
            assists_vs_xa=round(player.assists - xa, 2),
        )
    
    # Add derived stats
    if include_derived:
        minutes = player.minutes
        appearances = minutes / 90.0 if minutes > 0 else 0
        cost = player.price if player.price > 0 else 1  # Avoid division by zero
        
        # Calculate minutes percentage (assuming ~38 * 90 = 3420 max minutes)
        # Adjust based on current GW
        max_possible_minutes = 3420  # Full season
        
        player.derived_stats = DerivedStats(
            points_per_90=round(player.total_points / appearances, 2) if appearances > 0 else 0,
            points_per_million=round(player.total_points / cost, 2),
            points_per_game_per_million=round(player.points_per_game / cost, 2),
            points_per_million_per_90=round((player.total_points / appearances) / cost, 2) if appearances > 0 else 0,
            bonus_per_90=round(player.bonus / appearances, 2) if appearances > 0 else 0,
            goals_per_90=round(player.goals_scored / appearances, 2) if appearances > 0 else 0,
            assists_per_90=round(player.assists / appearances, 2) if appearances > 0 else 0,
            appearances_90=round(appearances, 1),
            minutes_percent=round((minutes / max_possible_minutes) * 100, 1),
        )
    
    # Add transfer info
    if include_transfers:
        player.transfer_info = TransferInfo(
            transfers_in_event=element.get("transfers_in_event", 0),
            transfers_out_event=element.get("transfers_out_event", 0),
            net_transfers=element.get("transfers_in_event", 0) - element.get("transfers_out_event", 0),
            transfers_in_total=element.get("transfers_in", 0),
            transfers_out_total=element.get("transfers_out", 0),
            price_change_event=element.get("cost_change_event", 0) / 10,
            price_change_start=element.get("cost_change_start", 0) / 10,
        )
    
    # Add metadata
    player.meta = DataMeta(source="fpl_api")
    
    return player


def create_team_from_api(
    team_data: Dict[str, Any],
    fixtures: Optional[List[Dict[str, Any]]] = None,
) -> TeamData:
    """
    Create TeamData from raw FPL API team dict.
    
    Args:
        team_data: Raw team dict from bootstrap_static['teams']
        fixtures: Optional list of fixture dicts for upcoming matches
        
    Returns:
        Standardized TeamData object
    """
    team = TeamData(
        id=team_data.get("id", 0),
        name=team_data.get("name", "Unknown"),
        short_name=team_data.get("short_name", "UNK"),
        strength=team_data.get("strength", 0),
        strength_overall_home=team_data.get("strength_overall_home", 0),
        strength_overall_away=team_data.get("strength_overall_away", 0),
        strength_attack_home=team_data.get("strength_attack_home", 0),
        strength_attack_away=team_data.get("strength_attack_away", 0),
        strength_defence_home=team_data.get("strength_defence_home", 0),
        strength_defence_away=team_data.get("strength_defence_away", 0),
        position=team_data.get("position"),
        played=team_data.get("played", 0),
        wins=team_data.get("win", 0),
        draws=team_data.get("draw", 0),
        losses=team_data.get("loss", 0),
    )
    
    team.meta = DataMeta(source="fpl_api")
    
    return team


def create_gameweek_from_api(event: Dict[str, Any]) -> GameweekData:
    """
    Create GameweekData from raw FPL API event dict.
    
    Args:
        event: Raw event dict from bootstrap_static['events']
        
    Returns:
        Standardized GameweekData object
    """
    gw = GameweekData(
        id=event.get("id", 0),
        name=event.get("name", ""),
        deadline_time=event.get("deadline_time", ""),
        is_current=event.get("is_current", False),
        is_next=event.get("is_next", False),
        finished=event.get("finished", False),
        data_checked=event.get("data_checked", False),
        average_score=event.get("average_entry_score"),
        highest_score=event.get("highest_score"),
        most_selected=event.get("most_selected"),
        most_transferred_in=event.get("most_transferred_in"),
        most_captained=event.get("most_captained"),
        chip_plays=event.get("chip_plays", []),
    )
    
    gw.meta = DataMeta(source="fpl_api")
    
    return gw


def wrap_response(
    data: Any,
    success: bool = True,
    message: Optional[str] = None,
    error: Optional[str] = None,
    source: str = "fpl_api",
    cache_ttl: Optional[int] = None,
    is_cached: bool = False,
) -> Dict[str, Any]:
    """
    Wrap any data in a standardized ToolResponse.
    
    Use this to ensure all tool outputs have consistent structure.
    
    Args:
        data: The response data
        success: Whether the operation succeeded
        message: Optional success message
        error: Optional error message
        source: Data source identifier
        cache_ttl: Cache TTL in seconds
        is_cached: Whether data came from cache
        
    Returns:
        Dictionary with standardized structure
    """
    response = ToolResponse(
        success=success,
        data=data,
        message=message,
        error=error,
        meta=DataMeta(
            source=source,
            cache_ttl_seconds=cache_ttl,
            is_cached=is_cached,
        )
    )
    return response.to_dict()
