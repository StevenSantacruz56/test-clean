"""
Core Configuration.

Application configuration, logging, security, and constants.
Shared technical kernel.
"""

from app.core.config import settings, get_settings, Settings
from app.core.secret_manager import AWSConfigManager, get_config_manager

__all__ = [
    "settings",
    "get_settings",
    "Settings",
    "AWSConfigManager",
    "get_config_manager",
]
