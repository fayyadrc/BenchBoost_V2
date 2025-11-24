#!/usr/bin/env python3
"""
FPL Data Consolidation Script

This script fetches data from all available FPL sources (APIs and web scrapes)
and consolidates them into a single JSON file for easy review.

Data Sources:
1. FPL API (via api_client.py) - players, teams, gameweeks, fixtures
2. Player Profiles (via player_injury_status.py) - injury/status information
3. Calculated Stats (via stats.py) - PPM, points per 90, etc.
4. FPL Alerts Scraper (via fplNews_scrape.py) - price changes
5. LiveFPL Scraper (via livefpl_scrape.py) - gameweek analysis (optional)

Usage:
    python consolidate_data.py
    python consolidate_data.py --entry-id 1605977 --event-id 15
    python consolidate_data.py --output custom_output.json
"""

import sys
import os
import json
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(project_root)

# Import data fetching modules
from backend.data.api_client import (
    bootstrap_static,
    fixtures,
    event_live,
    entry_summary,
    element_summary,
)
from backend.data.player_injury_status import get_all_players
from backend.data.stats import get_all_players_with_stats, get_fpl_rules
from backend.data.fplNews_scrape import scrape_fpl_alerts
from backend.data.livefpl_scrape import scrape_livefpl_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def fetch_api_data(
    event_id: Optional[int] = None,
    entry_id: Optional[int] = None,
    element_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fetch data from the FPL API.
    
    Args:
        event_id: Optional gameweek ID for event-specific data
        entry_id: Optional manager entry ID for entry-specific data
        element_id: Optional player ID for player-specific data
    
    Returns:
        Dictionary containing all fetched API data
    """
    logger.info("📡 Fetching FPL API data...")
    api_data = {}
    
    try:
        # Always fetch bootstrap-static (core data)
        logger.info("  - Fetching bootstrap-static data...")
        api_data["bootstrap_static"] = bootstrap_static()
        logger.info(f"    ✓ Retrieved {len(api_data['bootstrap_static'].get('elements', []))} players, "
                   f"{len(api_data['bootstrap_static'].get('teams', []))} teams, "
                   f"{len(api_data['bootstrap_static'].get('events', []))} gameweeks")
    except Exception as e:
        logger.error(f"    ✗ Failed to fetch bootstrap-static: {e}")
        api_data["bootstrap_static"] = {"error": str(e)}
    
    try:
        # Fetch all fixtures
        logger.info("  - Fetching all fixtures...")
        api_data["fixtures_all"] = fixtures()
        logger.info(f"    ✓ Retrieved {len(api_data['fixtures_all'])} fixtures")
    except Exception as e:
        logger.error(f"    ✗ Failed to fetch fixtures: {e}")
        api_data["fixtures_all"] = {"error": str(e)}
    
    # Optional: Event-specific data
    if event_id:
        try:
            logger.info(f"  - Fetching live data for gameweek {event_id}...")
            api_data["event_live"] = event_live(event_id)
            logger.info(f"    ✓ Retrieved live data for {len(api_data['event_live'].get('elements', []))} players")
        except Exception as e:
            logger.error(f"    ✗ Failed to fetch event live data: {e}")
            api_data["event_live"] = {"error": str(e)}
    
    # Optional: Entry-specific data
    if entry_id:
        try:
            logger.info(f"  - Fetching entry summary for manager {entry_id}...")
            api_data["entry_summary"] = entry_summary(entry_id)
            logger.info(f"    ✓ Retrieved entry summary")
        except Exception as e:
            logger.error(f"    ✗ Failed to fetch entry summary: {e}")
            api_data["entry_summary"] = {"error": str(e)}
    
    # Optional: Player-specific data
    if element_id:
        try:
            logger.info(f"  - Fetching element summary for player {element_id}...")
            api_data["element_summary"] = element_summary(element_id)
            logger.info(f"    ✓ Retrieved element summary")
        except Exception as e:
            logger.error(f"    ✗ Failed to fetch element summary: {e}")
            api_data["element_summary"] = {"error": str(e)}
    
    return api_data


def fetch_player_profiles() -> Dict[str, Any]:
    """
    Fetch player profiles with injury/status information.
    
    Returns:
        Dictionary containing player profiles or error information
    """
    logger.info("👥 Fetching player profiles with injury/status data...")
    try:
        players = get_all_players()
        logger.info(f"  ✓ Retrieved {len(players)} player profiles")
        return {"players": players, "count": len(players)}
    except Exception as e:
        logger.error(f"  ✗ Failed to fetch player profiles: {e}")
        return {"error": str(e)}


def fetch_calculated_stats() -> Dict[str, Any]:
    """
    Fetch calculated player statistics (PPM, points per 90, etc.).
    
    Returns:
        Dictionary containing calculated stats or error information
    """
    logger.info("📊 Fetching calculated player statistics...")
    stats_data = {}
    
    try:
        logger.info("  - Fetching all players with calculated stats...")
        players_with_stats = get_all_players_with_stats()
        stats_data["players_with_stats"] = players_with_stats
        logger.info(f"    ✓ Retrieved stats for {len(players_with_stats)} players")
    except Exception as e:
        logger.error(f"    ✗ Failed to fetch player stats: {e}")
        stats_data["players_with_stats"] = {"error": str(e)}
    
    try:
        logger.info("  - Fetching FPL rules knowledge base...")
        fpl_rules = get_fpl_rules()
        stats_data["fpl_rules"] = fpl_rules
        logger.info(f"    ✓ Retrieved FPL rules knowledge base")
    except Exception as e:
        logger.error(f"    ✗ Failed to fetch FPL rules: {e}")
        stats_data["fpl_rules"] = {"error": str(e)}
    
    return stats_data


def fetch_fpl_alerts() -> Dict[str, Any]:
    """
    Scrape price changes and status updates from FPL Alerts.
    
    Returns:
        Dictionary containing FPL alerts or error information
    """
    logger.info("🔔 Scraping FPL Alerts (price changes & status updates)...")
    try:
        alerts = scrape_fpl_alerts(headless=True)
        
        # Categorize alerts
        price_changes = [a for a in alerts if a.get("type") == "price_change"]
        status_updates = [a for a in alerts if a.get("type") == "status"]
        
        logger.info(f"  ✓ Retrieved {len(alerts)} alerts "
                   f"({len(price_changes)} price changes, {len(status_updates)} status updates)")
        
        return {
            "all_alerts": alerts,
            "price_changes": price_changes,
            "status_updates": status_updates,
            "summary": {
                "total": len(alerts),
                "price_changes": len(price_changes),
                "status_updates": len(status_updates),
            }
        }
    except Exception as e:
        logger.error(f"  ✗ Failed to scrape FPL alerts: {e}")
        return {"error": str(e)}


def fetch_livefpl_data(entry_id: int) -> Dict[str, Any]:
    """
    Scrape LiveFPL data for gameweek analysis.
    
    Args:
        entry_id: Manager entry ID
    
    Returns:
        Dictionary containing LiveFPL data or error information
    """
    logger.info(f"🎯 Scraping LiveFPL data for entry {entry_id}...")
    try:
        livefpl_data = scrape_livefpl_data(entry_id, headless=True)
        
        # Log summary
        differentials_count = len(livefpl_data.get("differentials", []))
        threats_count = len(livefpl_data.get("threats", []))
        team_players_count = len(livefpl_data.get("team_players", []))
        
        logger.info(f"  ✓ Retrieved LiveFPL data: "
                   f"{team_players_count} team players, "
                   f"{differentials_count} differentials, "
                   f"{threats_count} threats")
        
        return livefpl_data
    except Exception as e:
        logger.error(f"  ✗ Failed to scrape LiveFPL data: {e}")
        return {"error": str(e)}


def consolidate_all_data(
    entry_id: Optional[int] = None,
    event_id: Optional[int] = None,
    element_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Consolidate all FPL data from various sources.
    
    Args:
        entry_id: Optional manager entry ID
        event_id: Optional gameweek ID
        element_id: Optional player ID
    
    Returns:
        Dictionary containing all consolidated data
    """
    logger.info("🚀 Starting FPL data consolidation...")
    logger.info("=" * 60)
    
    consolidated = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parameters": {
                "entry_id": entry_id,
                "event_id": event_id,
                "element_id": element_id,
            },
            "description": "Consolidated FPL data from all available sources",
        }
    }
    
    # 1. Fetch API data
    consolidated["api_data"] = fetch_api_data(
        event_id=event_id,
        entry_id=entry_id,
        element_id=element_id,
    )
    
    # 2. Fetch player profiles
    consolidated["player_profiles"] = fetch_player_profiles()
    
    # 3. Fetch calculated stats
    consolidated["calculated_stats"] = fetch_calculated_stats()
    
    # 4. Scrape FPL alerts
    consolidated["fpl_alerts"] = fetch_fpl_alerts()
    
    # 5. Optional: Scrape LiveFPL data (only if entry_id provided)
    if entry_id:
        consolidated["livefpl_data"] = fetch_livefpl_data(entry_id)
    else:
        logger.info("ℹ️  Skipping LiveFPL scrape (no entry_id provided)")
        consolidated["livefpl_data"] = {
            "note": "Skipped - requires entry_id parameter"
        }
    
    logger.info("=" * 60)
    logger.info("✅ Data consolidation complete!")
    
    return consolidated


