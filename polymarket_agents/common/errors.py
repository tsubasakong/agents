"""
Common exception classes for Polymarket Agents.

This module provides standardized error handling across the application,
with clear error types and consistent error messaging.
"""

from typing import Optional, Dict, Any


class PolymarketAgentError(Exception):
    """Base exception class for all Polymarket Agent errors."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        retryable: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.retryable = retryable
        
    def __str__(self) -> str:
        return f"{self.message}" + (f" - Details: {self.details}" if self.details else "")


class ConfigurationError(PolymarketAgentError):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, missing_keys: Optional[list] = None):
        super().__init__(message, {"missing_keys": missing_keys}, retryable=False)
        self.missing_keys = missing_keys or []


class RetryableError(PolymarketAgentError):
    """Raised for errors that can be retried."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, retryable=True)


class NonRetryableError(PolymarketAgentError):
    """Raised for errors that should not be retried."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, retryable=False)


class MCPError(PolymarketAgentError):
    """Raised for MCP server related errors."""
    
    def __init__(
        self, 
        message: str, 
        server_url: Optional[str] = None,
        retryable: bool = True
    ):
        details = {"server_url": server_url} if server_url else {}
        super().__init__(message, details, retryable=retryable)
        self.server_url = server_url


class TradingError(PolymarketAgentError):
    """Raised for trading-related errors."""
    
    def __init__(
        self, 
        message: str, 
        market_id: Optional[str] = None,
        trade_data: Optional[Dict[str, Any]] = None,
        retryable: bool = False
    ):
        details = {}
        if market_id:
            details["market_id"] = market_id
        if trade_data:
            details["trade_data"] = trade_data
            
        super().__init__(message, details, retryable=retryable)
        self.market_id = market_id
        self.trade_data = trade_data 