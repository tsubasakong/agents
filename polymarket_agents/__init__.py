"""
Polymarket Agents - AI trading agents for Polymarket with advanced MCP integration
"""

__version__ = "0.2.0"
__author__ = "Polymarket"
__email__ = "liam@polymarket.com"

from .application.enhanced_executor import EnhancedExecutor, AgentConfig, MCPServerConfig
from .application.executor import Executor
from .application.trade import Trader
from .polymarket.polymarket import Polymarket
from .utils.objects import SimpleMarket, SimpleEvent

__all__ = [
    "EnhancedExecutor",
    "AgentConfig", 
    "MCPServerConfig",
    "Executor",
    "Trader",
    "Polymarket",
    "SimpleMarket",
    "SimpleEvent"
] 