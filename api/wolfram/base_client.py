"""Base Wolfram Alpha API client."""
import httpx
from typing import Dict, Any, Optional
import structlog
from urllib.parse import urlencode

from config.settings import settings

logger = structlog.get_logger()


class WolframBaseClient:
    """Base client for Wolfram Alpha API interactions."""
    
    def __init__(self):
        self.app_id = settings.wolfram_app_id
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    async def _make_request(
        self, 
        url: str, 
        params: Dict[str, Any], 
        method: str = "GET"
    ) -> Dict[str, Any]:
        """Make a request to Wolfram Alpha API.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            method: HTTP method (GET or POST)
            
        Returns:
            API response as dictionary
            
        Raises:
            httpx.HTTPError: If request fails
        """
        # Add app ID to params
        params["appid"] = self.app_id
        
        try:
            if method == "GET":
                response = await self.client.get(url, params=params)
            else:
                response = await self.client.post(url, data=params)
                
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("content-type", "")
            
            if "json" in content_type:
                return response.json()
            elif "xml" in content_type:
                # For XML responses, we'll need to parse them
                # For now, return raw text
                return {"raw_xml": response.text}
            else:
                return {"raw_text": response.text}
                
        except httpx.HTTPError as e:
            logger.error(
                "Wolfram API request failed",
                url=url,
                params=params,
                error=str(e)
            )
            raise
            
    def _preprocess_query(self, query: str) -> str:
        """Preprocess query for Wolfram Alpha.
        
        Args:
            query: User query
            
        Returns:
            Preprocessed query
        """
        # Convert to simplified keywords when possible
        # Remove unnecessary words
        query = query.strip()
        
        # Convert common patterns
        replacements = {
            "what is the": "",
            "how to calculate": "",
            "find the": "",
            "calculate": "",
            "what is": "",
            "how many": "",
            "how much": "",
        }
        
        query_lower = query.lower()
        for old, new in replacements.items():
            if query_lower.startswith(old):
                query = query[len(old):].strip()
                break
                
        # Convert exponential notation
        # e.g., "6e14" -> "6*10^14"
        import re
        query = re.sub(r'(\d+)e(\d+)', r'\1*10^\2', query)
        
        return query
