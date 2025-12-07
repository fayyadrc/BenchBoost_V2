# data/__init__.py
# This file makes the data directory a Python package.

"""
FPL Data Layer

Provides consistent data access with standardized models and utilities.

Modules:
    - models: Standardized data models (PlayerData, TeamData, etc.)
    - constants: Shared constants and configuration
    - utils: Utility functions for data processing
    - api_client: FPL API client
    - cache: TTL-based caching system
    - stats: Player statistics and analysis
"""

from .constants import (
    POSITION_ID_TO_NAME,
    POSITION_NAME_TO_ID,
    POSITION_ID_TO_FULL_NAME,
    CACHE_TTL,
    SCORING,
    GAME_RULES,
    FIXTURE_DIFFICULTY,
    OWNERSHIP_TIERS,
    FORM_THRESHOLDS,
    VALUE_THRESHOLDS,
    VALID_PLAYER_METRICS,
    METRIC_DISPLAY_NAMES,
)

from .models import (
    Position,
    AvailabilityStatus,
    ChipType,
    FixtureDifficulty,
    DataMeta,
    ExpectedStats,
    DerivedStats,
    TransferInfo,
    UpcomingFixture,
    PlayerData,
    TeamData,
    GameweekData,
    Recommendation,
    ToolResponse,
    create_player_from_api,
    create_team_from_api,
    create_gameweek_from_api,
    wrap_response,
)

from .utils import (
    get_player_full_name,
    get_position_name,
    get_position_full_name,
    calculate_player_stats,
    calculate_expected_performance,
    classify_ownership,
    classify_form,
    classify_price,
    classify_transfer_trend,
    classify_fixture_difficulty,
    get_availability_text,
    enrich_player_data,
    parse_player_and_team,
    parse_price,
    format_price,
    format_number,
    format_percentage,
    format_metric_name,
    generate_player_summary,
)

__all__ = [
    # Constants
    "POSITION_ID_TO_NAME",
    "POSITION_NAME_TO_ID", 
    "POSITION_ID_TO_FULL_NAME",
    "CACHE_TTL",
    "SCORING",
    "GAME_RULES",
    "FIXTURE_DIFFICULTY",
    "OWNERSHIP_TIERS",
    "FORM_THRESHOLDS",
    "VALUE_THRESHOLDS",
    "VALID_PLAYER_METRICS",
    "METRIC_DISPLAY_NAMES",
    # Models
    "Position",
    "AvailabilityStatus",
    "ChipType",
    "FixtureDifficulty",
    "DataMeta",
    "ExpectedStats",
    "DerivedStats",
    "TransferInfo",
    "UpcomingFixture",
    "PlayerData",
    "TeamData",
    "GameweekData",
    "Recommendation",
    "ToolResponse",
    "create_player_from_api",
    "create_team_from_api",
    "create_gameweek_from_api",
    "wrap_response",
    # Utils
    "get_player_full_name",
    "get_position_name",
    "get_position_full_name",
    "calculate_player_stats",
    "calculate_expected_performance",
    "classify_ownership",
    "classify_form",
    "classify_price",
    "classify_transfer_trend",
    "classify_fixture_difficulty",
    "get_availability_text",
    "enrich_player_data",
    "parse_player_and_team",
    "parse_price",
    "format_price",
    "format_number",
    "format_percentage",
    "format_metric_name",
    "generate_player_summary",
]