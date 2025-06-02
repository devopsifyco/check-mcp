import json
from typing import Optional
from .version import _make_request, VersionError
from .config import Config
from mcp.server.fastmcp import Context

async def search_cve(
    ctx: Context,
    cve_id: Optional[str] = None,
    title: Optional[str] = None,
    state: Optional[str] = None,
    priority: Optional[str] = None,
    severity: Optional[str] = None,
    score: Optional[float] = None,
    product_name: Optional[str] = None,
    product_version: Optional[str] = None,
    vendor: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> str:
    """
    Search for CVEs using various filters.

    Args:
        ctx: MCP context
        cve_id: Optional CVE ID to search for
        title: Optional title to search in CVE description
        state: Optional state to filter by
        priority: Optional priority level to filter by
        severity: Optional severity level to filter by
        score: Optional CVSS score to filter by
        product_name: Optional product name to filter affected products
        product_version: Optional product version to filter affected products
        vendor: Optional vendor name to filter affected products
        from_date: Optional start date for filtering (format: YYYY-MM-DD or ISO 8601)
        to_date: Optional end date for filtering (format: YYYY-MM-DD or ISO 8601)
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
    Returns:
        str: JSON list of CVEs matching the search criteria
    """
    params = {
        "cve_id": cve_id,
        "title": title,
        "state": state,
        "priority": priority,
        "severity": severity,
        "score": score,
        "product_name": product_name,
        "product_version": product_version,
        "vendor": vendor,
        "from_date": from_date,
        "to_date": to_date,
        "skip": skip,
        "limit": limit
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    try:
        data = await _make_request(
            "GET",
            f"{Config.api.cve_endpoint}/search",
            params=params
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}" 