"""
Shared retry logic for Polymarket Agents.

This module provides unified retry functionality with exponential backoff
to replace duplicate implementations across the codebase.
"""

import asyncio
import logging
import random
from typing import Any, Callable, Optional, List, Type, Union
from dataclasses import dataclass

from .errors import RetryableError, NonRetryableError


logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    timeout: Optional[float] = None
    retryable_exceptions: List[Type[Exception]] = None
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [
                RetryableError,
                asyncio.TimeoutError,
                ConnectionError,
                TimeoutError,
            ]
    
    def is_retryable(self, error: Exception) -> bool:
        """Check if an error is retryable."""
        # Check if it's a PolymarketAgentError with retryable flag
        if hasattr(error, 'retryable'):
            return error.retryable
        
        # Check if it's in the list of retryable exceptions
        return isinstance(error, tuple(self.retryable_exceptions))
    
    def get_delay(self, retry_count: int) -> float:
        """Calculate delay for the given retry attempt."""
        delay = self.base_delay * (self.backoff_multiplier ** retry_count)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 0.1) * delay
        return min(delay + jitter, self.max_delay)


async def execute_with_retry(
    func: Callable,
    *args,
    retry_config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """
    Execute a function with retry logic and exponential backoff.
    
    Args:
        func: The function to execute (can be sync or async)
        *args: Positional arguments for the function
        retry_config: Configuration for retry behavior
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function execution
        
    Raises:
        The last exception encountered if all retries fail
    """
    config = retry_config or RetryConfig()
    last_error = None
    
    for attempt in range(config.max_retries + 1):  # +1 for initial attempt
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                if config.timeout:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs), 
                        timeout=config.timeout
                    )
                else:
                    result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            return result
            
        except Exception as error:
            last_error = error
            
            # Check if we should retry
            if attempt >= config.max_retries:
                logger.error(f"Operation failed after {config.max_retries + 1} attempts: {error}")
                break
            
            if not config.is_retryable(error):
                logger.error(f"Non-retryable error encountered: {error}")
                break
            
            # Calculate delay and wait
            delay = config.get_delay(attempt)
            logger.warning(
                f"Retryable error in attempt {attempt + 1}/{config.max_retries + 1}: {error}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            await asyncio.sleep(delay)
    
    # All retries failed
    if last_error:
        raise last_error
    else:
        raise RuntimeError("Unknown error occurred during retry execution")


def execute_with_retry_sync(
    func: Callable,
    *args,
    retry_config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """
    Synchronous version of execute_with_retry.
    
    Args:
        func: The function to execute (must be synchronous)
        *args: Positional arguments for the function
        retry_config: Configuration for retry behavior
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function execution
        
    Raises:
        The last exception encountered if all retries fail
    """
    config = retry_config or RetryConfig()
    last_error = None
    
    for attempt in range(config.max_retries + 1):  # +1 for initial attempt
        try:
            result = func(*args, **kwargs)
            return result
            
        except Exception as error:
            last_error = error
            
            # Check if we should retry
            if attempt >= config.max_retries:
                logger.error(f"Operation failed after {config.max_retries + 1} attempts: {error}")
                break
            
            if not config.is_retryable(error):
                logger.error(f"Non-retryable error encountered: {error}")
                break
            
            # Calculate delay and wait
            delay = config.get_delay(attempt)
            logger.warning(
                f"Retryable error in attempt {attempt + 1}/{config.max_retries + 1}: {error}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            import time
            time.sleep(delay)
    
    # All retries failed
    if last_error:
        raise last_error
    else:
        raise RuntimeError("Unknown error occurred during retry execution") 