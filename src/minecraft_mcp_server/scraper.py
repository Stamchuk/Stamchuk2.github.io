"""Documentation scraper for Minecraft MCP Server."""

import logging
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .exceptions import NetworkError, ParsingError

logger = logging.getLogger(__name__)


class DocumentationScraper:
    """Scrapes and processes documentation from various sources.
    
    This class handles fetching and parsing documentation from:
    - Paper MC (docs.papermc.io)
    - Leaf MC (www.leafmc.one)
    - Purpur MC (purpurmc.org)
    - Minecraft Wiki (minecraft.wiki)
    
    Attributes:
        timeout: HTTP request timeout in seconds.
        max_content_length: Maximum content length in characters.
        client: Async HTTP client for making requests.
    """

    def __init__(self, timeout: int = 30, max_content_length: int = 10000) -> None:
        """Initialize the documentation scraper.
        
        Args:
            timeout: HTTP request timeout in seconds.
            max_content_length: Maximum content length in characters.
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "MinecraftMCPServer/1.0",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            },
        )
        logger.debug(
            f"DocumentationScraper initialized: timeout={timeout}s, "
            f"max_length={max_content_length}"
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def _fetch_url(self, url: str) -> str:
        """Fetch content from URL.
        
        Args:
            url: URL to fetch.
            
        Returns:
            HTML content as string.
            
        Raises:
            NetworkError: If the request fails.
        """
        try:
            logger.info(f"Fetching URL: {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching {url}: {e}")
            raise NetworkError(f"Request timed out after {self.timeout} seconds") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
            raise NetworkError(
                f"HTTP {e.response.status_code} error: {e.response.reason_phrase}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error fetching {url}: {e}")
            raise NetworkError(f"Network error: {str(e)}") from e

    def _extract_content(self, html: str, selectors: dict[str, str]) -> str:
        """Extract relevant content from HTML.
        
        Args:
            html: HTML content to parse.
            selectors: Dictionary of selector names to CSS selectors.
            
        Returns:
            Extracted and cleaned text content.
            
        Raises:
            ParsingError: If parsing fails.
        """
        try:
            soup = BeautifulSoup(html, "lxml")

            # Try each selector in order
            content_element = None
            for name, selector in selectors.items():
                content_element = soup.select_one(selector)
                if content_element:
                    logger.debug(f"Found content using selector: {name}")
                    break

            if not content_element:
                raise ParsingError(
                    f"Could not find content using selectors: {list(selectors.keys())}"
                )

            # Remove unwanted elements
            for unwanted in content_element.select("script, style, nav, footer, aside"):
                unwanted.decompose()

            # Extract text
            text = content_element.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            text = "\n".join(lines)

            # Truncate if necessary
            if len(text) > self.max_content_length:
                logger.warning(
                    f"Content truncated from {len(text)} to {self.max_content_length} chars"
                )
                text = text[: self.max_content_length] + "\n\n[Content truncated...]"

            return text

        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            raise ParsingError(f"Failed to parse HTML content: {str(e)}") from e

    async def fetch_paper_docs(self, section: Optional[str] = None) -> str:
        """Fetch Paper MC documentation.
        
        Args:
            section: Specific documentation section (optional).
            
        Returns:
            Documentation content as formatted text.
            
        Raises:
            NetworkError: If the request fails.
            ParsingError: If parsing fails.
        """
        base_url = "https://docs.papermc.io/paper"
        url = f"{base_url}/{section}" if section else base_url

        html = await self._fetch_url(url)

        selectors = {
            "main_content": "main",
            "article": "article",
            "content": ".content",
            "docs": ".docs-content",
        }

        content = self._extract_content(html, selectors)
        logger.info(f"Successfully fetched Paper docs: {len(content)} chars")
        return content

    async def fetch_leaf_docs(self, section: Optional[str] = None) -> str:
        """Fetch Leaf MC documentation.
        
        Args:
            section: Specific documentation section (optional).
            
        Returns:
            Documentation content as formatted text.
            
        Raises:
            NetworkError: If the request fails.
            ParsingError: If parsing fails.
        """
        base_url = "https://www.leafmc.one/ru"
        url = f"{base_url}/{section}" if section else base_url

        html = await self._fetch_url(url)

        selectors = {
            "main_content": "main",
            "article": "article",
            "content": ".content",
            "docs": ".docs-content",
        }

        content = self._extract_content(html, selectors)
        logger.info(f"Successfully fetched Leaf docs: {len(content)} chars")
        return content

    async def fetch_purpur_docs(self, section: Optional[str] = None) -> str:
        """Fetch Purpur MC documentation.
        
        Args:
            section: Specific documentation section (optional).
            
        Returns:
            Documentation content as formatted text.
            
        Raises:
            NetworkError: If the request fails.
            ParsingError: If parsing fails.
        """
        base_url = "https://purpurmc.org/docs/purpur"
        url = f"{base_url}/{section}" if section else base_url

        html = await self._fetch_url(url)

        selectors = {
            "main_content": "main",
            "article": "article",
            "content": ".content",
            "markdown": ".markdown-body",
        }

        content = self._extract_content(html, selectors)
        logger.info(f"Successfully fetched Purpur docs: {len(content)} chars")
        return content

    async def search_minecraft_wiki(self, query: str) -> str:
        """Search Minecraft Wiki for specific topic.
        
        Args:
            query: Search query (article name).
            
        Returns:
            Article content as formatted text.
            
        Raises:
            NetworkError: If the request fails.
            ParsingError: If parsing fails.
        """
        # Format query for URL (replace spaces with underscores)
        formatted_query = query.replace(" ", "_")
        url = f"https://minecraft.wiki/w/{formatted_query}"

        html = await self._fetch_url(url)

        selectors = {
            "content": "#mw-content-text",
            "parser_output": ".mw-parser-output",
            "main": "main",
        }

        content = self._extract_content(html, selectors)
        logger.info(f"Successfully fetched Minecraft Wiki article: {len(content)} chars")
        return content
