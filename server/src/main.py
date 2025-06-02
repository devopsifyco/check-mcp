from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
import asyncio
import uuid
from core.config import Config
from core.version import (
    get_latest_version,
    get_versions,
    get_specific_version,
    create_version,
    update_version,
    get_all_versions,
    get_all_latest_versions,
    delete_version,
    load_versions,
    search_releases,
    get_version_cves
)
from core.product import create_product
from core.cve import (    
    search_cve
)

load_dotenv()

def format_session_id(session_id: str) -> str:
    """Format session ID to ensure consistent format."""
    # Remove any hyphens and convert to lowercase
    clean_id = session_id.replace('-', '').lower()
    # Add hyphens in the correct positions
    return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"

# Create a dataclass for our application context
@dataclass
class DemoContext:
    """Context for the DevOpsify MCP server."""
    session_id: str = None

@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[DemoContext]:
    """
    Manages the DevOpsify client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        DemoContext: The context containing the Opsify API client
    """        
    context = None
    try:
        # Validate configuration before starting
        Config.validate_config()
        # Generate a new session ID
        session_id = format_session_id(str(uuid.uuid4()))
        context = DemoContext(session_id=session_id)
        yield context
    except Exception as e:
        print(f"Error in lifespan: {str(e)}")
        raise
    finally:
        # Cleanup any resources if needed
        if context:
            # Add any necessary cleanup here
            pass

# Initialize FastMCP server with the DevOpsify client as context
mcp = FastMCP(
    "mcp-devopsify",
    description="MCP server for long term memory storage and retrieval with DevOpsify",
    lifespan=lifespan,
    host=Config.server.host,
    port=Config.server.port,
    session_timeout=3600,  # Set session timeout to 1 hour
    session_cleanup_interval=300  # Clean up expired sessions every 5 minutes
)

# Register version management tools
#mcp.tool()(get_versions)
#
#mcp.tool()(create_version)
#mcp.tool()(update_version)
#mcp.tool()(get_all_versions)
#mcp.tool()(get_all_latest_versions)
#mcp.tool()(delete_version)
#mcp.tool()(load_versions)
#mcp.tool()(create_product)

mcp.tool()(get_specific_version)
mcp.tool()(get_latest_version)
mcp.tool()(search_releases)

mcp.tool()(get_version_cves)
mcp.tool()(search_cve)

async def main():
    if Config.server.transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run with default transport
        await mcp.run_async()

if __name__ == "__main__":
    asyncio.run(main())
