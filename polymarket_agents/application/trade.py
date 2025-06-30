from polymarket_agents.application.enhanced_executor import EnhancedExecutor, AgentConfig, MCPServerConfig
from polymarket_agents.polymarket.gamma import GammaMarketClient as Gamma
from polymarket_agents.polymarket.polymarket import Polymarket

import shutil
import asyncio
import os
import random
from dotenv import load_dotenv


class Trader:
    def __init__(self):
        load_dotenv()
        self.polymarket = Polymarket()
        self.gamma = Gamma()
        
        # Configure enhanced executor as the ONLY decision maker
        mcp_config = MCPServerConfig(
            name="Trading MCP Server",
            url=os.getenv("MCP_REMOTE_ENDPOINT", "your-mcp-endpoint-here"),
            api_key=os.getenv("MCP_API_KEY"),
            enable_cache=True,
            timeout=60
        )
        
        agent_config = AgentConfig(
            model="gpt-4.1",
            temperature=0.1,  # Will be ignored for o3 models - see enhanced_executor.py line ~185
            max_tokens=50000,
            timeout=180,
            max_retries=3
        )
        
        self.enhanced_executor = EnhancedExecutor(
            agent_config=agent_config,
            mcp_config=mcp_config
        )

    def pre_trade_logic(self) -> None:
        self.clear_local_dbs()

    def clear_local_dbs(self) -> None:
        try:
            shutil.rmtree("local_db_events")
        except:
            pass
        try:
            shutil.rmtree("local_db_markets")
        except:
            pass

    async def _enhanced_trade_analysis(self, market):
        """Run enhanced AI analysis with MCP tools - the ONLY analysis method"""
        try:
            print(f"🔍 Running enhanced MCP analysis for: {market.question}")
            
            # Initialize MCP connection
            await self.enhanced_executor.initialize_mcp_connection()
            
            # Run enhanced analysis
            result = await self.enhanced_executor.enhanced_market_analysis(market)
            
            print(f"📈 AI Recommendation: {result.get('recommendation', 'UNKNOWN')}")
            print(f"🎯 Confidence Level: {result.get('confidence', 0):.1%}")
            print(f"🔗 Analysis Trace: {result.get('trace_url', 'Not available')}")
            
            reasoning = result.get('reasoning', 'No reasoning provided')
            print(f"💭 Reasoning: {reasoning[:300]}{'...' if len(reasoning) > 300 else ''}")
            
            return result
            
        except Exception as e:
            print(f"❌ Enhanced analysis failed: {e}")
            raise e
        finally:
            await self.enhanced_executor.cleanup()

    def one_best_trade(self) -> None:
        """
        Enhanced autonomous trading using ONLY MCP-powered AI analysis.
        
        This strategy:
        1. Gets tradeable markets
        2. Uses ENHANCED AI with MCP tools for analysis
        3. Makes trading decisions based on AI recommendations
        4. NO fallback to simple analysis - enhanced only
        """
        try:
            self.pre_trade_logic()

            print("🚀 ENHANCED AUTONOMOUS TRADER - MCP POWERED")
            print("=" * 60)
            
            # Check MCP configuration
            mcp_endpoint = os.getenv("MCP_REMOTE_ENDPOINT")
            if not mcp_endpoint or mcp_endpoint == "your-mcp-endpoint-here":
                print("❌ ERROR: MCP_REMOTE_ENDPOINT not configured!")
                print("   Please set MCP_REMOTE_ENDPOINT in your .env file")
                print("   Example: MCP_REMOTE_ENDPOINT=https://your-mcp-server.com/sse")
                return

            print("1. 📊 FETCHING TRADEABLE MARKETS...")
            all_markets = self.polymarket.get_all_markets()
            tradeable_markets = self.polymarket.filter_markets_for_trading(all_markets)
            print(f"   ✅ FOUND {len(tradeable_markets)} TRADEABLE MARKETS")

            if not tradeable_markets:
                print("❌ No tradeable markets found. Exiting.")
                return

            # Sort by liquidity and select top markets for analysis
            tradeable_markets = sorted(tradeable_markets, key=lambda x: x.liquidity, reverse=True)
            markets_to_analyze = tradeable_markets[:20]  # Top 3 most liquid
            
            print(f"2. 🎯 SELECTED TOP {len(markets_to_analyze)} MARKETS BY LIQUIDITY")
            for i, market in enumerate(markets_to_analyze, 1):
                print(f"   {i}. {market.question[:80]}...")
                print(f"      💰 Liquidity: ${market.liquidity:,.2f} | Spread: {market.spread:.1%}")

            print("\n3. 🤖 ENHANCED AI ANALYSIS WITH MCP TOOLS...")
            print(f"   🔌 MCP Server: {mcp_endpoint}")
            
            # Analyze the most liquid market
            selected_market = random.choice(markets_to_analyze)
            print(f"   📈 Analyzing: {selected_market.question}")
            
            # Run async enhanced analysis
            analysis_result = asyncio.run(self._enhanced_trade_analysis(selected_market))
            
            if "error" in analysis_result:
                print(f"❌ Analysis failed: {analysis_result['error']}")
                print("🛑 TRADING HALTED - No fallback analysis available")
                return
            
            # Extract trading decision
            recommendation = analysis_result.get('recommendation', 'HOLD')
            confidence = analysis_result.get('confidence', 0)
            
            print(f"\n4. 📋 TRADING DECISION:")
            print(f"   📈 Recommendation: {recommendation}")
            print(f"   🎯 Confidence: {confidence:.1%}")
            
            # Determine trade execution based on AI recommendation and confidence
            should_trade = False
            if recommendation == "BUY" and confidence >= 0.7:
                should_trade = True
                trade_side = "Yes"
            elif recommendation == "SELL" and confidence >= 0.7:
                should_trade = True
                trade_side = "No"
            else:
                print(f"   🤔 Confidence too low ({confidence:.1%}) or HOLD recommendation")
                print("   ⏸️  No trade executed")
            
            if should_trade:
                print(f"\n5. 💰 TRADE EXECUTION PLAN:")
                print(f"   Market: {selected_market.question}")
                print(f"   Side: {trade_side}")
                print(f"   Amount: 10 USDC (test amount)")
                print(f"   Confidence: {confidence:.1%}")
                
                print("\n6. 🛡️  TRADE EXECUTION DISABLED (Safety Mode)")
                print("   Uncomment execution code below after reviewing TOS")
                
                # SAFETY: Trade execution disabled by default
                # Uncomment after reviewing polymarket.com/tos
                # try:
                #     trade_result = self.polymarket.execute_market_order(
                #         market=selected_market,
                #         side=trade_side,
                #         amount=10.0  # USDC
                #     )
                #     print(f"✅ TRADE EXECUTED: {trade_result}")
                # except Exception as trade_error:
                #     print(f"❌ TRADE EXECUTION FAILED: {trade_error}")
            else:
                print("\n5. ⏸️  NO TRADE EXECUTED")
                print("   Reason: Low confidence or HOLD recommendation")

        except Exception as e:
            print(f"❌ Critical error in autonomous trader: {e}")
            import traceback
            traceback.print_exc()
            print("🛑 TRADING HALTED")

    def maintain_positions(self):
        """Maintain existing positions using enhanced analysis"""
        # TODO: Implement position maintenance with enhanced executor
        pass

    def incentive_farm(self):
        """Farm incentives using enhanced market selection"""
        # TODO: Implement incentive farming with enhanced analysis
        pass


def main():
    """Main entry point for the enhanced trader"""
    trader = Trader()
    trader.one_best_trade()

if __name__ == "__main__":
    main()
