"""
Polymarket Agents - AI trading agents for Polymarket with advanced MCP integration
"""

__version__ = "0.2.0"
__author__ = "Polymarket"
__email__ = "liam@polymarket.com"

# Core application classes
from .application.enhanced_executor import EnhancedExecutor
from .application.executor import Executor
from .application.trade import Trader
from .application.base_executor import BaseExecutor
from .application.agent_factory import AgentFactory, AgentConfig

# Configuration and common utilities
from .config import Settings, get_settings
from .common import (
    PolymarketAgentError,
    ConfigurationError,
    RetryableError,
    NonRetryableError,
    MCPError,
    TradingError,
    execute_with_retry,
    RetryConfig,
    MCPServerManager,
    MCPServerConfig,
)

# Core Polymarket integration
from .polymarket.polymarket import Polymarket
from .utils.objects import SimpleMarket, SimpleEvent

__all__ = [
    # Enhanced classes with new architecture
    "EnhancedExecutor",
    "BaseExecutor",
    "AgentFactory",
    "AgentConfig",
    
    # Configuration
    "Settings",
    "get_settings",
    
    # Common utilities and error handling
    "PolymarketAgentError",
    "ConfigurationError", 
    "RetryableError",
    "NonRetryableError",
    "MCPError",
    "TradingError",
    "execute_with_retry",
    "RetryConfig",
    "MCPServerManager",
    "MCPServerConfig",
    
    # Legacy/backwards compatibility
    "Executor",
    "Trader",
    
    # Core Polymarket classes
    "Polymarket",
    "SimpleMarket",
    "SimpleEvent"
] 