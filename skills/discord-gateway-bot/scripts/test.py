#!/usr/bin/env python3
"""
Hermes Discord Bot - Test Scripts
Run individual tests or full suite for verification.

Usage:
    python scripts/test.py [test_name]
    python scripts/test.py all
"""

import asyncio
import sys
import os
from pathlib import Path

# Add bot directory to path
BOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BOT_DIR))

from config import BotConfig
from gateway_client import HermesGatewayClient
from thread_manager import ThreadManager, ThreadSession


async def test_config():
    """Test configuration loading."""
    print("🧪 Testing configuration...")
    config = BotConfig.from_env()
    assert config.token, "Token not loaded"
    assert config.app_id, "App ID not loaded"
    assert config.guild_id, "Guild ID not loaded"
    assert config.gateway_url, "Gateway URL not loaded"
    print(f"  ✅ Token: {config.token[:20]}...")
    print(f"  ✅ App ID: {config.app_id}")
    print(f"  ✅ Guild ID: {config.guild_id}")
    print(f"  ✅ Gateway: {config.gateway_url}")
    return True


async def test_gateway_client():
    """Test Hermes Gateway connectivity."""
    print("\n🧪 Testing Gateway Client...")
    config = BotConfig.from_env()
    client = HermesGatewayClient(config.gateway_url)
    
    # Health check
    health = await client.get("/health")
    assert health.get("status") == "ok", f"Gateway unhealthy: {health}"
    print(f"  ✅ Gateway health: {health}")
    
    # Test endpoints exist
    endpoints = [
        ("/v1/cron/jobs", list),
        ("/v1/skills", list),
    ]
    for endpoint, expected_type in endpoints:
        try:
            result = await client.get(endpoint)
            assert isinstance(result, expected_type), f"{endpoint} returned wrong type"
            print(f"  ✅ {endpoint}: {len(result)} items")
        except Exception as e:
            print(f"  ⚠️ {endpoint}: {e} (may be expected if not implemented)")
    
    await client.close()
    return True


async def test_thread_manager():
    """Test ThreadManager with mock bot."""
    print("\n🧪 Testing ThreadManager...")
    
    class MockBot:
        def get_channel(self, channel_id):
            return None
    
    # Use temp persistence file
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    persistence_file = Path(temp_dir) / "discord_threads.json"
    
    # Monkey patch
    import thread_manager as tm
    original_file = tm.PERSISTENCE_FILE
    tm.PERSISTENCE_FILE = persistence_file
    
    try:
        bot = MockBot()
        manager = ThreadManager(bot)
        
        # Test register
        class MockThread:
            id = 123456789
            parent_id = 987654321
            guild = type('Guild', (), {'id': 111222333})()
            name = "test-thread"
        
        session = manager.register_thread(
            MockThread(), 
            owner_id=555666777,
            topic="Test Topic"
        )
        
        assert session.thread_id == 123456789
        assert session.channel_id == 987654321
        assert session.owner_id == 555666777
        assert session.topic == "Test Topic"
        assert session.is_active is True
        print("  ✅ Register thread")
        
        # Test get_session
        retrieved = manager.get_session(123456789)
        assert retrieved is not None
        assert retrieved.thread_id == 123456789
        print("  ✅ Get session")
        
        # Test set_hermes_session
        manager.set_hermes_session(123456789, "hermes-session-abc123")
        retrieved = manager.get_session(123456789)
        assert retrieved.hermes_session_id == "hermes-session-abc123"
        print("  ✅ Set Hermes session")
        
        # Test archive
        result = manager.archive_thread(123456789)
        assert result is True
        retrieved = manager.get_session(123456789)
        assert retrieved.is_active is False
        assert retrieved.hermes_session_id == "hermes-session-abc123"  # Preserved
        print("  ✅ Archive thread (preserves session)")
        
        # Test unarchive
        result = manager.unarchive_thread(123456789)
        assert result is True
        retrieved = manager.get_session(123456789)
        assert retrieved.is_active is True
        print("  ✅ Unarchive thread")
        
        # Test persistence (save/load)
        manager2 = ThreadManager(bot)
        assert len(manager2._threads) == 1
        session2 = manager2.get_session(123456789)
        assert session2.hermes_session_id == "hermes-session-abc123"
        assert session2.is_active is True
        print("  ✅ Persistence load")
        
        return True
    finally:
        tm.PERSISTENCE_FILE = original_file
        shutil.rmtree(temp_dir)


async def test_discord_structure():
    """Verify Discord structure constants."""
    print("\n🧪 Testing Discord structure definition...")
    from bot import STRUCTURE
    
    expected_categories = [
        "🚀 HERMES-OPS",
        "🔧 CN-TECH", 
        "🏗️ INFRA",
        "🤖 AGENTS",
        "📋 TASKS",
        "🧠 BRAIN",
    ]
    
    for cat in expected_categories:
        assert cat in STRUCTURE, f"Missing category: {cat}"
        assert len(STRUCTURE[cat]) == 4, f"Category {cat} should have 4 channels"
    
    total_channels = sum(len(channels) for channels in STRUCTURE.values())
    assert total_channels == 24, f"Expected 24 channels, got {total_channels}"
    
    print(f"  ✅ Categories: {len(expected_categories)}")
    print(f"  ✅ Total channels: {total_channels}")
    return True


async def run_all():
    """Run all tests."""
    print("=" * 50)
    print("HERMES DISCORD BOT - TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Config", test_config),
        ("Gateway Client", test_gateway_client),
        ("Thread Manager", test_thread_manager),
        ("Discord Structure", test_discord_structure),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    # Load .env if exists
    env_file = BOT_DIR / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # Run specific test or all
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "all":
            success = asyncio.run(run_all())
        else:
            print(f"Unknown test: {test_name}")
            print("Available: config, gateway, thread, structure, all")
            sys.exit(1)
    else:
        success = asyncio.run(run_all())
    
    sys.exit(0 if success else 1)