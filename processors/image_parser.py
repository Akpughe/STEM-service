"""Image parsing processor for mathematical content extraction."""
from typing import Dict, Any, Optional, Union
from io import BytesIO
import structlog
from PIL import Image
import pytesseract

from api.groq import GroqClient

logger = structlog.get_logger()


class ImageParser:
    """Parse mathematical content from images.

    Note: openai/gpt-oss-120b does not have vision capabilities.
    This parser will primarily use OCR for image extraction.
    """

    def __init__(self):
        self.groq_client = GroqClient()
        
    async def parse_image(
        self,
        image_data: Union[bytes, BytesIO],
        use_ocr_fallback: bool = True
    ) -> Dict[str, Any]:
        """Parse mathematical content from image.
        
        Args:
            image_data: Image data
            use_ocr_fallback: Whether to use OCR as fallback
            
        Returns:
            Parsed content
        """
        result = {
            "success": False,
            "content": None,
            "content_type": None,
            "confidence": 0.0,
            "method": None,
            "error": None
        }
        
        try:
            # Note: openai/gpt-oss-120b doesn't have vision capabilities
            # Using OCR as primary method
            logger.info("Extracting text from image using OCR")
            ocr_result = self._ocr_extract(image_data)

            if ocr_result["success"]:
                result["success"] = True
                result["content"] = ocr_result["text"]
                result["content_type"] = "unknown"
                result["confidence"] = 0.75  # OCR confidence
                result["method"] = "ocr"

                # Post-process the content
                result["content"] = self._post_process_content(result["content"])
            else:
                result["error"] = "OCR extraction failed"
                    
        except Exception as e:
            logger.error("Image parsing failed", error=str(e))
            result["error"] = str(e)
            
        return result
        
    def _ocr_extract(self, image_data: Union[bytes, BytesIO]) -> Dict[str, Any]:
        """Extract text using OCR.
        
        Args:
            image_data: Image data
            
        Returns:
            OCR result
        """
        try:
            # Convert to PIL Image
            if isinstance(image_data, bytes):
                image = Image.open(BytesIO(image_data))
            else:
                image = Image.open(image_data)
                
            # Preprocess for better OCR
            image = self._preprocess_for_ocr(image)
            
            # Run OCR
            text = pytesseract.image_to_string(
                image, 
                config='--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/=()[]{}.,^_∫∑∏√∞αβγδεζηθικλμνξοπρστυφχψω'
            )
            
            return {
                "success": bool(text.strip()),
                "text": text.strip()
            }
            
        except Exception as e:
            logger.error("OCR extraction failed", error=str(e))
            return {
                "success": False,
                "text": None,
                "error": str(e)
            }
            
    def _preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
            
        # Resize if too small
        width, height = image.size
        if width < 1000:
            scale = 1000 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
        # Apply threshold to get black and white
        threshold = 127
        image = image.point(lambda p: p > threshold and 255)
        
        return image
        
    def _post_process_content(self, content: str) -> str:
        """Post-process extracted content.
        
        Args:
            content: Raw extracted content
            
        Returns:
            Cleaned content
        """
        # Clean up common OCR/extraction errors
        replacements = {
            " x ": "*",  # Multiplication
            "÷": "/",    # Division
            "×": "*",    # Multiplication symbol
            "−": "-",    # Minus sign
            "·": "*",    # Dot multiplication
            "\n\n": "\n",  # Double newlines
            "  ": " ",   # Double spaces
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        # Fix common math notation issues
        import re
        
        # Fix exponents (x^2 instead of x2)
        content = re.sub(r'([a-zA-Z])(\d+)', r'\1^\2', content)
        
        # Fix function notation
        content = re.sub(r'(\w+)\s*\(', r'\1(', content)
        
        # Ensure proper spacing around operators
        content = re.sub(r'([+\-*/=])', r' \1 ', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
        
    async def extract_diagram_elements(
        self, 
        image_data: Union[bytes, BytesIO]
    ) -> Dict[str, Any]:
        """Extract elements from diagrams (circuits, graphs, etc.).
        
        Args:
            image_data: Image data
            
        Returns:
            Extracted diagram elements
        """
        # Note: openai/gpt-oss-120b doesn't support vision
        # Using OCR-based extraction for diagrams
        logger.warning("Diagram extraction with openai/gpt-oss-120b limited to OCR")

        # Extract text using OCR
        ocr_result = self._ocr_extract(image_data)

        if ocr_result["success"]:
            # Parse the response to structure diagram elements
            return self._structure_diagram_elements(ocr_result["text"])
        else:
            return {
                "success": False,
                "error": "Failed to extract diagram elements via OCR. Vision model required for better results."
            }
            
    def _structure_diagram_elements(self, content: str) -> Dict[str, Any]:
        """Structure extracted diagram elements.
        
        Args:
            content: Extracted content
            
        Returns:
            Structured elements
        """
        # This is a simplified version - enhance based on specific needs
        return {
            "success": True,
            "raw_content": content,
            "elements": self._extract_elements(content),
            "diagram_type": self._identify_diagram_type(content)
        }
        
    def _extract_elements(self, content: str) -> list:
        """Extract individual elements from content.
        
        Args:
            content: Diagram description
            
        Returns:
            List of elements
        """
        elements = []
        
        # Look for component patterns
        import re
        
        # Resistor pattern: R1 = 10 ohm, 10Ω resistor, etc.
        resistor_pattern = r'[Rr](?:esistor)?\s*\d*\s*[:=]?\s*(\d+\.?\d*)\s*[ΩΩ]?(?:ohm)?'
        for match in re.finditer(resistor_pattern, content):
            elements.append({
                "type": "resistor",
                "value": float(match.group(1)),
                "unit": "ohm"
            })
            
        # Similar patterns for other components...
        
        return elements
        
    def _identify_diagram_type(self, content: str) -> str:
        """Identify the type of diagram.
        
        Args:
            content: Diagram description
            
        Returns:
            Diagram type
        """
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["resistor", "capacitor", "inductor", "voltage"]):
            return "electrical_circuit"
        elif any(word in content_lower for word in ["axis", "plot", "graph", "curve"]):
            return "mathematical_graph"
        elif any(word in content_lower for word in ["flow", "box", "arrow", "process"]):
            return "flowchart"
        else:
            return "unknown"
