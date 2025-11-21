"""
Centralized Settings Configuration.

This module provides centralized configuration management.
It supports loading configuration from:
1. .env files (for localhost/local development)
2. AWS Secrets Manager (for complex/JSON secrets in testing/staging/production)
3. AWS SSM Parameter Store (for individual sensitive values in testing/staging/production)

Environment-specific behavior:
- localhost/local: Uses .env file
- testing/staging/production: Uses AWS Secrets Manager + SSM Parameter Store
"""

from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
import os
import dotenv

from app.core.secret_manager import AWSConfigManager, get_config_manager

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings with support for multiple configuration sources.

    Configuration priority for localhost:
    1. .env file
    2. Environment variables
    3. Default values

    Configuration priority for testing/staging/production:
    1. AWS Secrets Manager (for JSON secrets)
    2. AWS SSM Parameter Store (for individual parameters)
    3. Environment variables (fallback)
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
        default="localhost",
        description="Environment: localhost, testing, staging, production"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Service
    service: str = Field(default="api", description="Service name for AWS Parameter Store")
    country: str = Field(default="MX", description="Country code")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database PostgreSQL
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/testclean",
        description="PostgreSQL connection URL"
    )
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_user: str = Field(default="postgres", description="PostgreSQL user")
    postgres_password: str = Field(default="postgres", description="PostgreSQL password")
    postgres_db: str = Field(default="testclean", description="PostgreSQL database name")
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")
    sql_debug: str = Field(default="False", description="SQL Debug mode")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
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
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Allowed CORS origins (comma-separated)"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: str = Field(default="*", description="Allowed HTTP methods")
    cors_allow_headers: str = Field(default="*", description="Allowed HTTP headers")

    # Cache
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    cache_enabled: bool = Field(default=True, description="Enable caching")

    # AWS Configuration
    aws_region: str = Field(default="us-east-1", description="AWS Region")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS Secret Access Key")

    # Event Bus
    event_bus_enabled: bool = Field(default=True, description="Enable event bus")
    event_bus_async: bool = Field(default=True, description="Use async event handlers")

    def __init__(self, **kwargs):
        """
        Initialize settings with environment-specific loading.

        For localhost: loads from .env
        For other environments: loads from AWS Secrets Manager + SSM Parameter Store
        """
        super().__init__(**kwargs)

        # Load configuration based on environment
        if self.is_localhost():
            self._load_from_env()
        else:
            self._load_from_aws()

    def _load_from_env(self):
        """Load configuration from .env file for localhost/local environment."""
        logger.info("Loading configuration from .env file (localhost mode)")
        dotenv.load_dotenv(".env")

        # All values are loaded automatically by Pydantic from environment variables
        logger.info("Configuration loaded from .env file")

    def _load_from_aws(self):
        """
        Load configuration from AWS Secrets Manager + SSM Parameter Store.

        Pattern:
        - Secrets Manager: For JSON secrets (multiple related values)
        - SSM Parameter Store: For individual sensitive parameters
        """
        logger.info(f"Loading configuration from AWS for environment: {self.environment}")

        # Create AWS config manager
        config_manager = AWSConfigManager(
            region_name=self.aws_region,
            service=self.service,
            environment=self.environment,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

        # 1. Load JSON secrets from Secrets Manager (optional, for complex configs)
        secrets = config_manager.get_secret_key()
        if secrets:
            logger.info(f"Loaded {len(secrets)} secrets from Secrets Manager")

            # Apply secrets to settings
            for key, value in secrets.items():
                key_upper = key.upper()
                if hasattr(self, key.lower()):
                    setattr(self, key.lower(), value)
                    logger.debug(f"Set {key.lower()} from Secrets Manager")

        # 2. Load individual sensitive parameters from SSM Parameter Store
        sensitive_params = [
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "REDIS_HOST",
            "REDIS_PORT",
            "SECRET_KEY",
        ]

        for param in sensitive_params:
            value = config_manager.get_parameter(param, param_type="default")
            if value:
                # Convert parameter name to lowercase attribute name
                attr_name = param.lower()
                if hasattr(self, attr_name):
                    # Convert to appropriate type
                    current_value = getattr(self, attr_name)
                    if isinstance(current_value, int):
                        setattr(self, attr_name, int(value))
                    elif isinstance(current_value, bool):
                        setattr(self, attr_name, value.lower() in ("true", "1", "yes"))
                    else:
                        setattr(self, attr_name, value)

                    logger.debug(f"Set {attr_name} from SSM Parameter Store")

        # 3. Build composite URLs from individual parameters
        if hasattr(self, 'postgres_host') and hasattr(self, 'postgres_user'):
            self.database_url = (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
            logger.info("Built database_url from SSM parameters")

        if hasattr(self, 'redis_host'):
            self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
            logger.info("Built redis_url from SSM parameters")

        logger.info("Configuration loaded from AWS")

    def is_localhost(self) -> bool:
        """Check if running in localhost/local mode."""
        return self.environment.lower() in ("localhost", "local", "development")

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment.lower() == "testing"

    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.environment.lower() == "staging"

    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins


def get_settings() -> Settings:
    """
    Factory function to create Settings instance.

    Returns:
        Settings instance with configuration loaded from appropriate source

    Example:
        >>> settings = get_settings()
        >>> print(settings.database_url)
    """
    environment = os.getenv("ENVIRONMENT", "localhost").lower()
    logger.info(f"Initializing settings for environment: {environment}")

    return Settings()


# Global settings instance
# Import and use this throughout the application
settings = get_settings()
