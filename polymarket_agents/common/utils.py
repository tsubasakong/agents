"""
Shared utility functions for Polymarket Agents.

This module provides common utilities that are used across the application,
extracted from various modules to reduce code duplication.
"""

import math
from typing import List, Dict, Any, Union


def retain_keys(data: Union[Dict, List], keys_to_retain: List[str]) -> Union[Dict, List]:
    """
    Recursively retain only specified keys from nested dictionaries and lists.
    
    Args:
        data: The data structure to filter (dict or list)
        keys_to_retain: List of keys to keep in dictionaries
        
    Returns:
        Filtered data structure with only retained keys
    """
    if isinstance(data, dict):
        return {
            key: retain_keys(value, keys_to_retain)
            for key, value in data.items()
            if key in keys_to_retain
        }
    elif isinstance(data, list):
        return [retain_keys(item, keys_to_retain) for item in data]
    else:
        return data


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    
    This is a rough estimate using the rule of thumb that 1 token ≈ 4 characters.
    For more accurate results, consider using a proper tokenizer.
    
    Args:
        text: The text to estimate tokens for
        
    Returns:
        Estimated number of tokens
    """
    return len(text) // 4


def divide_list(original_list: List[Any], num_parts: int) -> List[List[Any]]:
    """
    Divide a list into a specified number of roughly equal parts.
    
    Args:
        original_list: The list to divide
        num_parts: Number of parts to divide into
        
    Returns:
        List of sublists, each containing roughly equal parts of the original
    """
    if num_parts <= 0:
        raise ValueError("num_parts must be greater than 0")
    
    if not original_list:
        return [[] for _ in range(num_parts)]
    
    # Calculate the size of each sublist
    sublist_size = math.ceil(len(original_list) / num_parts)
    
    # Use list comprehension to create sublists
    return [
        original_list[i:i + sublist_size] 
        for i in range(0, len(original_list), sublist_size)
    ]


def validate_required_env_vars(required_vars: List[str], env_dict: Dict[str, str]) -> List[str]:
    """
    Validate that required environment variables are present and not empty.
    
    Args:
        required_vars: List of required environment variable names
        env_dict: Dictionary of environment variables (usually from os.environ)
        
    Returns:
        List of missing or empty environment variable names
    """
    missing_vars = []
    
    for var in required_vars:
        if var not in env_dict or not env_dict[var] or env_dict[var].strip() == "":
            missing_vars.append(var)
    
    return missing_vars


def safe_float_parse(value: str, default: float = 0.0) -> float:
    """
    Safely parse a string to float, returning default if parsing fails.
    
    Args:
        value: String value to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int_parse(value: str, default: int = 0) -> int:
    """
    Safely parse a string to int, returning default if parsing fails.
    
    Args:
        value: String value to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed int value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default 