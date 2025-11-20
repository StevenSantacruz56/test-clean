"""
Secret Manager Integration for AWS Secrets Manager.

This module provides functionality to fetch secrets from AWS Secrets Manager
for testing, staging, and production environments.
"""

from typing import Optional, Dict, Any
import os
import json
import logging
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class AWSSecretsManagerClient:
    """Client for accessing AWS Secrets Manager."""

    def __init__(
        self,
        region_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Initialize AWS Secrets Manager client.

        Args:
            region_name: AWS region name. If not provided, will be read from AWS_REGION or AWS_DEFAULT_REGION env var.
            aws_access_key_id: AWS access key ID. If not provided, will use default AWS credentials chain.
            aws_secret_access_key: AWS secret access key. If not provided, will use default AWS credentials chain.
        """
        self.region_name = region_name or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self._client: Optional[boto3.client] = None
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

    @property
    def client(self) -> boto3.client:
        """Lazy initialization of Secrets Manager client."""
        if self._client is None:
            session_kwargs = {"region_name": self.region_name}

            # Only add credentials if explicitly provided
            # Otherwise, use default AWS credentials chain (IAM roles, env vars, etc.)
            if self._aws_access_key_id and self._aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = self._aws_access_key_id
                session_kwargs["aws_secret_access_key"] = self._aws_secret_access_key

            self._client = boto3.client("secretsmanager", **session_kwargs)
        return self._client

    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Fetch a secret from AWS Secrets Manager.

        Args:
            secret_name: Name or ARN of the secret to fetch

        Returns:
            Secret value as string, or None if not found

        Example:
            >>> sm = AWSSecretsManagerClient(region_name="us-east-1")
            >>> db_password = sm.get_secret("production-database-password")
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)

            # Depending on whether the secret is a string or binary, return the appropriate value
            if "SecretString" in response:
                secret_value = response["SecretString"]
                logger.info(f"Successfully fetched secret: {secret_name}")
                return secret_value
            else:
                # Binary secrets (base64 encoded)
                secret_value = response["SecretBinary"].decode("utf-8")
                logger.info(f"Successfully fetched binary secret: {secret_name}")
                return secret_value

        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "ResourceNotFoundException":
                logger.warning(f"Secret not found: {secret_name}")
            elif error_code == "InvalidRequestException":
                logger.error(f"Invalid request for secret {secret_name}: {e}")
            elif error_code == "InvalidParameterException":
                logger.error(f"Invalid parameter for secret {secret_name}: {e}")
            elif error_code == "DecryptionFailure":
                logger.error(f"Decryption failed for secret {secret_name}: {e}")
            elif error_code == "InternalServiceError":
                logger.error(f"AWS internal service error for secret {secret_name}: {e}")
            else:
                logger.error(f"Error fetching secret {secret_name}: {e}")

            return None

        except BotoCoreError as e:
            logger.error(f"BotoCore error fetching secret {secret_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching secret {secret_name}: {e}")
            return None

    def get_secret_json(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a secret from AWS Secrets Manager and parse it as JSON.

        This is useful for secrets that contain multiple key-value pairs.

        Args:
            secret_name: Name or ARN of the secret to fetch

        Returns:
            Secret value as dictionary, or None if not found or invalid JSON

        Example:
            >>> sm = AWSSecretsManagerClient()
            >>> db_config = sm.get_secret_json("production-database-config")
            >>> print(db_config["username"])
        """
        secret_value = self.get_secret(secret_name)

        if not secret_value:
            return None

        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse secret {secret_name} as JSON: {e}")
            return None

    def get_secret_or_env(
        self,
        secret_name: str,
        env_var_name: str,
        default: Optional[str] = None
    ) -> Optional[str]:
        """
        Try to get secret from Secrets Manager, fallback to environment variable, then default.

        This is useful for local development where you might not have access to Secrets Manager.

        Args:
            secret_name: Name of the secret in Secrets Manager
            env_var_name: Name of the environment variable to use as fallback
            default: Default value if neither secret nor env var is found

        Returns:
            Secret value, environment variable value, or default value

        Example:
            >>> sm = AWSSecretsManagerClient()
            >>> db_url = sm.get_secret_or_env(
            ...     "production-database-url",
            ...     "DATABASE_URL",
            ...     "postgresql://localhost/db"
            ... )
        """
        # Try Secrets Manager first (for production/staging/testing)
        secret = self.get_secret(secret_name)
        if secret:
            return secret

        # Fallback to environment variable (for local development)
        env_value = os.getenv(env_var_name)
        if env_value:
            logger.info(f"Using environment variable {env_var_name} (Secrets Manager not available)")
            return env_value

        # Use default value
        if default:
            logger.info(f"Using default value for {secret_name}/{env_var_name}")
        return default

    def list_secrets(self) -> list:
        """
        List all secrets in the current AWS account and region.

        Returns:
            List of secret metadata dictionaries

        Example:
            >>> sm = AWSSecretsManagerClient()
            >>> secrets = sm.list_secrets()
            >>> for secret in secrets:
            ...     print(secret['Name'])
        """
        try:
            response = self.client.list_secrets()
            return response.get("SecretList", [])
        except Exception as e:
            logger.error(f"Error listing secrets: {e}")
            return []


def get_secrets_manager() -> Optional[AWSSecretsManagerClient]:
    """
    Factory function to create AWSSecretsManagerClient.

    Returns None if in local/development environment.

    Returns:
        AWSSecretsManagerClient instance or None

    Example:
        >>> sm = get_secrets_manager()
        >>> if sm:
        ...     db_password = sm.get_secret("production-db-password")
    """
    environment = os.getenv("ENVIRONMENT", "development")

    if environment.lower() in ("development", "local"):
        logger.info("Running in development/local mode. AWS Secrets Manager disabled.")
        return None

    return AWSSecretsManagerClient()
