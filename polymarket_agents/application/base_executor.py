"""
Base executor class for Polymarket Agents.

This module provides a base class with common functionality shared between
different executor implementations, promoting code reuse and consistency.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from polymarket_agents.config import get_settings
from polymarket_agents.common.errors import ConfigurationError
from polymarket_agents.utils.objects import SimpleMarket, SimpleEvent
from polymarket_agents.polymarket.gamma import GammaMarketClient
from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.application.prompts import Prompter


class BaseExecutor(ABC):
    """
    Base class for all executors with common functionality.
    
    This class provides shared functionality like configuration loading,
    logging setup, and common utilities while allowing subclasses to
    implement their specific analysis methods.
    """
    
    def __init__(self, settings=None):
        """
        Initialize the base executor.
        
        Args:
            settings: Optional Settings instance. If None, loads from environment.
        """
        self.settings = settings or get_settings()
        self.logger = self._setup_logging()
        
        # Initialize common clients
        self.gamma = GammaMarketClient()
        self.polymarket = Polymarket()
        self.prompter = Prompter()
        
        # Log initialization
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    def _setup_logging(self) -> logging.Logger:
        """
        Set up logging for the executor.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.__class__.__name__)
        
        # Set log level from settings
        log_level = getattr(logging, self.settings.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(self.settings.log_format)
        
        # Create console handler if not already exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    async def analyze_market(self, market: SimpleMarket) -> Dict[str, Any]:
        """
        Analyze a market and provide trading recommendations.
        
        Args:
            market: Market to analyze
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        pass
    
    def filter_events_with_rag(self, events: List[SimpleEvent]) -> List[SimpleEvent]:
        """
        Filter events using RAG (Retrieval-Augmented Generation).
        
        Args:
            events: List of events to filter
            
        Returns:
            Filtered list of events
        """
        if not events:
            self.logger.warning("Empty events list provided to filter_events_with_rag()")
            return []
        
        # This is a base implementation - subclasses can override
        self.logger.info(f"Filtering {len(events)} events")
        return events
    
    def map_filtered_events_to_markets(self, filtered_events: List[SimpleEvent]) -> List[SimpleMarket]:
        """
        Map filtered events to their corresponding markets.
        
        Args:
            filtered_events: List of filtered events
            
        Returns:
            List of markets corresponding to the events
        """
        if not filtered_events:
            self.logger.warning("Empty filtered_events list provided to map_filtered_events_to_markets()")
            return []
        
        markets = []
        for event in filtered_events:
            try:
                # Get market IDs from event
                market_ids = self._extract_market_ids_from_event(event)
                
                for market_id in market_ids:
                    market_data = self.gamma.get_market(market_id)
                    if market_data:
                        formatted_market = self.polymarket.map_api_to_market(market_data)
                        if formatted_market:
                            markets.append(formatted_market)
                            
            except Exception as e:
                self.logger.error(f"Error processing event in map_filtered_events_to_markets: {e}")
        
        return markets
    
    def _extract_market_ids_from_event(self, event: SimpleEvent) -> List[str]:
        """
        Extract market IDs from an event.
        
        Args:
            event: Event to extract market IDs from
            
        Returns:
            List of market IDs
        """
        try:
            # This is a simplified implementation
            # In reality, you'd extract this from the event's metadata
            if hasattr(event, 'markets'):
                return event.markets.split(',') if isinstance(event.markets, str) else event.markets
            return []
        except Exception as e:
            self.logger.error(f"Error extracting market IDs from event: {e}")
            return []
    
    def filter_markets(self, markets: List[SimpleMarket]) -> List[SimpleMarket]:
        """
        Filter markets based on trading criteria.
        
        Args:
            markets: List of markets to filter
            
        Returns:
            Filtered list of markets
        """
        if not markets:
            self.logger.warning("Empty markets list provided to filter_markets()")
            return []
        
        filtered_markets = []
        for market in markets:
            try:
                # Basic filtering criteria
                if self._should_include_market(market):
                    filtered_markets.append(market)
            except Exception as e:
                self.logger.error(f"Error filtering market {market.id}: {e}")
        
        self.logger.info(f"Filtered {len(markets)} markets to {len(filtered_markets)}")
        return filtered_markets
    
    def _should_include_market(self, market: SimpleMarket) -> bool:
        """
        Determine if a market should be included based on basic criteria.
        
        Args:
            market: Market to evaluate
            
        Returns:
            True if market should be included, False otherwise
        """
        # Basic filtering criteria
        if market.liquidity < 100:  # Minimum liquidity
            return False
        
        if market.spread > 0.1:  # Maximum spread
            return False
        
        # Add more criteria as needed
        return True
    
    def get_market_analysis_context(self, market: SimpleMarket) -> Dict[str, Any]:
        """
        Get context for market analysis.
        
        Args:
            market: Market to get context for
            
        Returns:
            Dictionary containing market context
        """
        return {
            "market_id": market.id,
            "question": market.question,
            "description": market.description,
            "outcomes": market.outcomes,
            "current_prices": market.outcome_prices,
            "liquidity": market.liquidity,
            "spread": market.spread,
            "volume": getattr(market, 'volume', 0),
            "analysis_timestamp": None,  # Will be set by subclass
        }
    
    def validate_configuration(self) -> None:
        """
        Validate that the executor is properly configured.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            self.settings.validate()
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration: {str(e)}")
    
    def __str__(self) -> str:
        """String representation of the executor."""
        return f"{self.__class__.__name__}(model={self.settings.openai_model})"
    
    def __repr__(self) -> str:
        """Detailed representation of the executor."""
        return (
            f"{self.__class__.__name__}("
            f"model={self.settings.openai_model}, "
            f"temperature={self.settings.openai_temperature}, "
            f"environment={self.settings.environment})"
        ) 