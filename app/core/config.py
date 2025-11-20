"""
Centralized Settings Configuration.

This module provides centralized configuration management using Pydantic Settings.
It supports loading configuration from:
1. Environment variables
2. .env files (for local development)
3. AWS Secrets Manager (for testing/staging/production)

Environment-specific behavior:
- development/local: Uses .env file and environment variables
- testing/staging/production: Uses AWS Secrets Manager with env var fallback
"""

from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
import os

from app.core.secret_manager import AWSSecretsManagerClient

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings with support for multiple configuration sources.

    Configuration priority (highest to lowest):
    1. Environment variables
    2. AWS Secrets Manager (for testing/staging/production)
    3. .env file
    4. Default values
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="test-clean", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(
        default="development",
        description="Environment: development, testing, staging, production"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database PostgreSQL
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/testclean",
        description="PostgreSQL connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_decode_responses: bool = Field(default=True, description="Decode Redis responses to strings")
    redis_max_connections: int = Field(default=10, description="Max Redis connections")

    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for JWT and encryption"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: List[str] = Field(default=["*"], description="Allowed HTTP methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="Allowed HTTP headers")

    # Cache
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    cache_enabled: bool = Field(default=True, description="Enable caching")

    # AWS Configuration
    aws_region: Optional[str] = Field(default=None, description="AWS Region")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS Secret Access Key")

    # Event Bus
    event_bus_enabled: bool = Field(default=True, description="Enable event bus")
    event_bus_async: bool = Field(default=True, description="Use async event handlers")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v):
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "local", "testing", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {', '.join(allowed)}")
        return v.lower()

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment in ("development", "local")

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.environment == "staging"


class SettingsWithSecretsManager(Settings):
    """
    Extended Settings that loads secrets from AWS Secrets Manager.

    This is used for testing, staging, and production environments.
    For local development, use the base Settings class.
    """

    def __init__(self, **kwargs):
        """
        Initialize settings with AWS Secrets Manager integration.

        Secrets are loaded from Secrets Manager with fallback to environment variables.
        """
        super().__init__(**kwargs)

        # Only use Secrets Manager in non-development environments
        if not self.is_development():
            self._load_secrets_from_secrets_manager()

    def _load_secrets_from_secrets_manager(self):
        """Load sensitive configuration from AWS Secrets Manager."""
        logger.info(f"Loading secrets from AWS Secrets Manager for environment: {self.environment}")

        sm = AWSSecretsManagerClient(
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

        # Mapping of secret names to setting attributes
        # Pattern: {environment}-{secret-name}
        secret_mapping = {
            # Database
            f"{self.environment}/database-url": "database_url",

            # Redis
            f"{self.environment}/redis-url": "redis_url",

            # Security
            f"{self.environment}/secret-key": "secret_key",
        }

        for secret_name, attr_name in secret_mapping.items():
            # Get current value as fallback
            current_value = getattr(self, attr_name)

            # Try to fetch from Secrets Manager
            secret_value = sm.get_secret(secret_name)

            if secret_value:
                setattr(self, attr_name, secret_value)
                logger.info(f"Loaded {attr_name} from AWS Secrets Manager")
            else:
                logger.warning(
                    f"Could not load {secret_name} from AWS Secrets Manager. "
                    f"Using {'environment variable' if current_value else 'default value'}"
                )

    def load_secrets_from_json(self, secret_name: str):
        """
        Load multiple configuration values from a single JSON secret.

        This is useful when you store all your configuration in one JSON secret.

        Args:
            secret_name: Name of the JSON secret containing multiple key-value pairs

        Example:
            Secret in AWS: "production/app-config"
            Content: {"database_url": "postgresql://...", "redis_url": "redis://...", "secret_key": "..."}
        """
        logger.info(f"Loading JSON secret: {secret_name}")

        sm = AWSSecretsManagerClient(
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

        secret_dict = sm.get_secret_json(secret_name)

        if not secret_dict:
            logger.warning(f"Could not load JSON secret: {secret_name}")
            return

        # Update settings with values from JSON secret
        for key, value in secret_dict.items():
            # Convert key to lowercase to match Pydantic field names
            field_name = key.lower()

            if hasattr(self, field_name):
                setattr(self, field_name, value)
                logger.info(f"Loaded {field_name} from JSON secret")
            else:
                logger.warning(f"Unknown configuration key in JSON secret: {key}")


def get_settings() -> Settings:
    """
    Factory function to create appropriate Settings instance.

    Returns:
        Settings instance (with or without AWS Secrets Manager based on environment)

    Example:
        >>> settings = get_settings()
        >>> print(settings.database_url)
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment in ("development", "local"):
        logger.info("Loading settings for development/local environment")
        return Settings()
    else:
        logger.info(f"Loading settings for {environment} environment with AWS Secrets Manager")
        return SettingsWithSecretsManager()


# Global settings instance
# Import and use this throughout the application
settings = get_settings()
