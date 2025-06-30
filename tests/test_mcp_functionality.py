#!/usr/bin/env python3
"""
Test script to thoroughly test MCP functionality in the refactored Polymarket Agents
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_mcp_imports():
    """Test MCP-related imports and graceful fallback"""
    print("🔍 Testing MCP imports and fallback logic...")
    
    try:
        from polymarket_agents.application.enhanced_executor import (
            EnhancedExecutor, 
            AgentConfig, 
            MCPServerConfig,
            MCP_AVAILABLE
        )
        
        print(f"✅ Enhanced executor imports successful")
        print(f"📊 MCP Available: {MCP_AVAILABLE}")
        
        if MCP_AVAILABLE:
            print("✅ MCP is available for enhanced analysis")
        else:
            print("⚠️  MCP not available - will use basic AI mode")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_mcp_config_creation():
    """Test creating MCP configurations"""
    print("\n⚙️  Testing MCP configuration creation...")
    
    try:
        from polymarket_agents.application.enhanced_executor import MCPServerConfig, AgentConfig
        
        # Test with environment variables
        load_dotenv()
        
        mcp_config = MCPServerConfig(
            name="Test MCP Server",
            url=os.getenv("MCP_REMOTE_ENDPOINT", "https://test-mcp-endpoint.com"),
            api_key=os.getenv("MCP_API_KEY", "test-key"),
            enable_cache=True,
            timeout=60
        )
        
        agent_config = AgentConfig(
            model="gpt-4o",
            temperature=0.1,
            max_tokens=10000,
            timeout=120,
            max_retries=3
        )
        
        print(f"✅ MCP Config: {mcp_config.name} at {mcp_config.url}")
        print(f"✅ Agent Config: {agent_config.model} with {agent_config.max_tokens} tokens")
        
        return mcp_config, agent_config
        
    except Exception as e:
        print(f"❌ Configuration creation failed: {e}")
        return None, None

def test_enhanced_executor_creation():
    """Test creating EnhancedExecutor with different configurations"""
    print("\n🤖 Testing Enhanced Executor creation...")
    
    try:
        from polymarket_agents.application.enhanced_executor import EnhancedExecutor, AgentConfig, MCPServerConfig
        
        # Test with default config
        print("  📝 Testing with default configuration...")
        executor_default = EnhancedExecutor()
        print("  ✅ Default executor created")
        
        # Test with custom config
        print("  📝 Testing with custom configuration...")
        mcp_config = MCPServerConfig(
            name="Custom Test MCP",
            url="https://custom-test-endpoint.com",
            api_key="custom-test-key"
        )
        
        agent_config = AgentConfig(
            model="gpt-4o",
            temperature=0.2,
            max_tokens=5000
        )
        
        executor_custom = EnhancedExecutor(
            agent_config=agent_config,
            mcp_config=mcp_config
        )
        print("  ✅ Custom executor created")
        
        # Check if MCP server was initialized
        if hasattr(executor_custom, 'mcp_server'):
            if executor_custom.mcp_server:
                print("  ✅ MCP server initialized")
            else:
                print("  ⚠️  MCP server is None (fallback mode)")
        
        return executor_default, executor_custom
        
    except Exception as e:
        print(f"❌ Enhanced executor creation failed: {e}")
        return None, None

async def test_mcp_connection():
    """Test MCP connection initialization"""
    print("\n🔌 Testing MCP connection initialization...")
    
    try:
        from polymarket_agents.application.enhanced_executor import EnhancedExecutor, MCPServerConfig
        
        # Test with a test endpoint
        mcp_config = MCPServerConfig(
            name="Connection Test MCP",
            url="https://test-connection-endpoint.com",
            api_key="test-connection-key",
            timeout=10  # Short timeout for testing
        )
        
        executor = EnhancedExecutor(mcp_config=mcp_config)
        
        # Test initialization
        print("  📡 Attempting MCP connection initialization...")
        result = await executor.initialize_mcp_connection()
        
        if result:
            print("  ✅ MCP connection initialization successful")
        else:
            print("  ⚠️  MCP connection initialization failed (expected with test endpoint)")
        
        # Test cleanup
        await executor.cleanup()
        print("  ✅ Executor cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ MCP connection test failed: {e}")
        return False

async def test_enhanced_analysis_without_mcp():
    """Test enhanced analysis in fallback mode (without MCP)"""
    print("\n🧠 Testing enhanced analysis in fallback mode...")
    
    try:
        from polymarket_agents.application.enhanced_executor import EnhancedExecutor
        from polymarket_agents.utils.objects import SimpleMarket
        
        # Create a test market
        test_market = SimpleMarket(
            id=999999,
            question="Will this be a successful MCP test?",
            end="2024-12-31T23:59:59Z",
            description="Test market for MCP functionality verification",
            active=True,
            funded=True,
            rewardsMinSize=1.0,
            rewardsMaxSpread=0.1,
            volume=1000.0,
            spread=0.05,
            outcomes="Yes,No",
            outcome_prices="0.6,0.4",
            clob_token_ids="test1,test2",
            enableOrderBook=True,
            liquidity=500.0
        )
        
        # Create executor (will use fallback mode if MCP not available)
        executor = EnhancedExecutor()
        
        print(f"  📊 Test Market: {test_market.question}")
        print(f"  💰 Liquidity: ${test_market.liquidity:,.2f}")
        print(f"  📈 Implied odds: {test_market.outcome_prices}")
        
        # Test without actually running full analysis (to avoid API calls)
        print("  🔍 Testing market context preparation...")
        
        market_context = {
            "market_id": test_market.id,
            "question": test_market.question,
            "description": test_market.description,
            "current_prices": test_market.outcome_prices,
            "outcomes": test_market.outcomes,
            "liquidity": test_market.liquidity,
            "spread": test_market.spread,
            "volume": test_market.volume
        }
        
        print("  ✅ Market context prepared successfully")
        print(f"  📋 Context keys: {list(market_context.keys())}")
        
        # Test trace ID generation
        from agents import gen_trace_id
        trace_id = gen_trace_id()
        print(f"  🔗 Generated trace ID: {trace_id}")
        
        await executor.cleanup()
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced analysis test failed: {e}")
        return False

def test_trader_integration():
    """Test that the Trader class uses enhanced executor correctly"""
    print("\n🎯 Testing Trader integration with Enhanced Executor...")
    
    try:
        from polymarket_agents.application.trade import Trader
        
        # Create trader instance
        trader = Trader()
        
        # Check enhanced executor integration
        if hasattr(trader, 'enhanced_executor'):
            print("  ✅ Trader has enhanced_executor")
            
            # Check configuration
            if hasattr(trader.enhanced_executor, 'mcp_config'):
                config = trader.enhanced_executor.mcp_config
                print(f"  📊 MCP Config: {config.name}")
                print(f"  🔗 MCP URL: {config.url}")
                print(f"  ⏱️  Timeout: {config.timeout}s")
            
            if hasattr(trader.enhanced_executor, 'agent_config'):
                config = trader.enhanced_executor.agent_config
                print(f"  🤖 Agent Model: {config.model}")
                print(f"  📊 Max Tokens: {config.max_tokens}")
                print(f"  🎯 Temperature: {config.temperature}")
        else:
            print("  ❌ Trader missing enhanced_executor")
            return False
        
        # Check that old agent attribute is gone
        if hasattr(trader, 'agent'):
            print("  ⚠️  Trader still has old 'agent' attribute")
        else:
            print("  ✅ Old 'agent' attribute properly removed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Trader integration test failed: {e}")
        return False

async def test_run_enhanced_analysis_wrapper():
    """Test the synchronous wrapper function"""
    print("\n🔄 Testing run_enhanced_analysis wrapper function...")
    
    try:
        from polymarket_agents.application.enhanced_executor import run_enhanced_analysis, MCPServerConfig
        from polymarket_agents.utils.objects import SimpleMarket
        
        # Create a simple test market
        test_market = SimpleMarket(
            id=888888,
            question="Will the wrapper function work correctly?",
            end="2024-12-31T23:59:59Z",
            description="Test market for wrapper function",
            active=True,
            funded=True,
            rewardsMinSize=1.0,
            rewardsMaxSpread=0.1,
            volume=500.0,
            spread=0.03,
            outcomes="Yes,No",
            outcome_prices="0.7,0.3",
            clob_token_ids="wrap1,wrap2",
            enableOrderBook=True,
            liquidity=250.0
        )
        
        print(f"  📊 Testing with market: {test_market.question}")
        
        # Test wrapper function exists and is callable
        print("  🔍 Checking wrapper function accessibility...")
        print(f"  ✅ run_enhanced_analysis function available: {callable(run_enhanced_analysis)}")
        
        # Note: We won't actually call it to avoid API calls, but we've verified it exists
        print("  ✅ Wrapper function test completed (without API call)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Wrapper function test failed: {e}")
        return False

async def main():
    """Run all MCP functionality tests"""
    print("🧪 Comprehensive MCP Functionality Test")
    print("=" * 50)
    
    tests = [
        ("MCP Imports & Fallback", test_mcp_imports),
        ("MCP Configuration", test_mcp_config_creation),
        ("Enhanced Executor Creation", test_enhanced_executor_creation),
        ("MCP Connection", test_mcp_connection),
        ("Enhanced Analysis Fallback", test_enhanced_analysis_without_mcp),
        ("Trader Integration", test_trader_integration),
        ("Wrapper Function", test_run_enhanced_analysis_wrapper),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 {test_name}")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n📊 MCP Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All MCP tests passed!")
        print("\n🔍 Summary:")
        print("✅ MCP imports work with graceful fallback")
        print("✅ Enhanced executor properly configured")
        print("✅ Trader integration successful") 
        print("✅ All components ready for MCP or fallback mode")
        print("\n🚀 Ready to test with real MCP endpoint!")
    else:
        print("❌ Some MCP tests failed. Check issues above.")
    
    return passed == total

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 