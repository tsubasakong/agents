"""
Centralized configuration management for Polymarket Agents.

This module provides a single source of truth for all configuration,
replacing scattered environment variable loading throughout the application.
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from functools import lru_cache

from dotenv import load_dotenv

from polymarket_agents.common.errors import ConfigurationError
from polymarket_agents.common.utils import validate_required_env_vars, safe_float_parse, safe_int_parse

# Load environment variables once at module import
load_dotenv()


@dataclass
class Settings:
    """
    Centralized configuration settings for Polymarket Agents.
    
    This class consolidates all configuration from environment variables
    and provides validation and defaults.
    """
    
    # Core API Keys
    openai_api_key: str = ""
    polygon_wallet_private_key: str = ""
    
    # MCP Configuration
    mcp_remote_endpoint: str = "https://api.example-mcp-service.com"
    mcp_api_key: Optional[str] = None
    mcp_timeout: int = 60
    mcp_enable_cache: bool = True
    mcp_cache_ttl: int = 3600
    
    # OpenAI Configuration
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 50000
    openai_timeout: int = 120
    openai_max_retries: int = 3
    
    # Trading Configuration
    max_trade_amount_usdc: float = 100.0
    risk_tolerance: float = 0.7
    min_confidence_threshold: float = 0.6
    
    # External API Keys
    tavily_api_key: Optional[str] = None
    newsapi_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    
    # Polymarket Configuration
    polymarket_chain_id: int = 137  # Polygon mainnet
    polymarket_testnet: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Database Configuration
    local_db_directory: str = "./local_db"
    vector_db_directory: str = "./vector_db"
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    # Required environment variables
    required_env_vars: List[str] = field(default_factory=lambda: [
        "OPENAI_API_KEY",
        "POLYGON_WALLET_PRIVATE_KEY"
    ])
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create Settings instance from environment variables.
        
        Returns:
            Settings instance populated from environment variables
            
        Raises:
            ConfigurationError: If required environment variables are missing
        """
        # Define required environment variables
        required_vars = ["OPENAI_API_KEY", "POLYGON_WALLET_PRIVATE_KEY"]
        
        # Validate required environment variables
        missing_vars = validate_required_env_vars(required_vars, dict(os.environ))
        if missing_vars:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_vars)}",
                missing_keys=missing_vars
            )
        
        return cls(
            # Core API Keys
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            polygon_wallet_private_key=os.getenv("POLYGON_WALLET_PRIVATE_KEY", ""),
            
            # MCP Configuration
            mcp_remote_endpoint=os.getenv("MCP_REMOTE_ENDPOINT", "https://api.example-mcp-service.com"),
            mcp_api_key=os.getenv("MCP_API_KEY"),
            mcp_timeout=safe_int_parse(os.getenv("MCP_TIMEOUT", "60"), 60),
            mcp_enable_cache=os.getenv("MCP_ENABLE_CACHE", "true").lower() == "true",
            mcp_cache_ttl=safe_int_parse(os.getenv("MCP_CACHE_TTL", "3600"), 3600),
            
            # OpenAI Configuration
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            openai_temperature=safe_float_parse(os.getenv("OPENAI_TEMPERATURE", "0.1"), 0.1),
            openai_max_tokens=safe_int_parse(os.getenv("OPENAI_MAX_TOKENS", "50000"), 50000),
            openai_timeout=safe_int_parse(os.getenv("OPENAI_TIMEOUT", "120"), 120),
            openai_max_retries=safe_int_parse(os.getenv("OPENAI_MAX_RETRIES", "3"), 3),
            
            # Trading Configuration
            max_trade_amount_usdc=safe_float_parse(os.getenv("MAX_TRADE_AMOUNT_USDC", "100.0"), 100.0),
            risk_tolerance=safe_float_parse(os.getenv("RISK_TOLERANCE", "0.7"), 0.7),
            min_confidence_threshold=safe_float_parse(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.6"), 0.6),
            
            # External API Keys
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            newsapi_api_key=os.getenv("NEWSAPI_API_KEY"),
            coingecko_api_key=os.getenv("COINGECKO_API_KEY"),
            alpha_vantage_api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
            
            # Polymarket Configuration
            polymarket_chain_id=safe_int_parse(os.getenv("POLYMARKET_CHAIN_ID", "137"), 137),
            polymarket_testnet=os.getenv("POLYMARKET_TESTNET", "false").lower() == "true",
            
            # Logging Configuration
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            
            # Database Configuration
            local_db_directory=os.getenv("LOCAL_DB_DIRECTORY", "./local_db"),
            vector_db_directory=os.getenv("VECTOR_DB_DIRECTORY", "./vector_db"),
            
            # Environment
            environment=os.getenv("ENVIRONMENT", "production"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration as a dictionary."""
        return {
            "model": self.openai_model,
            "temperature": self.openai_temperature,
            "max_tokens": self.openai_max_tokens,
            "timeout": self.openai_timeout,
            "max_retries": self.openai_max_retries,
        }
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP configuration as a dictionary."""
        return {
            "url": self.mcp_remote_endpoint,
            "api_key": self.mcp_api_key,
            "timeout": self.mcp_timeout,
            "enable_cache": self.mcp_enable_cache,
            "cache_ttl": self.mcp_cache_ttl,
        }
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration as a dictionary."""
        return {
            "max_trade_amount_usdc": self.max_trade_amount_usdc,
            "risk_tolerance": self.risk_tolerance,
            "min_confidence_threshold": self.min_confidence_threshold,
        }
    
    def get_agent_instructions(self) -> str:
        """Get default agent instructions."""
        return f"""
        You are a sophisticated trading agent for Polymarket, a prediction market platform.
        
        Your capabilities include:
        - Analyzing market data and trends
        - Evaluating news and external information
        - Making informed trading decisions
        - Risk management and position sizing
        
        Configuration:
        - Maximum trade amount: ${self.max_trade_amount_usdc} USDC
        - Risk tolerance: {self.risk_tolerance}
        - Minimum confidence threshold: {self.min_confidence_threshold}
        - Environment: {self.environment}
        
        Always provide clear reasoning for your recommendations and consider:
        1. Market liquidity and spread
        2. Recent news and events
        3. Historical patterns
        4. Risk-reward ratios
        5. Confidence levels
        
        Respond with structured recommendations including confidence scores.
        """
    
    def validate(self) -> None:
        """
        Validate configuration settings.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not self.openai_api_key:
            raise ConfigurationError("OpenAI API key is required")
        
        if not self.polygon_wallet_private_key:
            raise ConfigurationError("Polygon wallet private key is required")
        
        if self.openai_temperature < 0 or self.openai_temperature > 2:
            raise ConfigurationError("OpenAI temperature must be between 0 and 2")
        
        if self.openai_max_tokens <= 0:
            raise ConfigurationError("OpenAI max tokens must be greater than 0")
        
        if self.risk_tolerance < 0 or self.risk_tolerance > 1:
            raise ConfigurationError("Risk tolerance must be between 0 and 1")
        
        if self.min_confidence_threshold < 0 or self.min_confidence_threshold > 1:
            raise ConfigurationError("Minimum confidence threshold must be between 0 and 1")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    Returns:
        Settings instance
    """
    settings = Settings.from_env()
    settings.validate()
    return settings


# Convenience function for backwards compatibility
def load_settings() -> Settings:
    """
    Load and validate settings from environment.
    
    Returns:
        Settings instance
    """
    return get_settings() 