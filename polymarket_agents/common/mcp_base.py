"""
MCP (Model Context Protocol) server management utilities.

This module provides a centralized way to manage MCP server connections
and handle MCP-related operations consistently across the application.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .errors import MCPError

logger = logging.getLogger(__name__)

# Try to import MCP - graceful fallback if not available
try:
    from agents.mcp import MCPServerSse
    MCP_AVAILABLE = True
except ImportError:
    logger.warning("MCP not available - MCP functionality will be disabled")
    MCPServerSse = None
    MCP_AVAILABLE = False


@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection."""
    
    name: str = "Polymarket MCP Server"
    url: str = "https://api.example-mcp-service.com"
    api_key: Optional[str] = None
    timeout: int = 60
    enable_cache: bool = True
    cache_ttl: int = 3600


class MCPServerManager:
    """
    Centralized MCP server management.
    
    This class provides a consistent interface for creating and managing
    MCP server connections across the application.
    """
    
    @staticmethod
    def is_mcp_available() -> bool:
        """Check if MCP is available in the environment."""
        return MCP_AVAILABLE
    
    @staticmethod
    def create_server(config: MCPServerConfig) -> Optional[MCPServerSse]:
        """
        Create an MCP server instance with the given configuration.
        
        Args:
            config: MCP server configuration
            
        Returns:
            MCPServerSse instance if successful, None otherwise
            
        Raises:
            MCPError: If MCP server creation fails
        """
        if not MCP_AVAILABLE:
            logger.warning("MCP not available - cannot create MCP server")
            return None
        
        try:
            if not config.url:
                raise MCPError("MCP server URL is required", retryable=False)
            
            server = MCPServerSse(
                name=config.name,
                params={"url": config.url},
                cache_tools_list=config.enable_cache,
                client_session_timeout_seconds=config.timeout,
            )
            
            logger.info(f"MCP server created successfully: {config.name} at {config.url}")
            return server
            
        except Exception as e:
            error_msg = f"Failed to initialize MCP server '{config.name}' at {config.url}: {str(e)}"
            logger.error(error_msg)
            raise MCPError(error_msg, server_url=config.url, retryable=True)
    
    @staticmethod
    def validate_config(config: MCPServerConfig) -> None:
        """
        Validate MCP server configuration.
        
        Args:
            config: MCP server configuration to validate
            
        Raises:
            MCPError: If configuration is invalid
        """
        if not config.url:
            raise MCPError("MCP server URL is required", retryable=False)
        
        if not config.url.startswith(('http://', 'https://')):
            raise MCPError("MCP server URL must start with http:// or https://", retryable=False)
        
        if config.timeout <= 0:
            raise MCPError("MCP server timeout must be greater than 0", retryable=False)
        
        if config.cache_ttl < 0:
            raise MCPError("MCP server cache TTL must be non-negative", retryable=False)
    
    @staticmethod
    def create_server_with_validation(config: MCPServerConfig) -> Optional[MCPServerSse]:
        """
        Create an MCP server instance with configuration validation.
        
        Args:
            config: MCP server configuration
            
        Returns:
            MCPServerSse instance if successful, None otherwise
            
        Raises:
            MCPError: If configuration is invalid or server creation fails
        """
        MCPServerManager.validate_config(config)
        return MCPServerManager.create_server(config)
    
    @staticmethod
    def get_server_info(server: MCPServerSse) -> Dict[str, Any]:
        """
        Get information about an MCP server.
        
        Args:
            server: MCP server instance
            
        Returns:
            Dictionary containing server information
        """
        if not server:
            return {"status": "unavailable", "reason": "Server is None"}
        
        try:
            return {
                "status": "available",
                "name": getattr(server, 'name', 'Unknown'),
                "cache_enabled": getattr(server, 'cache_tools_list', False),
                "timeout": getattr(server, 'client_session_timeout_seconds', 60),
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e)
            } 