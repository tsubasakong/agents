"""
Configuration management for Polymarket Agents.

This module provides centralized configuration management, replacing
scattered environment variable loading throughout the application.
"""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"] 