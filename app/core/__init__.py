"""
Core Configuration.

Application configuration, logging, security, and constants.
Shared technical kernel.
"""

from app.core.config import settings, get_settings, Settings, SettingsWithSecretsManager
from app.core.secret_manager import AWSSecretsManagerClient, get_secrets_manager

__all__ = [
    "settings",
    "get_settings",
    "Settings",
    "SettingsWithSecretsManager",
    "AWSSecretsManagerClient",
    "get_secrets_manager",
]
