"""Math problem-solving routes."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List
import structlog
from pydantic import BaseModel, Field

from api.wolfram import (
    WolframLLMClient,
    WolframFullResultsClient,
    WolframShowStepsClient,
    WolframLanguageEvalClient
)
from api.openai import GPT5Client
from processors import QueryClassifier, ImageParser, ResultEnhancer

logger = structlog.get_logger()
router = APIRouter()


# Request/Response models
class MathQuery(BaseModel):
    """Math query request model."""
    query: str = Field(..., description="Mathematical query or problem")
    show_steps: bool = Field(default=True, description="Show step-by-step solution")
    student_level: str = Field(default="undergraduate", description="Student education level")
    include_educational: bool = Field(default=True, description="Include educational content")


class MathResponse(BaseModel):
    """Math query response model."""
    success: bool
    query: str
    result: dict
    explanation: Optional[str] = None
    steps: Optional[List[dict]] = None
    educational_content: Optional[dict] = None
    visualizations: Optional[List[dict]] = None
    error: Optional[str] = None


# Initialize components
query_classifier = QueryClassifier()
image_parser = ImageParser()
result_enhancer = ResultEnhancer()


@router.post("/solve", response_model=MathResponse)
async def solve_math_problem(query_data: MathQuery):
    """Solve a mathematical problem with explanation."""
    try:
        logger.info("Processing math query", query=query_data.query)
        
        # Classify query
        query_type, api_type = query_classifier.classify_query(query_data.query)
        logger.info("Query classified", type=query_type.value, api=api_type.value)
        
        # Check if clarification needed
        clarifications = query_classifier.requires_clarification(query_data.query)
        if clarifications:
            return MathResponse(
                success=False,
                query=query_data.query,
                result={},
                error=f"Please clarify: {'; '.join(clarifications)}"
            )
        
        # Get API parameters
        api_params = query_classifier.get_api_params(query_type, api_type)
        
        # Preprocess query
        processed_query = query_classifier.preprocess_for_api(
            query_data.query, 
            query_type, 
            api_type
        )
        
        # Route to appropriate Wolfram API
        wolfram_result = await _call_wolfram_api(
            api_type.value,
            processed_query,
            api_params
        )

        # Check if Wolfram failed and use GPT fallback for complex queries
        if not wolfram_result.get("success") and not wolfram_result.get("pods"):
            logger.info("Wolfram API returned empty result, trying GPT fallback")
            gpt_client = GPT5Client()
            gpt_result = await gpt_client.solve_math_problem(
                query_data.query,
                student_level=query_data.student_level,
                show_steps=query_data.show_steps
            )
            
            # Return GPT result directly if Wolfram failed
            if gpt_result.get("success"):
                return MathResponse(
                    success=True,
                    query=query_data.query,
                    result=gpt_result,
                    explanation=gpt_result.get("explanation"),
                    steps=gpt_result.get("steps"),
                    educational_content=gpt_result.get("educational_content"),
                    visualizations=gpt_result.get("visualizations")
                )

        # Normalize the result format
        normalized_result = _normalize_wolfram_result(wolfram_result, api_type.value)

        # Check if step-by-step solutions are available and fetch them
        steps = await _fetch_steps_if_available(wolfram_result, normalized_result, processed_query, query_data.query)

        # Add steps to normalized result
        if steps:
            normalized_result["steps"] = steps

        # Enhance result if requested
        if query_data.include_educational:
            enhanced_result = await result_enhancer.enhance_result(
                normalized_result,
                query_data.query,
                query_data.student_level,
                include_educational=True
            )

            return MathResponse(
                success=True,
                query=query_data.query,
                result=normalized_result,
                explanation=enhanced_result.get("explanation"),
                steps=enhanced_result.get("steps"),
                educational_content=enhanced_result.get("educational_content"),
                visualizations=enhanced_result.get("visualizations")
            )
        else:
            return MathResponse(
                success=True,
                query=query_data.query,
                result=normalized_result
            )
            
    except Exception as e:
        logger.error("Failed to solve problem", error=str(e))
        return MathResponse(
            success=False,
            query=query_data.query,
            result={},
            error=str(e)
        )


@router.post("/solve-image", response_model=MathResponse)
async def solve_from_image(
    file: UploadFile = File(...),
    show_steps: bool = Form(default=True),
    student_level: str = Form(default="undergraduate"),
    include_educational: bool = Form(default=True)
):
    """Solve mathematical problem from uploaded image."""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
            
        # Read image data
        image_data = await file.read()
        
        # Parse image
        logger.info("Parsing image for mathematical content")
        parse_result = await image_parser.parse_image(image_data)
        
        if not parse_result["success"]:
            return MathResponse(
                success=False,
                query="[Image]",
                result={},
                error=f"Failed to parse image: {parse_result.get('error', 'Unknown error')}"
            )
            
        # Extract mathematical query
        extracted_query = parse_result["content"]
        logger.info("Extracted query from image", query=extracted_query)
        
        # Process as regular query
        query_data = MathQuery(
            query=extracted_query,
            show_steps=show_steps,
            student_level=student_level,
            include_educational=include_educational
        )
        
        return await solve_math_problem(query_data)
        
    except Exception as e:
        logger.error("Failed to process image", error=str(e))
        return MathResponse(
            success=False,
            query="[Image]",
            result={},
            error=str(e)
        )


@router.post("/plot")
async def create_plot(
    expression: str = Form(...),
    variable: str = Form(default="x"),
    range_min: float = Form(default=-10),
    range_max: float = Form(default=10),
    plot_type: str = Form(default="Plot")
):
    """Create a mathematical plot."""
    try:
        async with WolframLanguageEvalClient() as client:
            result = await client.plot(
                expression=expression,
                variable=variable,
                range_min=range_min,
                range_max=range_max,
                plot_type=plot_type
            )
            
        return {
            "success": result["success"],
            "expression": expression,
            "plot": result.get("output"),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error("Failed to create plot", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


def _normalize_wolfram_result(wolfram_result: dict, api_type: str) -> dict:
    """Normalize Wolfram API results to a consistent format.

    Args:
        wolfram_result: Raw result from Wolfram API
        api_type: The API type that was used

    Returns:
        Normalized result with consistent structure
    """
    if api_type == "show_steps":
        # Show steps API already returns the expected format
        return wolfram_result
    elif api_type == "full_results":
        # Extract key information from pods
        normalized = {
            "original_query": wolfram_result.get("original_query", ""),
            "success": wolfram_result.get("success", False),
            "final_answer": None,
            "steps": [],
            "visualizations": [],
            "error": wolfram_result.get("error")
        }

        # Extract final answer from Result pod
        pods = wolfram_result.get("pods", [])
        for pod in pods:
            if pod.get("id") == "Result":
                subpods = pod.get("subpods", [])
                if subpods:
                    normalized["final_answer"] = subpods[0].get("plaintext")

            # Extract visualizations
            elif "plot" in pod.get("id", "").lower():
                for subpod in pod.get("subpods", []):
                    if "img" in subpod:
                        normalized["visualizations"].append({
                            "title": pod.get("title"),
                            "image": subpod["img"]
                        })
        return normalized
    else:
        # For other APIs, return as-is
        return wolfram_result


async def _fetch_steps_if_available(wolfram_result: dict, normalized_result: dict, processed_query: str, original_query: str) -> Optional[List[dict]]:
    """Check if step-by-step solutions are available and fetch them.

    Args:
        wolfram_result: Result from initial Wolfram API call
        normalized_result: Normalized result from _normalize_wolfram_result
        processed_query: The processed/formatted query used for the main API call
        original_query: The original user query

    Returns:
        List of steps if available, None otherwise
    """
    # Check if result has pods that might contain step-by-step solutions
    if not wolfram_result.get("pods"):
        return None

    # Look for pods with step-by-step states
    has_step_states = False
    for pod in wolfram_result["pods"]:
        states = pod.get("states", [])
        for state in states:
            if "Step-by-step" in state.get("name", "") and state.get("stepbystep", False):
                has_step_states = True
                break
        if has_step_states:
            break

    # If step-by-step solutions are available, fetch them
    if has_step_states:
        try:
            logger.info("Step-by-step solutions available, fetching them")
            # Use original query for step fetching, not the processed/formatted one
            async with WolframShowStepsClient() as client:
                steps_result = await client.solve(original_query, show_steps=True)
                steps = steps_result.get("steps")
                if steps:
                    return steps
        except Exception as e:
            logger.warning("Failed to fetch step-by-step solutions", error=str(e))

    # For systems of equations, even if no step states are found, try to generate steps
    if query_classifier._is_system_of_equations(original_query):
        try:
            async with WolframShowStepsClient() as client:
                # Get the final answer from the normalized result
                final_answer = None
                if "final_answer" in normalized_result:
                    final_answer = normalized_result["final_answer"]
                elif wolfram_result.get("pods"):
                    # Try to extract from pods
                    for pod in wolfram_result["pods"]:
                        if pod.get("id") == "Result":
                            subpods = pod.get("subpods", [])
                            if subpods:
                                final_answer = subpods[0].get("plaintext")
                                break

                if final_answer:
                    steps = client._generate_basic_steps(original_query, final_answer)
                    return steps if steps else None
        except Exception as e:
            logger.warning("Failed to generate system steps", error=str(e))

    return None


async def _call_wolfram_api(
    api_type: str,
    query: str,
    params: dict
) -> dict:
    """Call appropriate Wolfram API.

    Args:
        api_type: Type of API to call
        query: Processed query
        params: API parameters

    Returns:
        API result
    """
    if api_type == "llm":
        async with WolframLLMClient() as client:
            return await client.query(query, **params)

    elif api_type == "full_results":
        async with WolframFullResultsClient() as client:
            return await client.query(query, **params)

    elif api_type == "show_steps":
        async with WolframShowStepsClient() as client:
            return await client.solve(query, **params)

    elif api_type == "language_eval":
        async with WolframLanguageEvalClient() as client:
            return await client.evaluate(query, **params)

    else:
        raise ValueError(f"Unknown API type: {api_type}")
