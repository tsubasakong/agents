"""
Agent Factory for creating OpenAI agents with consistent configuration.

This module provides a centralized way to create OpenAI agents with
standardized configuration and MCP server integration.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from agents import Agent, ModelSettings

from polymarket_agents.config import get_settings
from polymarket_agents.common.mcp_base import MCPServerManager, MCPServerConfig
from polymarket_agents.common.errors import ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for OpenAI Agent creation."""
    
    name: str = "Polymarket Trading Agent"
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 50000
    timeout: int = 120
    max_retries: int = 3
    instructions: Optional[str] = None


class AgentFactory:
    """
    Factory for creating OpenAI agents with consistent configuration.
    
    This class provides a centralized way to create agents with proper
    configuration, MCP server integration, and error handling.
    """
    
    @staticmethod
    def create_agent(
        agent_config: Optional[AgentConfig] = None,
        mcp_config: Optional[MCPServerConfig] = None,
        settings=None
    ) -> Agent:
        """
        Create an OpenAI agent with consistent configuration.
        
        Args:
            agent_config: Configuration for the agent
            mcp_config: Configuration for MCP server integration
            settings: Application settings (optional)
            
        Returns:
            Configured OpenAI Agent instance
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        settings = settings or get_settings()
        
        # Use provided config or create from settings
        if agent_config is None:
            agent_config = AgentFactory._create_agent_config_from_settings(settings)
        
        # Create MCP server if configured
        mcp_server = None
        if mcp_config is not None:
            mcp_server = MCPServerManager.create_server(mcp_config)
        
        # Create model settings
        model_settings = AgentFactory._create_model_settings(agent_config)
        
        # Get instructions
        instructions = agent_config.instructions or settings.get_agent_instructions()
        
        # Create MCP servers list
        mcp_servers = [mcp_server] if mcp_server else []
        
        try:
            agent = Agent(
                name=agent_config.name,
                instructions=instructions,
                mcp_servers=mcp_servers,
                model=agent_config.model,
                model_settings=model_settings,
            )
            
            logger.info(f"Created agent: {agent_config.name} with model {agent_config.model}")
            if mcp_server:
                logger.info(f"Agent configured with MCP server: {mcp_config.name}")
            
            return agent
            
        except Exception as e:
            error_msg = f"Failed to create agent: {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
    
    @staticmethod
    def create_trading_agent(
        mcp_config: Optional[MCPServerConfig] = None,
        settings=None
    ) -> Agent:
        """
        Create a trading agent with default trading configuration.
        
        Args:
            mcp_config: Optional MCP server configuration
            settings: Application settings (optional)
            
        Returns:
            Configured trading agent
        """
        settings = settings or get_settings()
        
        # Create agent config optimized for trading
        agent_config = AgentConfig(
            name="Polymarket Trading Agent",
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            timeout=settings.openai_timeout,
            max_retries=settings.openai_max_retries,
            instructions=settings.get_agent_instructions()
        )
        
        return AgentFactory.create_agent(agent_config, mcp_config, settings)
    
    @staticmethod
    def create_analysis_agent(
        mcp_config: Optional[MCPServerConfig] = None,
        settings=None
    ) -> Agent:
        """
        Create an analysis agent optimized for market analysis.
        
        Args:
            mcp_config: Optional MCP server configuration
            settings: Application settings (optional)
            
        Returns:
            Configured analysis agent
        """
        settings = settings or get_settings()
        
        # Create agent config optimized for analysis
        agent_config = AgentConfig(
            name="Polymarket Analysis Agent",
            model=settings.openai_model,
            temperature=0.0,  # More deterministic for analysis
            max_tokens=settings.openai_max_tokens,
            timeout=settings.openai_timeout,
            max_retries=settings.openai_max_retries,
            instructions=AgentFactory._get_analysis_instructions(settings)
        )
        
        return AgentFactory.create_agent(agent_config, mcp_config, settings)
    
    @staticmethod
    def create_agent_with_mcp(
        mcp_url: str,
        mcp_api_key: Optional[str] = None,
        agent_config: Optional[AgentConfig] = None,
        settings=None
    ) -> Agent:
        """
        Create an agent with MCP server integration.
        
        Args:
            mcp_url: MCP server URL
            mcp_api_key: Optional MCP API key
            agent_config: Optional agent configuration
            settings: Application settings (optional)
            
        Returns:
            Agent with MCP server integration
        """
        mcp_config = MCPServerConfig(
            name="Dynamic MCP Server",
            url=mcp_url,
            api_key=mcp_api_key
        )
        
        return AgentFactory.create_agent(agent_config, mcp_config, settings)
    
    @staticmethod
    def _create_agent_config_from_settings(settings) -> AgentConfig:
        """
        Create agent configuration from application settings.
        
        Args:
            settings: Application settings
            
        Returns:
            Agent configuration
        """
        return AgentConfig(
            name="Polymarket Agent",
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            timeout=settings.openai_timeout,
            max_retries=settings.openai_max_retries,
        )
    
    @staticmethod
    def _create_model_settings(agent_config: AgentConfig) -> ModelSettings:
        """
        Create model settings from agent configuration.
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            Model settings for the agent
        """
        # For o3 models, temperature is ignored
        temperature = agent_config.temperature
        if agent_config.model.startswith("o3"):
            temperature = None
            logger.info(f"Using o3 model {agent_config.model} - temperature will be ignored")
        
        return ModelSettings(
            temperature=temperature,
            max_tokens=min(agent_config.max_tokens, 50000),  # API limit
        )
    
    @staticmethod
    def _get_analysis_instructions(settings) -> str:
        """
        Get specialized instructions for analysis agents.
        
        Args:
            settings: Application settings
            
        Returns:
            Analysis-specific instructions
        """
        return f"""
        You are a sophisticated market analysis agent for Polymarket prediction markets.
        
        Your primary role is to analyze market data, news, and trends to provide
        objective assessments of market conditions and probabilities.
        
        Key capabilities:
        - Market data analysis and trend identification
        - News sentiment analysis and impact assessment
        - Statistical modeling and probability estimation
        - Risk assessment and market dynamics evaluation
        
        Analysis guidelines:
        - Provide objective, data-driven analysis
        - Quantify uncertainty and confidence levels
        - Consider multiple perspectives and scenarios
        - Identify key factors influencing market outcomes
        - Assess information quality and reliability
        
        Always structure your analysis with:
        1. Market overview and current state
        2. Key factors and drivers
        3. Probability assessments with confidence intervals
        4. Risk factors and uncertainties
        5. Potential catalysts and timeline considerations
        
        Environment: {settings.environment}
        Analysis context: Prediction market analysis
        """
    
    @staticmethod
    def get_agent_info(agent: Agent) -> Dict[str, Any]:
        """
        Get information about an agent.
        
        Args:
            agent: Agent instance
            
        Returns:
            Dictionary containing agent information
        """
        try:
            return {
                "name": getattr(agent, 'name', 'Unknown'),
                "model": getattr(agent, 'model', 'Unknown'),
                "mcp_servers": len(getattr(agent, 'mcp_servers', [])),
                "has_mcp": len(getattr(agent, 'mcp_servers', [])) > 0,
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            } 