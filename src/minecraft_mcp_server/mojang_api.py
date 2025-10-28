"""Mojang API client for Minecraft MCP Server."""

import logging
from typing import Optional

import httpx

from .exceptions import APIError, NetworkError

logger = logging.getLogger(__name__)


class MojangAPIClient:
    """Client for Mojang API interactions.
    
    This client handles communication with Mojang's official APIs:
    - Player UUID lookup
    - Player profile retrieval
    - Service status checking
    
    Attributes:
        BASE_URL: Base URL for Mojang API.
        SESSION_URL: Base URL for session server API.
        timeout: HTTP request timeout in seconds.
        client: Async HTTP client for making requests.
    """

    BASE_URL = "https://api.mojang.com"
    SESSION_URL = "https://sessionserver.mojang.com"

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the Mojang API client.
        
        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "MinecraftMCPServer/1.0",
                "Accept": "application/json",
            },
        )
        logger.debug(f"MojangAPIClient initialized: timeout={timeout}s")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_player_uuid(self, username: str) -> Optional[dict[str, str]]:
        """Get player UUID by username.
        
        Args:
            username: Minecraft player username.
            
        Returns:
            Dictionary with 'id' (UUID) and 'name' fields, or None if not found.
            
        Raises:
            APIError: If the API request fails.
            NetworkError: If the network request fails.
        """
        if not username or not username.strip():
            raise APIError("Username cannot be empty")

        # Validate username format (alphanumeric and underscore, 3-16 chars)
        if not username.replace("_", "").isalnum() or not (3 <= len(username) <= 16):
            raise APIError(
                f"Invalid username format: '{username}'. "
                "Must be 3-16 alphanumeric characters or underscores."
            )

        url = f"{self.BASE_URL}/users/profiles/minecraft/{username}"

        try:
            logger.info(f"Fetching UUID for username: {username}")
            response = await self.client.get(url)

            if response.status_code == 404:
                logger.warning(f"Player not found: {username}")
                return None

            if response.status_code == 429:
                logger.error("Rate limit exceeded for Mojang API")
                raise APIError(
                    "Rate limit exceeded. Please try again later. "
                    "Mojang API allows max 600 requests per 10 minutes."
                )

            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched UUID for {username}: {data.get('id')}")
            return data

        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching UUID for {username}: {e}")
            raise NetworkError(f"Request timed out after {self.timeout} seconds") from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise APIError("Rate limit exceeded") from e
            logger.error(f"HTTP error fetching UUID: {e.response.status_code}")
            raise APIError(
                f"Mojang API error: HTTP {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error fetching UUID: {e}")
            raise NetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error fetching UUID: {e}")
            raise APIError(f"Unexpected error: {str(e)}") from e

    async def get_player_profile(self, uuid: str) -> Optional[dict[str, any]]:
        """Get player profile by UUID.
        
        Args:
            uuid: Player UUID (with or without dashes).
            
        Returns:
            Dictionary with profile data including properties, or None if not found.
            
        Raises:
            APIError: If the API request fails.
            NetworkError: If the network request fails.
        """
        # Remove dashes from UUID if present
        clean_uuid = uuid.replace("-", "")

        # Validate UUID format (32 hex characters)
        if len(clean_uuid) != 32 or not all(c in "0123456789abcdefABCDEF" for c in clean_uuid):
            raise APIError(f"Invalid UUID format: '{uuid}'")

        url = f"{self.SESSION_URL}/session/minecraft/profile/{clean_uuid}"

        try:
            logger.info(f"Fetching profile for UUID: {clean_uuid}")
            response = await self.client.get(url)

            if response.status_code == 404:
                logger.warning(f"Profile not found for UUID: {clean_uuid}")
                return None

            if response.status_code == 429:
                logger.error("Rate limit exceeded for Mojang API")
                raise APIError(
                    "Rate limit exceeded. Please try again later. "
                    "Mojang API allows max 600 requests per 10 minutes."
                )

            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched profile for UUID: {clean_uuid}")
            return data

        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching profile for {clean_uuid}: {e}")
            raise NetworkError(f"Request timed out after {self.timeout} seconds") from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise APIError("Rate limit exceeded") from e
            logger.error(f"HTTP error fetching profile: {e.response.status_code}")
            raise APIError(
                f"Mojang API error: HTTP {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error fetching profile: {e}")
            raise NetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error fetching profile: {e}")
            raise APIError(f"Unexpected error: {str(e)}") from e

    async def get_server_status(self) -> dict[str, str]:
        """Check Mojang services status.
        
        Returns:
            Dictionary with service names as keys and status as values.
            Status can be: "online", "degraded", or "offline".
            
        Raises:
            APIError: If the API request fails.
            NetworkError: If the network request fails.
        """
        # Note: Mojang's status API endpoint has changed over time
        # We'll check multiple services by attempting to reach them
        services = {
            "api.mojang.com": f"{self.BASE_URL}/",
            "sessionserver.mojang.com": f"{self.SESSION_URL}/",
        }

        status_results: dict[str, str] = {}

        for service_name, service_url in services.items():
            try:
                logger.debug(f"Checking status of {service_name}")
                response = await self.client.get(service_url, timeout=10)
                
                if response.status_code < 500:
                    status_results[service_name] = "online"
                else:
                    status_results[service_name] = "degraded"
                    
            except httpx.TimeoutException:
                logger.warning(f"Timeout checking {service_name}")
                status_results[service_name] = "degraded"
            except httpx.RequestError:
                logger.warning(f"Error checking {service_name}")
                status_results[service_name] = "offline"

        logger.info(f"Service status check complete: {status_results}")
        return status_results
