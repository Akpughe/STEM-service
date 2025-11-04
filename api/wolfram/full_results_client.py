"""Wolfram Full Results API client for structured responses."""
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET
import structlog

from .base_client import WolframBaseClient
from config.settings import settings

logger = structlog.get_logger()


class WolframFullResultsClient(WolframBaseClient):
    """Client for Wolfram Alpha Full Results API.
    
    This API returns complete structured results including pods,
    subpods, and various data formats.
    """
    
    def __init__(self):
        super().__init__()
        self.api_url = settings.wolfram_full_results_api_url
        
    async def query(
        self, 
        input_text: str,
        output: str = "json",
        format_types: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None,
        pod_index: Optional[int] = None,
        include_pod_id: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Query Wolfram Alpha Full Results API.
        
        Args:
            input_text: Query text
            output: Output format (json or xml)
            format_types: List of format types to include
            assumptions: List of assumption values
            pod_index: Specific pod index to return
            include_pod_id: List of pod IDs to include
            
        Returns:
            Structured API response
        """
        # Preprocess query
        processed_query = self._preprocess_query(input_text)
        
        # Build parameters
        params = {
            "input": processed_query,
            "output": output
        }
        
        # Add optional parameters
        if format_types:
            params["format"] = ",".join(format_types)
        else:
            params["format"] = "plaintext,image"
            
        if assumptions:
            params["assumption"] = assumptions
            
        if pod_index is not None:
            params["podindex"] = pod_index
            
        if include_pod_id:
            params["includepodid"] = "|".join(include_pod_id)
            
        logger.info(
            "Querying Wolfram Full Results API",
            query=processed_query,
            output=output
        )
        
        # Make request
        response = await self._make_request(self.api_url, params)
        
        # Process based on output format
        if output == "json":
            return self._process_json_response(response, input_text)
        else:
            return self._process_xml_response(response, input_text)
            
    def _process_json_response(
        self, 
        response: Dict[str, Any], 
        original_query: str
    ) -> Dict[str, Any]:
        """Process JSON response.
        
        Args:
            response: Raw JSON response
            original_query: Original query
            
        Returns:
            Processed response
        """
        result = {
            "original_query": original_query,
            "success": False,
            "pods": [],
            "assumptions": [],
            "warnings": [],
            "error": None
        }
        
        if "queryresult" in response:
            qr = response["queryresult"]
            
            result["success"] = qr.get("success", False)
            result["error"] = qr.get("error")
            
            # Extract pods
            if "pods" in qr:
                result["pods"] = qr["pods"]
                
            # Extract assumptions
            if "assumptions" in qr:
                result["assumptions"] = qr["assumptions"]
                
            # Extract warnings
            if "warnings" in qr:
                result["warnings"] = qr["warnings"]
                
        return result
        
    def _process_xml_response(
        self, 
        response: Dict[str, Any], 
        original_query: str
    ) -> Dict[str, Any]:
        """Process XML response.
        
        Args:
            response: Raw response with XML
            original_query: Original query
            
        Returns:
            Processed response
        """
        result = {
            "original_query": original_query,
            "success": False,
            "pods": [],
            "assumptions": [],
            "warnings": [],
            "error": None
        }
        
        # Parse XML
        if "raw_xml" in response:
            try:
                root = ET.fromstring(response["raw_xml"])
                
                # Extract success status
                result["success"] = root.get("success") == "true"
                
                # Extract pods
                for pod in root.findall(".//pod"):
                    pod_data = {
                        "title": pod.get("title"),
                        "id": pod.get("id"),
                        "position": pod.get("position"),
                        "subpods": []
                    }
                    
                    # Extract subpods
                    for subpod in pod.findall(".//subpod"):
                        subpod_data = {
                            "title": subpod.get("title"),
                            "plaintext": None,
                            "img": None
                        }
                        
                        # Get plaintext
                        plaintext = subpod.find(".//plaintext")
                        if plaintext is not None and plaintext.text:
                            subpod_data["plaintext"] = plaintext.text
                            
                        # Get image
                        img = subpod.find(".//img")
                        if img is not None:
                            subpod_data["img"] = {
                                "src": img.get("src"),
                                "alt": img.get("alt"),
                                "width": img.get("width"),
                                "height": img.get("height")
                            }
                            
                        pod_data["subpods"].append(subpod_data)
                        
                    result["pods"].append(pod_data)
                    
            except ET.ParseError as e:
                logger.error("Failed to parse XML response", error=str(e))
                result["error"] = f"XML parse error: {str(e)}"
                
        return result
