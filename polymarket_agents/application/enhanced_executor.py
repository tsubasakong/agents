"""
Enhanced Executor with OpenAI Agent and Remote MCP Server Integration
Based on agent_example.py pattern using OpenAIAgent
"""

import os
import json
import logging
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

# Import from the installed openai-agents package  
from agents import Agent, Runner, gen_trace_id, trace, ModelSettings, set_default_openai_api

set_default_openai_api("responses") 

# Try to import MCP - graceful fallback if not available
try:
    from agents.mcp import MCPServerSse
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️  MCP not available - enhanced analysis will use basic mode")
    MCPServerSse = None
    MCP_AVAILABLE = False

# Import from local polymarket_agents package
from polymarket_agents.utils.objects import SimpleMarket
from polymarket_agents.application.executor import Executor as BaseExecutor

@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection"""
    name: str = "Polymarket MCP Server"
    url: str = "https://api.example-mcp-service.com"
    api_key: Optional[str] = None
    timeout: int = 60
    enable_cache: bool = True
    cache_ttl: int = 3600

@dataclass
class AgentConfig:
    """Configuration for OpenAI Agent"""
    model: str = "gpt-4.1"  # Production-ready model
    temperature: float = 0.1
    max_tokens: int = 50000
    timeout: int = 120  # Longer timeout for MCP calls
    max_retries: int = 3

class EnhancedExecutor(BaseExecutor):
    """Enhanced executor with OpenAI Agent and MCP server integration using agent pattern"""
    
    def __init__(self, agent_config: AgentConfig = None, mcp_config: MCPServerConfig = None):
        super().__init__()
        load_dotenv()
        
        # Configuration
        self.agent_config = agent_config or AgentConfig()
        self.mcp_config = mcp_config or MCPServerConfig(
            url=os.getenv("MCP_REMOTE_ENDPOINT", "https://api.example-mcp-service.com"),
            api_key=os.getenv("MCP_API_KEY")
        )
        
        # Initialize MCP Server (if available)
        self.mcp_server = None
        if MCP_AVAILABLE and MCPServerSse:
            try:
                self.mcp_server = MCPServerSse(
                    name=self.mcp_config.name,
                    params={"url": self.mcp_config.url},
                    cache_tools_list=self.mcp_config.enable_cache,
                    client_session_timeout_seconds=self.mcp_config.timeout,
                )
                print(f"✅ MCP server configured at: {self.mcp_config.url}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize MCP server at {self.mcp_config.url}: {e}")
                print("⚠️  MCP server initialization failed - using basic analysis mode")
                self.mcp_server = None
        else:
            print("⚠️  MCP server not available - using basic analysis mode")
        
        # OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Context for agent conversations
        self.agent_context = {}
        self.trace_id = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def initialize_mcp_connection(self):
        """Initialize MCP server connection - handled by MCPServerSse"""
        try:
            if self.mcp_server:
                self.logger.info(f"MCP server configured at: {self.mcp_config.url}")
                # The MCPServerSse handles connection and tool discovery automatically
                return True
            else:
                self.logger.warning("MCP server not available - using basic mode")
                return False
        except Exception as e:
            self.logger.error(f"Failed to configure MCP server: {e}")
            return False
    async def enhanced_market_analysis(self, market: SimpleMarket) -> Dict[str, Any]:
        """
        Enhanced market analysis using OpenAI agent with MCP tools
        """
        try:
            # Prepare market context
            market_context = {
                "market_id": market.id,
                "question": market.question,
                "description": market.description,
                "current_prices": market.outcome_prices,
                "outcomes": market.outcomes,
                "liquidity": market.liquidity,
                "spread": market.spread,
                "volume": market.volume
            }
            
            # Update agent context
            self.agent_context.update(market_context)
            
            # Generate trace ID for this analysis
            self.trace_id = gen_trace_id()
            self.logger.debug(f"Generated trace ID: {self.trace_id}")
            
            # Create agent instructions
            instructions = f"""
            You are an expert prediction market trader analyzing Polymarket opportunities.
            
            You have access to MCP tools that can help you gather market data, news, and analysis.
            Use these tools to make informed trading decisions.
            Do NOT promise to call a  MCP tools later. If a function call is required, emit it now; otherwise respond normally.


            
            When analyzing a market:
            1. Gather relevant external data using available tools
            2. Analyze current market pricing vs fair value
            3. Consider external factors (news, price movements, etc.)
            4. Assess risk/reward profile
            5. Provide a clear trade recommendation with confidence level
            
            Format your final recommendation as:
            - Recommendation: BUY/SELL/HOLD
            - Confidence: X% (0-100)
            - Reasoning: Clear explanation of your analysis
            """
            
            # Create model settings (exclude temperature for o3 models)
            model_settings_params = {
                "max_tokens": min(self.agent_config.max_tokens, 10000),
            }
            
            # Only add temperature for models that support it (not o3 models)
            if not self.agent_config.model.startswith("o3"):
                model_settings_params["temperature"] = self.agent_config.temperature
                
            model_settings = ModelSettings(**model_settings_params)
            
            # Create OpenAI Agent (with or without MCP)
            mcp_servers = [self.mcp_server] if self.mcp_server else []
            agent = Agent(
                name="Polymarket Trading Analyst",
                instructions=instructions,
                mcp_servers=mcp_servers,
                model=self.agent_config.model,
                model_settings=model_settings,
            )
            
            # Prepare analysis request
            analysis_request = f"""
            Please analyze this prediction market and provide a trading recommendation:
            
            Market Question: "{market.question}"
            Description: {market.description}
            
            Current Market Data:
            - Outcome Prices: {market.outcome_prices}
            - Liquidity: ${market.liquidity:,.2f}
            - Spread: {market.spread:.1%}
            - Volume: ${market.volume:,.2f}
            
            Use available MCP tools to gather relevant information, then provide your analysis.
            """
            
            # Try MCP mode first, fall back to basic mode if needed
            mcp_success = False
            result = None
            
            if self.mcp_server:
                try:
                    async with self.mcp_server:
                        with trace(workflow_name="Polymarket Enhanced Analysis", trace_id=self.trace_id):
                            # Execute agent with retry logic
                            result = await self._execute_with_retry(
                                Runner.run,
                                starting_agent=agent,
                                input=analysis_request,
                                context=self.agent_context,
                            )
                            mcp_success = True
                            
                except Exception as mcp_error:
                    self.logger.warning(f"MCP server failed: {mcp_error}, falling back to basic analysis")
                    print("⚠️  MCP server failed - falling back to basic analysis")
                    mcp_success = False
            
            # If MCP failed or not available, use basic mode
            if not mcp_success:
                # Create agent without MCP tools for basic mode
                agent_basic = Agent(
                    name="Polymarket Trading Analyst",
                    instructions=instructions,
                    mcp_servers=[],  # No MCP servers
                    model=self.agent_config.model,
                    model_settings=model_settings,
                )
                
                with trace(workflow_name="Polymarket Basic Analysis", trace_id=self.trace_id):
                    # Execute agent with retry logic (no MCP tools)
                    result = await self._execute_with_retry(
                        Runner.run,
                        starting_agent=agent_basic,
                        input=analysis_request,
                        context=self.agent_context,
                    )
            
            # Process results
            if result:
                # Update context with any new values from result
                if hasattr(result, "context") and result.context:
                    self.agent_context.update(result.context)
                
                # Parse and return the trading recommendation
                recommendation = self._parse_trading_recommendation(result.final_output)
                recommendation["analysis_type"] = "enhanced_ai_mcp" if mcp_success else "basic_ai_no_mcp"
                return recommendation
            else:
                raise Exception("No result from agent execution")
                        
        except Exception as e:
            self.logger.error(f"Error in enhanced market analysis: {e}")
            return {
                "error": str(e),
                "recommendation": "HOLD",
                "confidence": 0.0,
                "reasoning": "Analysis failed due to technical error",
                "trace_url": self.get_trace_url() if self.trace_id else None
            }
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with retry logic"""
        max_retries = self.agent_config.max_retries
        last_error = None
        
        for retry in range(max_retries):
            try:
                if self.agent_config.timeout:
                    return await asyncio.wait_for(
                        func(*args, **kwargs), 
                        timeout=self.agent_config.timeout
                    )
                return await func(*args, **kwargs)
                
            except Exception as error:
                last_error = error
                if retry >= max_retries - 1:
                    break
                    
                self.logger.warning(
                    f"Retryable error in attempt {retry + 1}/{max_retries}: {str(error)}"
                )
                # Exponential backoff
                await asyncio.sleep(2 ** retry)
        
        # All retries failed
        error_message = f"Operation failed after {max_retries} retries: {str(last_error)}"
        self.logger.error(error_message)
        raise Exception(error_message)
    
    def get_trace_url(self) -> str:
        """Get the URL for the current trace"""
        if self.trace_id:
            return f"https://platform.openai.com/traces/trace?trace_id={self.trace_id}"
        return "No trace ID available"
    
    def _parse_trading_recommendation(self, content: str) -> Dict[str, Any]:
        """Parse the AI response into structured trading recommendation"""
        try:
            import re
            
            # Initialize defaults
            recommendation = "HOLD"
            confidence = 0.5
            reasoning = content
            
            content_lower = content.lower()
            
            # Extract recommendation
            if "recommendation:" in content_lower:
                rec_match = re.search(r'recommendation:\s*(buy|sell|hold)', content_lower)
                if rec_match:
                    recommendation = rec_match.group(1).upper()
            else:
                # Fallback pattern matching
                if "strong buy" in content_lower or ("buy" in content_lower and "don't buy" not in content_lower):
                    recommendation = "BUY"
                elif "strong sell" in content_lower or ("sell" in content_lower and "don't sell" not in content_lower):
                    recommendation = "SELL"
            
            # Extract confidence
            confidence_patterns = [
                r'confidence[:\s]*(\d+)%',
                r'confidence[:\s]*(\d+)',
                r'(\d+)%\s*confidence',
                r'(\d+)\s*percent\s*confidence'
            ]
            
            for pattern in confidence_patterns:
                match = re.search(pattern, content_lower)
                if match:
                    confidence = float(match.group(1)) / 100
                    break
            
            # Extract reasoning section if structured
            reasoning_match = re.search(r'reasoning:(.*?)(?=recommendation:|confidence:|$)', content, re.IGNORECASE | re.DOTALL)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            
            return {
                "recommendation": recommendation,
                "confidence": confidence,
                "reasoning": reasoning,
                "full_analysis": content,
                "analysis_type": "enhanced_ai_mcp",
                "trace_url": self.get_trace_url()
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing recommendation: {e}")
            return {
                "recommendation": "HOLD",
                "confidence": 0.0,
                "reasoning": content,
                "analysis_type": "enhanced_ai_mcp",
                "parse_error": str(e),
                "trace_url": self.get_trace_url()
            }
    
    async def cleanup(self):
        """Cleanup connections"""
        self.logger.info("Enhanced executor cleanup completed")
        # MCP server cleanup is handled automatically in context manager


# Async wrapper for integration with existing sync code
def run_enhanced_analysis(market: SimpleMarket, mcp_config: MCPServerConfig = None) -> Dict[str, Any]:
    """Synchronous wrapper for enhanced market analysis"""
    async def _run():
        executor = EnhancedExecutor(mcp_config=mcp_config)
        await executor.initialize_mcp_connection()
        try:
            result = await executor.enhanced_market_analysis(market)
            return result
        finally:
            await executor.cleanup()
    
    return asyncio.run(_run())