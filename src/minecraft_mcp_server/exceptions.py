"""Custom exceptions for Minecraft MCP Server."""


class MCPServerError(Exception):
    """Base exception for all MCP server errors.
    
    All custom exceptions in the Minecraft MCP Server should inherit
    from this base class to allow for easy exception handling.
    """

    pass


class NetworkError(MCPServerError):
    """Network-related errors.
    
    Raised when network operations fail, including:
    - Connection timeouts
    - DNS resolution failures
    - SSL/TLS errors
    - Connection refused errors
    """

    pass


class ParsingError(MCPServerError):
    """Content parsing errors.
    
    Raised when HTML or data parsing fails, including:
    - Invalid HTML structure
    - Missing expected elements
    - Encoding issues
    - Malformed data
    """

    pass


class APIError(MCPServerError):
    """External API errors.
    
    Raised when external API calls fail, including:
    - Invalid username/UUID
    - Rate limiting (429 responses)
    - API unavailable (5xx errors)
    - Authentication failures
    """

    pass
