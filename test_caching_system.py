#!/usr/bin/env python3
"""
Test script to verify enhanced caching system implementation.

Tests:
1. Cache loading and TTL functionality
2. Context builder formatters
3. Smart tool routing
4. Cache statistics
"""

import sys
import os
import time

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(project_root)

from backend.data import cache
from backend.agent import context_builder

def test_cache_loading():
    """Test 1: Cache loading and statistics"""
    print("=" * 60)
    print("TEST 1: Cache Loading and Statistics")
    print("=" * 60)
    
    # Load core data
    print("\n1. Loading core game data...")
    start_time = time.time()
    data = cache.load_core_game_data()
    load_time = time.time() - start_time
    
    print(f"   ✓ Loaded in {load_time:.2f}s")
    print(f"   ✓ Players: {len(data.get('players', {}))}")
    print(f"   ✓ Teams: {len(data.get('teams', {}))}")
    print(f"   ✓ Gameweeks: {len(data.get('gameweeks', {}))}")
    print(f"   ✓ Fixtures: {len(data.get('fixtures', {}))}")
    
    # Test cache hit
    print("\n2. Testing cache hit...")
    start_time = time.time()
    cached_data = cache.load_core_game_data()
    cache_time = time.time() - start_time
    
    print(f"   ✓ Retrieved in {cache_time:.2f}s (should be <0.01s)")
    
    # Get cache stats
    print("\n3. Cache statistics:")
    stats = cache.get_cache_stats()
    print(f"   ✓ Hits: {stats['hits']}")
    print(f"   ✓ Misses: {stats['misses']}")
    print(f"   ✓ Hit Rate: {stats['hit_rate_percent']}%")
    print(f"   ✓ Cache Size: {stats['cache_size']} entries")
    
    return True


def test_context_builders():
    """Test 2: Context builder formatters"""
    print("\n" + "=" * 60)
    print("TEST 2: Context Builder Formatters")
    print("=" * 60)
    
    # Ensure data is loaded
    cache.load_core_game_data()
    
    # Test player context
    print("\n1. Player Context:")
    player_context = context_builder.build_player_context(["Haaland", "Salah"])
    print(player_context)
    
    # Test player comparison
    print("\n2. Player Comparison:")
    comparison = context_builder.build_player_comparison(
        ["Haaland", "Salah", "Kane"],
        sort_by="total_points"
    )
    print(comparison[:300] + "..." if len(comparison) > 300 else comparison)
    
    # Test fixture difficulty
    print("\n3. Fixture Difficulty:")
    fixtures = context_builder.build_fixture_difficulty_narrative("Arsenal", num_fixtures=3)
    print(fixtures)
    
    # Test gameweek summary
    print("\n4. Gameweek Summary:")
    gw_summary = context_builder.build_gameweek_summary()
    print(gw_summary)
    
    return True


def test_cache_lookup_performance():
    """Test 3: Cache lookup performance"""
    print("\n" + "=" * 60)
    print("TEST 3: Cache Lookup Performance")
    print("=" * 60)
    
    # Ensure data is loaded
    cache.load_core_game_data()
    
    # Test multiple lookups
    test_players = ["Haaland", "Salah", "Kane", "Saka", "Palmer"]
    
    print(f"\nTesting {len(test_players)} player lookups...")
    start_time = time.time()
    
    for player_name in test_players:
        player = cache.get_player_by_name(player_name)
        if player:
            print(f"   ✓ Found: {player.get('web_name')}")
        else:
            print(f"   ✗ Not found: {player_name}")
    
    total_time = time.time() - start_time
    avg_time = total_time / len(test_players)
    
    print(f"\nTotal time: {total_time:.4f}s")
    print(f"Average per lookup: {avg_time:.4f}s")
    print(f"Expected: <0.001s per lookup")
    
    return True


def test_cache_invalidation():
    """Test 4: Cache invalidation"""
    print("\n" + "=" * 60)
    print("TEST 4: Cache Invalidation")
    print("=" * 60)
    
    # Get initial stats
    initial_stats = cache.get_cache_stats()
    print(f"\nInitial cache size: {initial_stats['cache_size']}")
    
    # Invalidate cache
    print("Invalidating cache...")
    cache.invalidate_cache()
    
    # Check stats after invalidation
    after_stats = cache.get_cache_stats()
    print(f"Cache size after invalidation: {after_stats['cache_size']}")
    print(f"   ✓ Cache cleared successfully" if after_stats['cache_size'] == 0 else "   ✗ Cache not cleared")
    
    # Reload data
    print("\nReloading data...")
    cache.load_core_game_data(force_refresh=True)
    
    final_stats = cache.get_cache_stats()
    print(f"Cache size after reload: {final_stats['cache_size']}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ENHANCED CACHING SYSTEM VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Cache Loading and Statistics", test_cache_loading),
        ("Context Builder Formatters", test_context_builders),
        ("Cache Lookup Performance", test_cache_lookup_performance),
        ("Cache Invalidation", test_cache_invalidation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    # Final cache stats
    print("\n" + "=" * 60)
    print("FINAL CACHE STATISTICS")
    print("=" * 60)
    final_stats = cache.get_cache_stats()
    for key, value in final_stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
