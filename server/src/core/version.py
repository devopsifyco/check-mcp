"""Version management module for DevOpsify MCP server.

This module provides tools for managing component versions, including:
- Getting current version information
- Getting version history
- Creating new versions
- Updating existing versions
- Getting all components with filtering and pagination
"""

from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import Context
from core.config import Config
import aiohttp
import json
from datetime import datetime

class VersionError(Exception):
    """Base exception for version management errors."""
    pass

class VersionAPIError(VersionError):
    """Exception raised when API calls fail."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")

async def _make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make an HTTP request to the version API.
    
    Args:
        method: HTTP method (GET, POST, PUT)
        endpoint: API endpoint
        params: Query parameters
        json_data: JSON payload for POST/PUT requests
        
    Returns:
        Dict[str, Any]: JSON response from the API
        
    Raises:
        VersionAPIError: If the API request fails
    """
    headers = {
        "Content-Type": "application/json",
        "apikey": Config.api.api_key
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{Config.api.base_url}{endpoint}",
                params=params,
                json=json_data,
                headers=headers
            ) as response:
                if response.status >= 400:
                    raise VersionAPIError(response.status, await response.text())
                return await response.json()
    except aiohttp.ClientError as e:
        raise VersionError(f"Network error: {str(e)}")
    except json.JSONDecodeError as e:
        raise VersionError(f"Invalid JSON response: {str(e)}")

