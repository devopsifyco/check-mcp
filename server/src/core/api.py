import aiohttp
from typing import Dict, Any, Optional
from .config import Config

class OpsifyAPI:
    """Client for interacting with the Opsify API."""
    
    def __init__(self):
        self.base_url = Config.api.base_url
        self.api_key = Config.api.api_key
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def get_component_version(self, component_name: str) -> Dict[str, Any]:
        """Get version information for a specific component.
        
        Args:
            component_name: The name of the component to get version information for
            
        Returns:
            Dict containing the version information
            
        Raises:
            aiohttp.ClientError: If the API request fails
            ValueError: If the response is not valid JSON
        """
        if not self._session:
            raise RuntimeError("API client not initialized. Use async with context manager.")
            
        endpoint = f"{self.base_url}{Config.api.release_endpoint}/{component_name}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        async with self._session.get(endpoint, headers=headers) as response:
            response.raise_for_status()
            return await response.json() 