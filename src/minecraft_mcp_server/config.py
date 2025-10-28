"""Configuration management for Minecraft MCP Server."""

import logging
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class ServerConfig(BaseSettings):
    """Server configuration from environment variables.
    
    All settings can be configured via environment variables with the
    MINECRAFT_MCP_ prefix. For example, to set cache_ttl, use:
    MINECRAFT_MCP_CACHE_TTL=7200
    """

    model_config = SettingsConfigDict(
        env_prefix="MINECRAFT_MCP_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Cache settings
    cache_ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds",
        ge=0,
    )

    # HTTP settings
    request_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
        ge=1,
        le=300,
    )

    max_content_length: int = Field(
        default=10000,
        description="Maximum content length in characters",
        ge=1000,
        le=100000,
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # API settings
    user_agent: str = Field(
        default="MinecraftMCPServer/1.0",
        description="User agent for HTTP requests",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level."""
        v_upper = v.upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        if v_upper not in valid_levels:
            logger.warning(
                f"Invalid log level '{v}'. Using 'INFO'. "
                f"Valid levels: {', '.join(valid_levels)}"
            )
            return "INFO"
        
        return v_upper

    @field_validator("cache_ttl")
    @classmethod
    def validate_cache_ttl(cls, v: int) -> int:
        """Validate cache TTL and log warnings."""
        if v < 0:
            logger.warning(f"Invalid cache_ttl '{v}'. Using default 3600 seconds.")
            return 3600
        
        if v > 86400:  # 24 hours
            logger.warning(
                f"Cache TTL of {v} seconds is very high (>24 hours). "
                "This may lead to stale data."
            )
        
        return v

    @field_validator("request_timeout")
    @classmethod
    def validate_request_timeout(cls, v: int) -> int:
        """Validate request timeout and log warnings."""
        if v < 1:
            logger.warning(f"Invalid request_timeout '{v}'. Using default 30 seconds.")
            return 30
        
        if v > 300:  # 5 minutes
            logger.warning(
                f"Request timeout of {v} seconds is very high (>5 minutes). "
                "This may cause long waits."
            )
        
        return v


# Global configuration instance
_config: Optional[ServerConfig] = None


def get_config() -> ServerConfig:
    """Get the global server configuration instance.
    
    Returns:
        ServerConfig: The configuration instance.
    """
    global _config
    
    if _config is None:
        _config = ServerConfig()
        logger.info(
            f"Configuration loaded: cache_ttl={_config.cache_ttl}s, "
            f"request_timeout={_config.request_timeout}s, "
            f"log_level={_config.log_level}"
        )
    
    return _config
