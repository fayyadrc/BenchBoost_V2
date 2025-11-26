#!/usr/bin/env python3
"""
MongoDB Test Script for FPL Chatbot
====================================
This script tests the MongoDB connection and validates the database schema,
collections, indexes, and data integrity.

Usage:
    python backend/database/test_mongodb.py
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# --- Path Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after loading env vars
try:
    from backend.database.db import get_db, MONGO_URI, DB_NAME
except Exception as e:
    print(f"Error importing database module: {e}")
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    
    if not MONGO_URI:
        print("ERROR: MONGO_URI environment variable is not set!")
        print("Please set it in your .env file")
        sys.exit(1)
    
    if not DB_NAME:
        print("ERROR: DB_NAME environment variable is not set!")
        print("Please set it in your .env file")
        sys.exit(1)
    
    from backend.database.db import get_db


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def test_connection() -> bool:
    """Test MongoDB connection"""
    print_header("Testing MongoDB Connection")
    
    try:
        db = get_db()
        # The ping command is cheap and does not require auth
        db.client.admin.command('ping')
        print_success(f"Connected to MongoDB successfully!")
        print_info(f"URI: {MONGO_URI[:20]}...{MONGO_URI[-10:] if len(MONGO_URI) > 30 else ''}")
        print_info(f"Database: {DB_NAME}")
        return True
    except ConnectionFailure as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print_error(f"MongoDB server selection timeout: {e}")
        print_warning("Make sure MongoDB is running and accessible")
        return False
    except Exception as e:
        print_error(f"Unexpected error during connection: {e}")
        return False


def test_collections() -> Dict[str, int]:
    """Test collections existence and count documents"""
    print_header("Testing Collections")
    
    expected_collections = ["players", "teams", "gameweeks", "fixtures"]
    collection_counts = {}
    
    try:
        db = get_db()
        existing_collections = db.list_collection_names()
        
        print_info(f"Found {len(existing_collections)} collections in database")
        
        for coll_name in expected_collections:
            if coll_name in existing_collections:
                count = db[coll_name].count_documents({})
                collection_counts[coll_name] = count
                print_success(f"Collection '{coll_name}': {count} documents")
            else:
                collection_counts[coll_name] = 0
                print_warning(f"Collection '{coll_name}' not found!")
        
        # Check for unexpected collections
        unexpected = set(existing_collections) - set(expected_collections)
        if unexpected:
            print_info(f"Additional collections found: {', '.join(unexpected)}")
        
        return collection_counts
    except Exception as e:
        print_error(f"Error testing collections: {e}")
        return {}


def test_indexes():
    """Test if indexes are properly created"""
    print_header("Testing Indexes")
    
    try:
        db = get_db()
        
        # Expected indexes for each collection
        expected_indexes = {
            "players": ["id_1", "web_name_1", "second_name_1", "team_1", 
                       "element_type_1", "now_cost_1_total_points_-1"],
            "teams": ["id_1", "name_1", "short_name_1"],
            "gameweeks": ["id_1", "is_current_1", "is_next_1"],
            "fixtures": ["id_1", "event_1", "team_h_1", "team_a_1", "kickoff_time_1"]
        }
        
        for coll_name, expected_idx in expected_indexes.items():
            if coll_name in db.list_collection_names():
                indexes = db[coll_name].list_indexes()
                index_names = [idx['name'] for idx in indexes]
                
                print_info(f"\n{coll_name.capitalize()} Collection Indexes:")
                
                for idx_name in expected_idx:
                    if idx_name in index_names:
                        print_success(f"  Index '{idx_name}' exists")
                    else:
                        print_warning(f"  Index '{idx_name}' missing!")
                
                # Check for unexpected indexes (excluding _id_)
                unexpected = set(index_names) - set(expected_idx) - {"_id_"}
                if unexpected:
                    print_info(f"  Additional indexes: {', '.join(unexpected)}")
            else:
                print_warning(f"Collection '{coll_name}' not found, skipping index check")
        
        print_success("\nIndex validation complete")
    except Exception as e:
        print_error(f"Error testing indexes: {e}")


def test_data_integrity():
    """Test data integrity and sample queries"""
    print_header("Testing Data Integrity")
    
    try:
        db = get_db()
        
        # Test 1: Check if players have required fields
        print_info("Testing player documents structure...")
        sample_player = db.players.find_one()
        if sample_player:
            required_fields = ["id", "web_name", "team", "element_type", "now_cost", "total_points"]
            missing_fields = [f for f in required_fields if f not in sample_player]
            
            if not missing_fields:
                print_success("Player documents have all required fields")
            else:
                print_warning(f"Player documents missing fields: {', '.join(missing_fields)}")
            
            # Show sample player
            print_info(f"Sample player: {sample_player.get('web_name', 'N/A')} "
                      f"(Team ID: {sample_player.get('team', 'N/A')}, "
                      f"Price: {sample_player.get('now_cost', 0) / 10}m)")
        else:
            print_warning("No player documents found")
        
        # Test 2: Check teams
        print_info("\nTesting team documents...")
        sample_team = db.teams.find_one()
        if sample_team:
            print_success(f"Sample team: {sample_team.get('name', 'N/A')} "
                         f"({sample_team.get('short_name', 'N/A')})")
        else:
            print_warning("No team documents found")
        
        # Test 3: Check current gameweek
        print_info("\nTesting gameweek documents...")
        current_gw = db.gameweeks.find_one({"is_current": True})
        if current_gw:
            print_success(f"Current gameweek: GW{current_gw.get('id', 'N/A')} "
                         f"({current_gw.get('name', 'N/A')})")
        else:
            print_warning("No current gameweek found")
        
        # Test 4: Check fixtures
        print_info("\nTesting fixture documents...")
        sample_fixture = db.fixtures.find_one()
        if sample_fixture:
            print_success(f"Sample fixture: Team {sample_fixture.get('team_h', 'N/A')} vs "
                         f"Team {sample_fixture.get('team_a', 'N/A')} "
                         f"(GW{sample_fixture.get('event', 'N/A')})")
        else:
            print_warning("No fixture documents found")
        
        print_success("\nData integrity check complete")
    except Exception as e:
        print_error(f"Error testing data integrity: {e}")


def test_queries():
    """Test common queries"""
    print_header("Testing Common Queries")
    
    try:
        db = get_db()
        
        # Query 1: Top 5 players by total points
        print_info("Query 1: Top 5 players by total points")
        top_players = list(db.players.find(
            {},
            {"web_name": 1, "total_points": 1, "now_cost": 1}
        ).sort("total_points", -1).limit(5))
        
        if top_players:
            for i, player in enumerate(top_players, 1):
                print_success(f"  {i}. {player.get('web_name', 'N/A')}: "
                            f"{player.get('total_points', 0)} points "
                            f"(£{player.get('now_cost', 0) / 10}m)")
        else:
            print_warning("No players found")
        
        # Query 2: Count players by position
        print_info("\nQuery 2: Players by position")
        positions = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}
        for pos_id, pos_name in positions.items():
            count = db.players.count_documents({"element_type": pos_id})
            print_success(f"  {pos_name}s: {count}")
        
        # Query 3: Upcoming fixtures
        print_info("\nQuery 3: Next 5 upcoming fixtures")
        upcoming_fixtures = list(db.fixtures.find(
            {"finished": False},
            {"team_h": 1, "team_a": 1, "event": 1, "kickoff_time": 1}
        ).sort("kickoff_time", 1).limit(5))
        
        if upcoming_fixtures:
            for i, fixture in enumerate(upcoming_fixtures, 1):
                kickoff = fixture.get('kickoff_time', 'TBD')
                print_success(f"  {i}. GW{fixture.get('event', 'N/A')}: "
                            f"Team {fixture.get('team_h', 'N/A')} vs "
                            f"Team {fixture.get('team_a', 'N/A')} ({kickoff})")
        else:
            print_warning("No upcoming fixtures found")
        
        print_success("\nQuery tests complete")
    except Exception as e:
        print_error(f"Error testing queries: {e}")


def test_database_stats():
    """Display database statistics"""
    print_header("Database Statistics")
    
    try:
        db = get_db()
        stats = db.command("dbstats")
        
        print_info(f"Database: {stats.get('db', 'N/A')}")
        print_info(f"Collections: {stats.get('collections', 0)}")
        print_info(f"Data Size: {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
        print_info(f"Storage Size: {stats.get('storageSize', 0) / 1024 / 1024:.2f} MB")
        print_info(f"Indexes: {stats.get('indexes', 0)}")
        print_info(f"Index Size: {stats.get('indexSize', 0) / 1024 / 1024:.2f} MB")
        
        print_success("\nDatabase statistics retrieved successfully")
    except Exception as e:
        print_error(f"Error getting database stats: {e}")


def run_all_tests():
    """Run all MongoDB tests"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          MongoDB Test Suite for FPL Chatbot                       ║")
    print("║          Running comprehensive database tests...                  ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    start_time = datetime.now()
    
    # Run tests
    connection_ok = test_connection()
    
    if not connection_ok:
        print_error("\n❌ Connection failed. Aborting remaining tests.")
        return False
    
    collection_counts = test_collections()
    test_indexes()
    test_data_integrity()
    test_queries()
    test_database_stats()
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_header("Test Summary")
    print_info(f"Test Duration: {duration:.2f} seconds")
    print_info(f"Timestamp: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_docs = sum(collection_counts.values())
    print_info(f"Total Documents: {total_docs}")
    
    if total_docs > 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ All tests completed successfully!{Colors.ENDC}\n")
        return True
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ Tests completed but database appears empty.{Colors.ENDC}")
        print(f"{Colors.WARNING}Run 'python backend/database/ingestion.py' to populate the database.{Colors.ENDC}\n")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Test interrupted by user.{Colors.ENDC}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}\n")
        sys.exit(1)
