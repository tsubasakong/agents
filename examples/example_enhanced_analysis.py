#!/usr/bin/env python3
"""
Example: Enhanced Market Analysis with OpenAI Agent + MCP Integration

This example demonstrates how to use the enhanced executor with real MCP tools
for intelligent market analysis and trading decisions.

Requirements:
- Python 3.10+ (for MCP support)
- OpenAI API key
- MCP server endpoint
"""

import asyncio
import os
from dotenv import load_dotenv

from polymarket_agents.application.enhanced_executor import EnhancedExecutor, AgentConfig, MCPServerConfig
from polymarket_agents.utils.objects import SimpleMarket

async def main():
    """Example of enhanced market analysis"""
    
    # Load environment variables
    load_dotenv()
    
    # Create a sample market (replace with real market data)
    market = SimpleMarket(
        id=123456789,
        question="Will Bitcoin price exceed $100,000 by end of 2024?",
        end="2024-12-31T23:59:59Z",
        description="Market resolves based on Bitcoin reaching $100k USD",
        active=True,
        funded=True,
        rewardsMinSize=10.0,
        rewardsMaxSpread=0.05,
        volume=125000.0,
        spread=0.02,
        outcomes="Yes,No",
        outcome_prices="0.65,0.35",  # 65% Yes, 35% No
        clob_token_ids="token1,token2",
        enableOrderBook=True,
        liquidity=50000.0
    )
    
    print("🚀 Enhanced Market Analysis Example")
    print(f"📊 Market: {market.question}")
    print(f"💰 Current implied probability: 65% Yes, 35% No")
    print()
    
    # Configure MCP server
    mcp_config = MCPServerConfig(
        name="Trading MCP Server",
        url=os.getenv("MCP_REMOTE_ENDPOINT", "your-mcp-endpoint-here"),
        api_key=os.getenv("MCP_API_KEY"),
        enable_cache=True,
        timeout=60
    )
    
    # Configure agent
    agent_config = AgentConfig(
        model="o3-mini",
        # temperature=0.1,
        max_tokens=50000,
        timeout=180,
        max_retries=3
    )
    
    # Create enhanced executor
    executor = EnhancedExecutor(
        agent_config=agent_config,
        mcp_config=mcp_config
    )
    
    try:
        # Initialize MCP connection
        print("🔌 Connecting to MCP server...")
        await executor.initialize_mcp_connection()
        
        # Run enhanced analysis
        print("🔍 Running enhanced market analysis with MCP tools...")
        print("⏳ This may take 1-3 minutes for comprehensive analysis...")
        
        result = await executor.enhanced_market_analysis(market)
        
        # Display results
        print("\n📋 Analysis Results:")
        print("=" * 60)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📈 Recommendation: {result.get('recommendation', 'UNKNOWN')}")
            print(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
            print(f"🔗 Trace URL: {result.get('trace_url', 'Not available')}")
            
            print(f"\n💭 Analysis Reasoning:")
            reasoning = result.get('reasoning', 'No reasoning provided')
            print(reasoning[:2000] + "..." if len(reasoning) > 2000 else reasoning)
        
        # Cleanup
        await executor.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await executor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())