async def get_latest_version(ctx: Context, product_name: str, vendor: Optional[str] = None) -> str:
    """Get the latest version information for a product.
    
    Args:
        ctx: MCP context
        product_name: Product name (e.g., "nginx")
        vendor: Optional vendor name to filter by
        
    Returns:
        str: JSON with latest version details
    """
    try:
        # Build the endpoint with optional vendor parameter
        endpoint = f"{Config.api.release_endpoint}/{product_name}/latest"
        if vendor:
            endpoint = f"{endpoint}?vendor={vendor}"
            
        data = await _make_request(
            "GET",
            endpoint
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def get_versions(ctx: Context, product_name: str, vendor: Optional[str] = None) -> str:
    """Get all versions for a product.
    
    Args:
        ctx: MCP context
        product_name: Product name (e.g., "nginx")
        vendor: Optional vendor name to filter by
        
    Returns:
        str: JSON array of version entries for the product
    """
    try:
        # Build the endpoint with optional vendor parameter
        endpoint = f"{Config.api.release_endpoint}/{product_name}"
        if vendor:
            endpoint = f"{endpoint}?vendor={vendor}"
            
        data = await _make_request(
            "GET",
            endpoint
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def get_specific_version(
    ctx: Context,
    product_name: str,
    version: str,
    vendor: Optional[str] = None
) -> str:
    """Get a specific version of a product.
    
    Args:
        ctx: MCP context
        product_name: Product name (e.g., "nginx")
        version: Specific version to retrieve (e.g., "1.0.0"). Must be a string.
        vendor: Optional vendor name to filter by
        
    Returns:
        str: JSON with specific version details
        
    Example:
        # Correct usage:
        get_specific_version(ctx, "istio", "1.23")
        get_specific_version(ctx, "nginx", "1.0.0", vendor="NGINX Inc")
        
        # Incorrect usage:
        get_specific_version(ctx, "istio", 1.23)  # Wrong: version must be a string
        
    Raises:
        TypeError: If version is not provided as a string
    """
    if not isinstance(version, str):
        raise TypeError("Version must be provided as a string, e.g., '1.23' not 1.23")
        
    try:
        # Build the endpoint with optional vendor parameter
        endpoint = f"{Config.api.release_endpoint}/{product_name}/{version}"
        if vendor:
            endpoint = f"{endpoint}?vendor={vendor}"
            
        data = await _make_request(
            "GET",
            endpoint
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def create_version(
    ctx: Context,
    product_name: str,
    version: str,
    release_date: str,
    active_support_end_date: str,
    security_support_end_date: str,
    eol_date: str
) -> str:
    """Create a new version entry for a product release.
    
    Args:
        ctx: MCP context
        product_name: Product name (e.g., "nginx")
        version: The specific semantic version identifier for this release (e.g., "1.0.0").
            **IMPORTANT:** 'version' must ALWAYS be passed as a string, not a number. For example, use "1.0.0" not 1.0 or 1.
        release_date: Date in YYYY-MM-DD format (e.g., "2024-04-15") or ISO 8601 datetime (e.g., "2024-04-15T00:00:00Z")
        active_support_end_date: Date in YYYY-MM-DD format or ISO 8601 datetime
        security_support_end_date: Date in YYYY-MM-DD format or ISO 8601 datetime
        eol_date: Date in YYYY-MM-DD format or ISO 8601 datetime
        
    Returns:
        str: JSON with created version details
        
    Example:
        # Correct usage (version as string):
        create_version(ctx, "nginx", "1.0.0", "2024-04-15", ...)
        create_version(ctx, "nginx", "1.0", "2024-04-15", ...)
        create_version(ctx, "nginx", "23", "2024-04-15", ...)
        create_version(ctx, "nginx", "1.0.0", "2024-04-15T00:00:00Z", ...)
        
        # Incorrect usage (version as number):
        create_version(ctx, "nginx", 1.0, "2024-04-15", ...)  # WRONG: version must be a string
        create_version(ctx, "nginx", 23, "2024-04-15", ...)   # WRONG: version must be a string
    
    WARNING:
        If you pass a number for 'version', it will cause an error. Always use quotes to ensure it is a string.
    """
    if not isinstance(version, str):
        raise TypeError("Version must be provided as a string, e.g., '1.23' not 1.23")
    try:
        data = await _make_request(
            "POST",
            f"{Config.api.release_endpoint}",
            json_data={
                "product_name": product_name,
                "version": version,
                "release_date": release_date,
                "active_support_end_date": active_support_end_date,
                "security_support_end_date": security_support_end_date,
                "eol_date": eol_date
            }
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def update_version(
    ctx: Context,
    product_name: str,
    version: str,
    release_date: str,
    active_support_end_date: str,
    security_support_end_date: str,
    eol_date: str
) -> str:
    """Update an existing version entry for a product release.
    
    Args:
        ctx: MCP context
        product_name: Product to update (e.g., "nginx") - identifier, cannot be changed
        version: The specific semantic version identifier to update (e.g., "1.0.0") - identifier, cannot be changed
        release_date: Date in YYYY-MM-DD format (e.g., "2024-04-15") or ISO 8601 datetime (e.g., "2024-04-15T00:00:00Z")
        active_support_end_date: Date in YYYY-MM-DD format or ISO 8601 datetime
        security_support_end_date: Date in YYYY-MM-DD format or ISO 8601 datetime
        eol_date: Date in YYYY-MM-DD format or ISO 8601 datetime
        
    Returns:
        str: JSON with updated version details
        
    Note:
        - product_name and version are identifiers used to locate the version to update.
          These values cannot be changed in an update operation.
        - Both simple date format (YYYY-MM-DD) and ISO 8601 datetime format are supported for all date fields.
    """
    if not isinstance(version, str):
        raise TypeError("Version must be provided as a string, e.g., '1.23' not 1.23")
    try:
        data = await _make_request(
            "PUT",
            f"{Config.api.release_endpoint}/{product_name}/{version}",
            json_data={
                "release_date": release_date,
                "active_support_end_date": active_support_end_date,
                "security_support_end_date": security_support_end_date,
                "eol_date": eol_date
            }
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def delete_version(
    ctx: Context,
    product_name: str,
    version: str
) -> str:
    """Delete a specific version of a product.
    
    Args:
        ctx: MCP context
        product_name: Product name (e.g., "nginx")
        version: Version to delete (e.g., "1.0.0")
        
    Returns:
        str: Success message or error details
    """
    try:
        await _make_request(
            "DELETE",
            f"{Config.api.release_endpoint}/{product_name}/{version}"
        )
        return json.dumps({
            "status": "success",
            "message": f"Version {version} of product {product_name} deleted successfully"
        }, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def get_all_versions(
    ctx: Context,
    product_name: Optional[str] = None,
    vendor: Optional[str] = None,
    page: int = 1,
    page_size: int = 100
) -> str:
    """Get all versions with optional filtering and pagination.
    
    Args:
        ctx: MCP context
        product_name: Filter by product name (optional)
        vendor: Filter by vendor name (optional)
        page: Page number (default: 1)
        page_size: Number of items per page (default: 100)
        
    Returns:
        str: JSON with paginated list of versions and metadata
    """
    try:
        # Build query parameters
        params = {
            "page": page,
            "page_size": page_size
        }
        
        # Add optional filters
        if product_name:
            params["product_name"] = product_name
        if vendor:
            params["vendor"] = vendor
            
        data = await _make_request(
            "GET",
            f"{Config.api.release_endpoint}",
            params=params
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def get_all_latest_versions(
    ctx: Context,
    product_name: Optional[str] = None,
    vendor: Optional[str] = None,
    page: int = 1,
    page_size: int = 100
) -> str:
    """Get the latest versions of all products with optional filtering and pagination.
    
    Args:
        ctx: MCP context
        product_name: Filter by product name (optional)
        vendor: Filter by vendor name (optional)
        page: Page number (default: 1)
        page_size: Number of items per page (default: 100)
        
    Returns:
        str: JSON with paginated list of latest versions and metadata
    """
    try:
        # Build query parameters
        params = {
            "page": page,
            "page_size": page_size
        }
        
        # Add optional filters
        if product_name:
            params["product_name"] = product_name
        if vendor:
            params["vendor"] = vendor
            
        data = await _make_request(
            "GET",
            f"{Config.api.release_endpoint}/latest",
            params=params
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def load_versions(ctx: Context, releases: str) -> str:
    """Load multiple release entries from a JSON string.
    
    Args:
        ctx: MCP context
        releases: JSON string containing release data. 
                  Accepts a direct JSON array [...], a single release object {...},
                  or a JSON object {"releases": [...]}.
                  Each release must include required fields.
                  
    Returns:
        str: JSON with results of the load operation
        
    Example of CORRECT JSON formats:
    [
        {
            "product_name": "string",
            "version": "string",
            "release_date": "2024-04-15",
            "active_support_end_date": "2024-04-15",
            "security_support_end_date": "2024-04-15",
            "eol_date": "2024-04-15"
        }
    ]
    
    {
        "product_name": "string",
        "version": "string",
        "release_date": "2024-04-15",
        "active_support_end_date": "2024-04-15",
        "security_support_end_date": "2024-04-15",
        "eol_date": "2024-04-15"
    }
    
    {
        "releases": [
            {
                "product_name": "string",
                "version": "string",
                "release_date": "2024-04-15",
                "active_support_end_date": "2024-04-15",
                "security_support_end_date": "2024-04-15",
                "eol_date": "2024-04-15"
            }
        ]
    }
    
    IMPORTANT INSTRUCTIONS FOR AI:
    1. The JSON can be a direct array '[...]', a single object '{...}', or an object with a 'releases' key.
    2. Each release item must have all required fields:
       - product_name (string)
       - version (string)
       - release_date (YYYY-MM-DD or ISO 8601 datetime)
       - active_support_end_date (YYYY-MM-DD or ISO 8601 datetime)
       - security_support_end_date (YYYY-MM-DD or ISO 8601 datetime)
       - eol_date (YYYY-MM-DD or ISO 8601 datetime)
    """
    try:
        # Parse the releases string to validate JSON
        releases_data = json.loads(releases)
        
        # Send to API
        data = await _make_request(
            "POST",
            f"{Config.api.release_endpoint}/load",
            json_data=releases_data
        )
        return json.dumps(data, indent=2)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format - {str(e)}"
    except VersionError as e:
        return f"Error: {str(e)}"

async def search_releases(
    ctx: Context,
    vendor: Optional[str] = None,
    product_name: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    date_field: str = "release_date",
    page: int = 1,
    page_size: int = 100
) -> str:
    """Search releases with optional filters for vendor, product name and date range.
    
    Args:
        ctx: MCP context
        vendor: Optional vendor name to filter by
        product_name: Optional product name to filter by
        from_date: Optional start date for filtering. Accepts both YYYY-MM-DD format (e.g., "2024-04-15") 
                  and ISO 8601 datetime format (e.g., "2024-04-15T00:00:00Z")
        to_date: Optional end date for filtering. Accepts both YYYY-MM-DD format and ISO 8601 datetime format
        date_field: Which date field to filter on (release_date, active_support_end_date, security_support_end_date, eol_date)
        page: Page number (starting from 1)
        page_size: Number of items per page
        
    Returns:
        str: JSON string containing list of releases matching the search criteria
        
    Example:
        Both date formats are supported:
        search_releases(ctx, from_date="2024-01-01", to_date="2024-12-31")  # Simple date format
        search_releases(ctx, from_date="2024-01-01T00:00:00Z", to_date="2024-12-31T23:59:59Z")  # ISO datetime format
    """
    try:
        params = {
            "vendor": vendor,
            "product_name": product_name,
            "from_date": from_date,
            "to_date": to_date,
            "date_field": date_field,
            "page": str(page),
            "page_size": str(page_size)
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        data = await _make_request(
            "GET",
            f"{Config.api.release_endpoint}/search",
            params=params
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"

async def get_version_cves(
    ctx: Context,
    product_name: str,
    version: str,
    vendor: Optional[str] = None
) -> str:
    """Get CVEs (Common Vulnerabilities and Exposures) for a specific version of a product.
    
    Args:
        ctx: MCP context
        product_name: Product name (e.g., "nginx")
        version: Specific version to retrieve CVEs for (e.g., "1.0.0"). Must be a string.
        vendor: Optional vendor name to filter by
        
    Returns:
        str: JSON array of CVE entries for the specified version
        
    Example:
        # Correct usage:
        get_version_cves(ctx, "nginx", "1.0.0")
        get_version_cves(ctx, "nginx", "1.0.0", vendor="NGINX Inc")
        
    Raises:
        TypeError: If version is not provided as a string
        VersionError: If the API request fails
    """
    if not isinstance(version, str):
        raise TypeError("Version must be provided as a string, e.g., '1.0.0' not 1.0")
        
    try:
        # Build the endpoint with optional vendor parameter
        endpoint = f"{Config.api.release_endpoint}/{product_name}/{version}/cves"
        if vendor:
            endpoint = f"{endpoint}?vendor={vendor}"
            
        data = await _make_request(
            "GET",
            endpoint
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}" 