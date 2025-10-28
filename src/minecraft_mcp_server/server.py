"""Main FastMCP server for Minecraft documentation and APIs."""

import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .cache import CacheManager
from .config import get_config
from .exceptions import APIError, NetworkError, ParsingError
from .mojang_api import MojangAPIClient
from .scraper import DocumentationScraper

# Initialize configuration
config = get_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="Minecraft Documentation Server",
    instructions=(
        "Provides access to Minecraft server documentation (Paper, Leaf, Purpur), "
        "Minecraft Wiki articles, and Mojang API data for player profiles and server status."
    ),
)

# Initialize global components
cache = CacheManager(default_ttl=config.cache_ttl)
scraper = DocumentationScraper(
    timeout=config.request_timeout,
    max_content_length=config.max_content_length,
)
mojang_api = MojangAPIClient(timeout=config.request_timeout)

logger.info("Minecraft MCP Server initialized")


@mcp.tool()
async def get_paper_docs(section: Optional[str] = None, force_refresh: bool = False) -> str:
    """Get Paper MC documentation.

    Paper is a high-performance Minecraft server platform. This tool fetches
    the latest documentation from docs.papermc.io.

    Args:
        section: Specific documentation section to fetch (optional).
                 Example: "admin/reference/configuration"
        force_refresh: Force cache refresh, bypassing cached data.

    Returns:
        Documentation content as formatted text.
    """
    cache_key = f"paper:{section or 'index'}"

    # Check cache first (unless force_refresh)
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached Paper docs: {cache_key}")
            return cached

    try:
        # Fetch fresh documentation
        content = await scraper.fetch_paper_docs(section)
        
        # Cache the result
        cache.set(cache_key, content)
        
        return content

    except NetworkError as e:
        error_msg = f"Network error fetching Paper documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except ParsingError as e:
        error_msg = f"Failed to parse Paper documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error fetching Paper documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def get_leaf_docs(section: Optional[str] = None, force_refresh: bool = False) -> str:
    """Get Leaf MC documentation.

    Leaf is a Paper fork with additional optimizations. This tool fetches
    documentation from www.leafmc.one (Russian locale).

    Args:
        section: Specific documentation section to fetch (optional).
        force_refresh: Force cache refresh, bypassing cached data.

    Returns:
        Documentation content as formatted text.
    """
    cache_key = f"leaf:{section or 'index'}"

    # Check cache first (unless force_refresh)
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached Leaf docs: {cache_key}")
            return cached

    try:
        # Fetch fresh documentation
        content = await scraper.fetch_leaf_docs(section)
        
        # Cache the result
        cache.set(cache_key, content)
        
        return content

    except NetworkError as e:
        error_msg = f"Network error fetching Leaf documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except ParsingError as e:
        error_msg = f"Failed to parse Leaf documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error fetching Leaf documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def get_purpur_docs(section: Optional[str] = None, force_refresh: bool = False) -> str:
    """Get Purpur MC documentation.

    Purpur is a Paper fork with extensive configuration options. This tool
    fetches documentation from purpurmc.org.

    Args:
        section: Specific documentation section to fetch (optional).
                 Example: "configuration"
        force_refresh: Force cache refresh, bypassing cached data.

    Returns:
        Documentation content as formatted text.
    """
    cache_key = f"purpur:{section or 'index'}"

    # Check cache first (unless force_refresh)
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached Purpur docs: {cache_key}")
            return cached

    try:
        # Fetch fresh documentation
        content = await scraper.fetch_purpur_docs(section)
        
        # Cache the result
        cache.set(cache_key, content)
        
        return content

    except NetworkError as e:
        error_msg = f"Network error fetching Purpur documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except ParsingError as e:
        error_msg = f"Failed to parse Purpur documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error fetching Purpur documentation: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def search_minecraft_wiki(query: str) -> str:
    """Search Minecraft Wiki for articles.

    Searches the official Minecraft Wiki (minecraft.wiki) for articles
    about game mechanics, blocks, items, mobs, and more.

    Args:
        query: Search query or article name.
               Example: "Diamond", "Redstone", "Creeper"

    Returns:
        Article content as formatted text.
    """
    cache_key = f"wiki:{query.lower()}"

    # Check cache first
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"Returning cached Wiki article: {cache_key}")
        return cached

    try:
        # Fetch article
        content = await scraper.search_minecraft_wiki(query)
        
        # Cache the result
        cache.set(cache_key, content)
        
        return content

    except NetworkError as e:
        error_msg = f"Network error searching Minecraft Wiki: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except ParsingError as e:
        error_msg = f"Failed to parse Minecraft Wiki article: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error searching Minecraft Wiki: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def get_player_profile(username: str) -> str:
    """Get Minecraft player profile from Mojang API.

    Retrieves player information including UUID and profile data from
    Mojang's official API.

    Args:
        username: Minecraft player username (3-16 alphanumeric characters).
                  Example: "Notch", "jeb_"

    Returns:
        Player profile information as formatted text.
    """
    cache_key = f"player:{username.lower()}"

    # Check cache first
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"Returning cached player profile: {cache_key}")
        return cached

    try:
        # Get UUID first
        uuid_data = await mojang_api.get_player_uuid(username)
        
        if not uuid_data:
            return f"Player '{username}' not found."

        player_uuid = uuid_data.get("id")
        player_name = uuid_data.get("name")

        # Get full profile
        profile_data = await mojang_api.get_player_profile(player_uuid)

        if not profile_data:
            result = f"Player: {player_name}\nUUID: {player_uuid}\n\nProfile data not available."
        else:
            # Format profile information
            result = f"Player: {player_name}\nUUID: {player_uuid}\n\n"
            
            if "properties" in profile_data:
                result += "Profile Properties:\n"
                for prop in profile_data["properties"]:
                    result += f"  - {prop.get('name', 'unknown')}\n"

        # Cache the result
        cache.set(cache_key, result)
        
        return result

    except APIError as e:
        error_msg = f"Mojang API error: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except NetworkError as e:
        error_msg = f"Network error accessing Mojang API: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error fetching player profile: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def get_server_status() -> str:
    """Check Mojang services status.

    Checks the status of Mojang's API services to determine if they are
    online, degraded, or offline.

    Returns:
        Status information for Mojang services.
    """
    cache_key = "mojang:status"

    # Check cache first (shorter TTL for status)
    cached = cache.get(cache_key)
    if cached:
        logger.info("Returning cached Mojang status")
        return cached

    try:
        # Get service status
        status_data = await mojang_api.get_server_status()

        # Format status information
        result = "Mojang Services Status:\n\n"
        for service, status in status_data.items():
            status_emoji = {
                "online": "✓",
                "degraded": "⚠",
                "offline": "✗",
            }.get(status, "?")
            
            result += f"{status_emoji} {service}: {status.upper()}\n"

        # Cache with shorter TTL (5 minutes)
        cache.set(cache_key, result, ttl=300)
        
        return result

    except NetworkError as e:
        error_msg = f"Network error checking Mojang status: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error checking Mojang status: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def main() -> None:
    """Main entry point for the MCP server."""
    logger.info("Starting Minecraft MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