def save_to_file(data: Dict[str, Any], output_path: str) -> None:
    """
    Save consolidated data to a JSON file.
    
    Args:
        data: Dictionary containing consolidated data
        output_path: Path to output JSON file
    """
    logger.info(f"💾 Saving consolidated data to {output_path}...")
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Get file size
        file_size = os.path.getsize(output_path)
        file_size_mb = file_size / (1024 * 1024)
        
        logger.info(f"✅ Successfully saved {file_size_mb:.2f} MB to {output_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        raise


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Consolidate FPL data from all sources into a single JSON file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (API data, player profiles, stats, FPL alerts)
  python consolidate_data.py
  
  # Include LiveFPL data for a specific manager
  python consolidate_data.py --entry-id 1605977
  
  # Include event-specific data for gameweek 15
  python consolidate_data.py --event-id 15
  
  # Full data with custom output file
  python consolidate_data.py --entry-id 1605977 --event-id 15 --output my_data.json
        """,
    )
    
    parser.add_argument(
        "--entry-id",
        type=int,
        help="FPL manager entry ID (enables LiveFPL scraping and entry-specific API data)",
    )
    parser.add_argument(
        "--event-id",
        type=int,
        help="Gameweek/event ID for event-specific data (e.g., live scores)",
    )
    parser.add_argument(
        "--element-id",
        type=int,
        help="Player/element ID for player-specific data",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="consolidated_fpl_data.json",
        help="Output JSON file path (default: consolidated_fpl_data.json)",
    )
    
    args = parser.parse_args()
    
    try:
        # Consolidate all data
        consolidated_data = consolidate_all_data(
            entry_id=args.entry_id,
            event_id=args.event_id,
            element_id=args.element_id,
        )
        
        # Save to file
        save_to_file(consolidated_data, args.output)
        
        logger.info("")
        logger.info("📋 Summary:")
        logger.info(f"  - Output file: {args.output}")
        logger.info(f"  - Timestamp: {consolidated_data['metadata']['timestamp']}")
        logger.info(f"  - Data sections: {len(consolidated_data) - 1}")  # -1 for metadata
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
