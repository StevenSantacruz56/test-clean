"""
Core Configuration.

Application configuration, logging, security, and constants.
Shared technical kernel.
"""

from app.core.config import settings, get_settings, Settings, SettingsWithSecretManager
from app.core.secret_manager import SecretManagerClient, get_secret_manager

__all__ = [
    "settings",
    "get_settings",
    "Settings",
    "SettingsWithSecretManager",
    "SecretManagerClient",
    "get_secret_manager",
]
