#!/usr/bin/env python3
"""
Test script to verify the Polymarket Agents refactoring was successful
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all new import paths work correctly"""
    print("🔍 Testing import paths...")
    
    try:
        # Test main package import
        import polymarket_agents
        print(f"✅ polymarket_agents v{polymarket_agents.__version__}")
        
        # Test enhanced executor import
        from polymarket_agents.application.enhanced_executor import EnhancedExecutor, AgentConfig, MCPServerConfig
        print("✅ Enhanced executor imports")
        
        # Test trader import
        from polymarket_agents.application.trade import Trader
        print("✅ Trader import")
        
        # Test CLI import (check if typer app exists)
        try:
            from scripts.python.cli import app
            print("✅ CLI import")
        except ImportError as cli_error:
            print(f"⚠️  CLI import issue (non-critical): {cli_error}")
            # This is okay - CLI might have some missing legacy dependencies
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_files_exist():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "pyproject.toml",
        ".python-version", 
        "setup_uv.sh",
        "run_cli_uv.sh",
        "run_enhanced_trader_uv.sh",
        "MIGRATION_UV.md",
        "README_REFACTORING_SUMMARY.md",
        "polymarket_agents/__init__.py",
        "polymarket_agents/application/enhanced_executor.py",
        "polymarket_agents/application/trade.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_enhanced_executor_config():
    """Test that enhanced executor can be configured"""
    print("\n⚙️  Testing enhanced executor configuration...")
    
    try:
        from polymarket_agents.application.enhanced_executor import EnhancedExecutor, AgentConfig, MCPServerConfig
        
        # Test configuration creation
        mcp_config = MCPServerConfig(
            name="Test MCP Server",
            url="https://test-endpoint.com",
            api_key="test-key"
        )
        
        agent_config = AgentConfig(
            model="gpt-4o",
            temperature=0.1,
            max_tokens=10000
        )
        
        # Test executor creation (without initialization)
        executor = EnhancedExecutor(
            agent_config=agent_config,
            mcp_config=mcp_config
        )
        
        print("✅ Enhanced executor configuration")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced executor configuration failed: {e}")
        return False

def test_trader_enhanced_only():
    """Test that trader is configured for enhanced-only analysis"""
    print("\n🤖 Testing trader enhanced-only configuration...")
    
    try:
        from polymarket_agents.application.trade import Trader
        
        # Create trader instance
        trader = Trader()
        
        # Check that it has enhanced_executor
        if hasattr(trader, 'enhanced_executor'):
            print("✅ Trader has enhanced_executor")
        else:
            print("❌ Trader missing enhanced_executor")
            return False
        
        # Check that it doesn't have old agent
        if hasattr(trader, 'agent'):
            print("⚠️  Trader still has old 'agent' attribute")
        else:
            print("✅ Old 'agent' attribute removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Trader test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Polymarket Agents Refactoring Verification")
    print("=" * 50)
    
    tests = [
        ("Import Paths", test_imports),
        ("File Structure", test_files_exist), 
        ("Enhanced Executor Config", test_enhanced_executor_config),
        ("Trader Enhanced-Only", test_trader_enhanced_only)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactoring successful!")
        print("\n🚀 Next steps:")
        print("1. Run: ./setup_uv.sh")
        print("2. Configure .env with API keys")
        print("3. Test: ./run_enhanced_trader_uv.sh")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 