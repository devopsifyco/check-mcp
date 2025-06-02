import os
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables
load_dotenv()

@dataclass
class ServerConfig:
    """Server configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8050
    transport: str = "sse"

@dataclass
class APIConfig:
    """API configuration settings."""
    base_url: str = "https://api.opsify.dev"
    api_key: Optional[str] = None
    release_endpoint: str = "/checks/release"
    product_endpoint: str = "/checks/product"
    cve_endpoint: str = "/checks/cve"

class Config:
    """Core configuration settings for the DevOpsify MCP server."""
    
    # Server configuration
    server = ServerConfig(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8050")),
        transport=os.getenv("TRANSPORT", "sse")
    )
    
    # API configuration
    api = APIConfig(
        base_url=os.getenv("OPSIFY_API_BASE_URL", "https://api.opsify.dev"),
        api_key=os.getenv("OPSIFY_API_KEY"),
        release_endpoint="/checks/release",
        product_endpoint="/checks/product",
        cve_endpoint="/checks/cve"
    )
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate that all required configuration is present."""
        if not cls.api.api_key:
            raise ValueError("OPSIFY_API_KEY environment variable is not set")
            
        if not cls.api.base_url:
            raise ValueError("OPSIFY_API_BASE_URL environment variable is not set")
            
        if cls.server.transport not in ["sse", "stdio"]:
            raise ValueError("TRANSPORT must be either 'sse' or 'stdio'")
            
        if not isinstance(cls.server.port, int) or cls.server.port < 1 or cls.server.port > 65535:
            raise ValueError("PORT must be a valid port number between 1 and 65535") 