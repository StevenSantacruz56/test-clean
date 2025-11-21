"""
Secret Manager Integration for AWS Secrets Manager and SSM Parameter Store.

This module provides functionality to fetch:
- Complex/multiple secrets from AWS Secrets Manager (JSON format)
- Individual sensitive parameters from AWS Systems Manager Parameter Store (SSM)

Usage pattern:
- Secrets Manager: For JSON secrets with multiple key-value pairs
- Parameter Store: For individual sensitive configuration values
"""

import json
import logging
import os
from typing import Optional, Dict, Any

import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class AWSConfigManager:
    """
    Manager for AWS Secrets Manager and SSM Parameter Store.

    Handles both complex secrets (Secrets Manager) and individual parameters (Parameter Store).
    """

    def __init__(
        self,
        region_name: Optional[str] = None,
        service: Optional[str] = None,
        environment: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Initialize AWS Config Manager.

        Args:
            region_name: AWS region name (defaults to AWS_REGION or us-east-1)
            service: Service name for parameter store paths
            environment: Environment name (testing, staging, production)
            aws_access_key_id: AWS access key ID (optional, uses credentials chain if not provided)
            aws_secret_access_key: AWS secret access key (optional)
        """
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.service = service or os.getenv("SERVICE", "api")
        self.environment = environment or os.getenv("ENVIRONMENT", "testing")

        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

        self._secrets_manager_client: Optional[boto3.client] = None
        self._ssm_client: Optional[boto3.client] = None

    @property
    def secrets_manager_client(self) -> boto3.client:
        """Lazy initialization of Secrets Manager client."""
        if self._secrets_manager_client is None:
            session_kwargs = {"region_name": self.region_name}

            if self._aws_access_key_id and self._aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = self._aws_access_key_id
                session_kwargs["aws_secret_access_key"] = self._aws_secret_access_key

            self._secrets_manager_client = boto3.client("secretsmanager", **session_kwargs)

        return self._secrets_manager_client

    @property
    def ssm_client(self) -> boto3.client:
        """Lazy initialization of SSM Parameter Store client."""
        if self._ssm_client is None:
            session_kwargs = {"region_name": self.region_name}

            if self._aws_access_key_id and self._aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = self._aws_access_key_id
                session_kwargs["aws_secret_access_key"] = self._aws_secret_access_key

            self._ssm_client = boto3.client("ssm", **session_kwargs)

        return self._ssm_client

    def get_secret_key(self, secret_name: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Obtiene secretos desde AWS Secrets Manager (JSON format).

        Use this for complex secrets with multiple key-value pairs.

        Args:
            secret_name: Name of the secret (defaults to {service}/{environment})

        Returns:
            dict: Dictionary with secret key-value pairs or None if error

        Example:
            >>> manager = AWSConfigManager()
            >>> secrets = manager.get_secret_key()
            >>> print(secrets["database_url"])
        """
        if not secret_name:
            # Default pattern: service/environment (e.g., "api/testing", "api/production")
            secret_name = f"{self.service}/{self.environment}"

        try:
            logger.info(f"Fetching secret from Secrets Manager: {secret_name}")
            response = self.secrets_manager_client.get_secret_value(SecretId=secret_name)

            secret_value = response.get("SecretString")
            if secret_value:
                secrets_dict = json.loads(secret_value)
                logger.info(f"Successfully fetched secret: {secret_name}")
                return secrets_dict

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                logger.warning(f"Secret not found: {secret_name}")
            else:
                logger.error(f"Error fetching secret {secret_name}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse secret {secret_name} as JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching secret {secret_name}: {e}")

        return None

    def get_parameter(
        self,
        param: str,
        param_type: str = "default",
        fallback_env_var: bool = True
    ) -> Optional[str]:
        """
        Retrieves a parameter from AWS Systems Manager Parameter Store.

        Use this for individual sensitive configuration values.

        Args:
            param: Name of the parameter
            param_type: Type of parameter (default, static, global, static_env)
                - default: {environment}/{service}/{param}
                - Add more patterns as needed
            fallback_env_var: If True, falls back to environment variable if AWS call fails

        Returns:
            str: Value of the parameter or None if error

        Example:
            >>> manager = AWSConfigManager(environment="production", service="api")
            >>> postgres_host = manager.get_parameter("POSTGRES_HOST", "default")
            >>> # Fetches: production/api/POSTGRES_HOST
        """
        try:
            # Parameter name patterns
            param_mappings = {
                "default": f"{self.environment}/{self.service}/{param}",
                "static": f"static/{param}",
                "global": f"global/{param}",
                "static_env": f"static/{self.environment}/{param}",
            }

            param_name = param_mappings.get(param_type, param_mappings["default"])
            logger.info(f"Fetching SSM parameter: {param_name}")

            response = self.ssm_client.get_parameter(
                Name=param_name,
                WithDecryption=True
            )

            if "Parameter" in response and "Value" in response["Parameter"]:
                value = response["Parameter"]["Value"]
                logger.info(f"Successfully fetched parameter: {param_name}")
                return value
            else:
                logger.error(f"'Value' key missing in parameter response for: {param_name}")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ParameterNotFound":
                logger.warning(f"Parameter not found: {param_name}")
            else:
                logger.error(f"Error fetching parameter {param_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching parameter {param_name}: {e}")

        # Fallback to environment variable
        if fallback_env_var:
            env_value = os.getenv(param)
            if env_value:
                logger.info(f"Using environment variable fallback for: {param}")
                return env_value
            else:
                logger.warning(f"No fallback environment variable found for: {param}")

        return None

    def get_all_parameters_by_path(
        self,
        path: Optional[str] = None,
        recursive: bool = True
    ) -> Dict[str, str]:
        """
        Get all parameters under a specific path in Parameter Store.

        Args:
            path: Parameter path (defaults to /{environment}/{service}/)
            recursive: Whether to retrieve all parameters within the hierarchy

        Returns:
            dict: Dictionary of parameter names and values

        Example:
            >>> manager = AWSConfigManager()
            >>> params = manager.get_all_parameters_by_path()
            >>> # Returns all params under /testing/api/
        """
        if not path:
            path = f"/{self.environment}/{self.service}/"

        parameters = {}

        try:
            logger.info(f"Fetching all parameters from path: {path}")

            paginator = self.ssm_client.get_paginator("get_parameters_by_path")
            page_iterator = paginator.paginate(
                Path=path,
                Recursive=recursive,
                WithDecryption=True
            )

            for page in page_iterator:
                for param in page.get("Parameters", []):
                    # Extract parameter name (remove path prefix)
                    param_name = param["Name"].replace(path, "").lstrip("/")
                    parameters[param_name] = param["Value"]

            logger.info(f"Successfully fetched {len(parameters)} parameters from path: {path}")

        except Exception as e:
            logger.error(f"Error fetching parameters from path {path}: {e}")

        return parameters


def get_config_manager(
    environment: Optional[str] = None,
    service: Optional[str] = None
) -> Optional[AWSConfigManager]:
    """
    Factory function to create AWSConfigManager.

    Returns None if in local/localhost environment.

    Args:
        environment: Environment name (defaults to ENVIRONMENT env var)
        service: Service name (defaults to SERVICE env var)

    Returns:
        AWSConfigManager instance or None

    Example:
        >>> manager = get_config_manager()
        >>> if manager:
        ...     secrets = manager.get_secret_key()
    """
    env = environment or os.getenv("ENVIRONMENT", "localhost")

    if env.lower() in ("localhost", "local", "development"):
        logger.info("Running in local environment. AWS Config Manager disabled.")
        return None

    return AWSConfigManager(environment=env, service=service)
