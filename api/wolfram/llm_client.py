"""Wolfram LLM API client for natural language queries."""
from typing import Dict, Any, List, Optional
import structlog

from .base_client import WolframBaseClient
from config.settings import settings

logger = structlog.get_logger()


class WolframLLMClient(WolframBaseClient):
    """Client for Wolfram Alpha LLM API.
    
    This API is designed for natural language queries and returns
    computed results in a format suitable for LLMs.
    """
    
    def __init__(self):
        super().__init__()
        self.api_url = settings.wolfram_llm_api_url
        
    async def query(
        self, 
        input_text: str,
        assumptions: Optional[List[str]] = None,
        max_chars: int = 10000
    ) -> Dict[str, Any]:
        """Query Wolfram Alpha LLM API.
        
        Args:
            input_text: Natural language query
            assumptions: List of assumption values to use
            max_chars: Maximum characters in response
            
        Returns:
            API response with computed results
        """
        # Preprocess the query
        processed_query = self._preprocess_query(input_text)
        
        # Build parameters
        params = {
            "input": processed_query,
            "maxchars": max_chars
        }
        
        # Add assumptions if provided
        if assumptions:
            params["assumption"] = assumptions
            
        logger.info(
            "Querying Wolfram LLM API",
            query=processed_query,
            assumptions=assumptions
        )
        
        # Make request
        response = await self._make_request(self.api_url, params)
        
        # Process response
        return self._process_response(response, input_text)
        
    def _process_response(
        self, 
        response: Dict[str, Any], 
        original_query: str
    ) -> Dict[str, Any]:
        """Process API response.
        
        Args:
            response: Raw API response
            original_query: Original user query
            
        Returns:
            Processed response
        """
        # Extract key information
        result = {
            "original_query": original_query,
            "success": False,
            "result": None,
            "assumptions": None,
            "warnings": None,
            "error": None
        }
        
        # Handle different response formats
        if isinstance(response, dict):
            if "result" in response:
                result["success"] = True
                result["result"] = response["result"]
                
            if "assumptions" in response:
                result["assumptions"] = response["assumptions"]
                
            if "warnings" in response:
                result["warnings"] = response["warnings"]
                
            if "error" in response:
                result["error"] = response["error"]
                
        return result
        
    async def query_with_best_assumption(
        self, 
        input_text: str
    ) -> Dict[str, Any]:
        """Query with automatic assumption selection.
        
        Args:
            input_text: Natural language query
            
        Returns:
            API response with best assumption applied
        """
        # First query
        initial_response = await self.query(input_text)
        
        # Check if assumptions are available
        if initial_response.get("assumptions"):
            # Select best assumption (first one for now)
            # In production, use more sophisticated selection
            best_assumption = initial_response["assumptions"][0]
            
            logger.info(
                "Retrying with assumption",
                assumption=best_assumption
            )
            
            # Query again with assumption
            return await self.query(
                input_text, 
                assumptions=[best_assumption]
            )
            
        return initial_response
