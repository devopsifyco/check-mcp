import json
from typing import Optional
from .version import _make_request, VersionError
from .config import Config
from mcp.server.fastmcp import Context

async def create_product(
    ctx: Context,
    product_name: str,
    release_url: Optional[str] = None,
    vendor_name: Optional[str] = None,
    vendor_website: Optional[str] = None
) -> str:
    """Create a new product, optionally associating it with a vendor.

    This MCP tool takes product details and optional vendor details as arguments.
    It then constructs a JSON payload and calls the backend API endpoint to create the product.

    Args:
        ctx: MCP context
        product_name: The name of the product (e.g., "nginx")
        release_url: Optional URL for the product's release notes or information.
        vendor_name: Optional name of the vendor. If provided, the vendor will be found or created by the API.
        vendor_website: Optional website of the vendor. Used by the API only if vendor_name is provided and the vendor needs to be created.

    Returns:
        str: JSON with created product details or error message.

    API Request Body Structure:
    The tool sends a POST request to the product API endpoint with the following JSON body structure:

    ```json
    {
      "name": "<product_name>",
      "release_url": "<release_url or null>",
      "vendor": { // This key is included only if vendor_name is provided
        "name": "<vendor_name>",
        "website": "<vendor_website or null>"
      }
    }
    ```
    """
    payload = {
        "name": product_name,
        "release_url": release_url,
        "vendor": {
            "name": vendor_name if vendor_name else "",
            "website": vendor_website if vendor_website else ""
        }
    }

    try:

             
        data = await _make_request(
            "POST",
            f"{Config.api.product_endpoint}", # Use the product endpoint
            json_data=payload
        )
        return json.dumps(data, indent=2)
    except VersionError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        # Catch other potential errors during request
        return f"An unexpected error occurred: {str(e)}" 