"""Wolfram Language Evaluation API client for code execution."""
from typing import Dict, Any, Optional, Union
import base64
import structlog

from .base_client import WolframBaseClient
from config.settings import settings

logger = structlog.get_logger()


class WolframLanguageEvalClient(WolframBaseClient):
    """Client for Wolfram Language Evaluation API.
    
    This API allows direct execution of Wolfram Language code
    for complex computations, plotting, and data analysis.
    """
    
    def __init__(self):
        super().__init__()
        self.api_url = settings.wolfram_language_api_url
        
    async def evaluate(
        self, 
        code: str,
        output_format: str = "string",
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Evaluate Wolfram Language code.
        
        Args:
            code: Wolfram Language code to execute
            output_format: Output format (string, expression, image, etc.)
            timeout: Execution timeout in seconds
            
        Returns:
            Evaluation result
        """
        # Clean and format code
        clean_code = self._clean_code(code)
        
        # Build parameters
        params = {
            "input": clean_code,
            "format": output_format,
            "timeout": timeout
        }
        
        logger.info(
            "Evaluating Wolfram Language code",
            code_length=len(clean_code),
            output_format=output_format
        )
        
        # Make request
        response = await self._make_request(self.api_url, params)
        
        # Process response
        return self._process_response(response, code, output_format)
        
    def _clean_code(self, code: str) -> str:
        """Clean Wolfram Language code.
        
        Args:
            code: Raw code
            
        Returns:
            Cleaned code
        """
        # Remove comments and extra whitespace
        lines = []
        for line in code.split("\n"):
            # Remove comments
            if "(*" in line and "*)" in line:
                start = line.find("(*")
                end = line.find("*)") + 2
                line = line[:start] + line[end:]
                
            # Strip whitespace
            line = line.strip()
            if line:
                lines.append(line)
                
        # Join lines
        clean_code = " ".join(lines)
        
        # Compress whitespace
        import re
        clean_code = re.sub(r'\s+', ' ', clean_code)
        
        return clean_code
        
    def _process_response(
        self,
        response: Dict[str, Any],
        original_code: str,
        output_format: str
    ) -> Dict[str, Any]:
        """Process evaluation response.

        Args:
            response: Raw API response
            original_code: Original code
            output_format: Expected output format

        Returns:
            Processed response
        """
        result = {
            "original_code": original_code,
            "success": False,
            "output": None,
            "output_type": output_format,
            "error": None,
            "messages": []
        }

        # Handle different response types
        if "raw_text" in response:
            result["success"] = True
            result["output"] = response["raw_text"]

        elif "raw_xml" in response:
            # Handle XML responses from Wolfram Alpha
            xml_content = response["raw_xml"]
            result = self._process_xml_response(xml_content, result)

        elif "error" in response:
            result["error"] = response["error"]

        # Handle image outputs
        if output_format == "image" and result["success"]:
            # Convert to base64 if needed
            if isinstance(result["output"], bytes):
                result["output"] = base64.b64encode(result["output"]).decode()
                result["output_type"] = "base64_image"

        return result

    def _process_xml_response(self, xml_content: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process XML response from Wolfram Alpha.

        Args:
            xml_content: Raw XML content
            result: Result dictionary to update

        Returns:
            Updated result dictionary
        """
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)

            # Check if query was successful
            if not self._is_query_successful(root):
                result["error"] = self._extract_error_message(root)
                return result

            result["success"] = True

            # Extract output based on type
            if result["output_type"] == "image":
                result["output"] = self._extract_image_url(root)
            else:
                result["output"] = self._extract_plaintext(root)

        except ET.ParseError as e:
            result["error"] = f"Failed to parse XML response: {str(e)}"
        except Exception as e:
            result["error"] = f"Failed to process XML response: {str(e)}"

        return result

    def _is_query_successful(self, root) -> bool:
        """Check if the Wolfram Alpha query was successful."""
        success_elem = root.find(".//success")
        return success_elem is not None and success_elem.text == "true"

    def _extract_error_message(self, root) -> str:
        """Extract error message from XML response."""
        error_elem = root.find(".//error/msg")
        return error_elem.text if error_elem is not None else "Unknown error in XML response"

    def _extract_image_url(self, root) -> str:
        """Extract image URL from XML response."""
        images = root.findall(".//img")
        if images:
            img_src = images[0].get("src")
            if img_src:
                return img_src
        # Fallback to plaintext if no images
        return self._extract_plaintext(root)

    def _extract_plaintext(self, root) -> str:
        """Extract plaintext content from XML response."""
        plaintext_elem = root.find(".//plaintext")
        return plaintext_elem.text if plaintext_elem is not None else ""
        
    async def plot(
        self,
        expression: str,
        variable: str = "x",
        range_min: float = -10,
        range_max: float = 10,
        plot_type: str = "Plot"
    ) -> Dict[str, Any]:
        """Create a plot using natural language query.

        Args:
            expression: Expression to plot
            variable: Variable name
            range_min: Minimum range value
            range_max: Maximum range value
            plot_type: Type of plot (Plot, Plot3D, etc.)

        Returns:
            Plot result with image
        """
        # Build natural language query
        query = f"plot {expression} from {range_min} to {range_max}"

        # Use full results client for better image extraction
        from .full_results_client import WolframFullResultsClient

        async with WolframFullResultsClient() as client:
            result = await client.query(
                input_text=query,
                output="xml",
                format_types=["image"]
            )

            # Convert to expected format
            return {
                "original_code": query,
                "success": result.get("success", False),
                "output": self._extract_plot_image(result),
                "output_type": "image_url" if result.get("success") else "text",
                "error": result.get("error"),
                "messages": []
            }

    def _extract_plot_image(self, result: Dict[str, Any]) -> str:
        """Extract plot image URL from full results response."""
        if not result.get("success") or not result.get("pods"):
            return None

        # Look for plot pods
        for pod in result["pods"]:
            if "plot" in pod.get("id", "").lower():
                for subpod in pod.get("subpods", []):
                    if subpod.get("img") and subpod["img"].get("src"):
                        return subpod["img"]["src"]

        # If no plot pod found, return first available image
        for pod in result["pods"]:
            for subpod in pod.get("subpods", []):
                if subpod.get("img") and subpod["img"].get("src"):
                    return subpod["img"]["src"]

        return None
        
    async def manipulate(
        self,
        expression: str,
        parameters: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create interactive manipulation.
        
        Args:
            expression: Expression to manipulate
            parameters: Parameter specifications
            
        Returns:
            Manipulation result
        """
        # Build parameter list
        param_specs = []
        for param, spec in parameters.items():
            min_val = spec.get("min", 0)
            max_val = spec.get("max", 10)
            step = spec.get("step", 1)
            initial = spec.get("initial", min_val)
            
            param_specs.append(
                f"{{{param}, {initial}, {min_val}, {max_val}, {step}}}"
            )
            
        # Build Manipulate code
        code = f"Manipulate[{expression}, {', '.join(param_specs)}]"
        
        # Evaluate
        return await self.evaluate(code)
        
    async def solve_equation(
        self,
        equation: str,
        variable: str = "x",
        domain: str = "Reals"
    ) -> Dict[str, Any]:
        """Solve an equation symbolically.
        
        Args:
            equation: Equation to solve
            variable: Variable to solve for
            domain: Solution domain
            
        Returns:
            Solution(s)
        """
        # Build solve code
        code = f"Solve[{equation}, {variable}, {domain}]"
        
        # Evaluate
        result = await self.evaluate(code)
        
        # Post-process to extract solutions
        if result["success"] and result["output"]:
            # Parse solutions from output
            result["solutions"] = self._parse_solutions(result["output"])
            
        return result
        
    def _parse_solutions(self, output: str) -> list:
        """Parse solutions from Solve output.
        
        Args:
            output: Solve command output
            
        Returns:
            List of solutions
        """
        solutions = []
        
        # Simple parsing - in production use proper Wolfram Language parser
        if "{{" in output and "}}" in output:
            # Extract solution sets
            import re
            matches = re.findall(r'{([^{}]+)}', output)
            for match in matches:
                if "->" in match:
                    parts = match.split("->")
                    if len(parts) == 2:
                        var = parts[0].strip()
                        value = parts[1].strip()
                        solutions.append({
                            "variable": var,
                            "value": value
                        })
                        
        return solutions
