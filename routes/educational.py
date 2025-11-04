"""Educational content routes."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import structlog
from pydantic import BaseModel, Field

from generators import FlashcardGenerator, QuizGenerator, ExplanationGenerator

logger = structlog.get_logger()
router = APIRouter()


# Request/Response models
class FlashcardRequest(BaseModel):
    """Flashcard generation request."""
    problem: str = Field(..., description="Problem statement")
    solution: str = Field(..., description="Problem solution")
    concepts: List[str] = Field(default=[], description="Related concepts")
    difficulty: str = Field(default="intermediate", description="Difficulty level")
    count: int = Field(default=5, ge=1, le=20, description="Number of flashcards")


class QuizRequest(BaseModel):
    """Quiz generation request."""
    topic: str = Field(..., description="Quiz topic")
    concepts: List[str] = Field(..., description="Concepts to cover")
    difficulty: str = Field(default="intermediate", description="Difficulty level")
    question_count: int = Field(default=10, ge=5, le=30, description="Number of questions")
    question_types: Optional[List[str]] = Field(default=None, description="Types of questions")


class ExplanationRequest(BaseModel):
    """Concept explanation request."""
    concept: str = Field(..., description="Concept to explain")
    context: Optional[str] = Field(default=None, description="Context where concept appears")
    examples_count: int = Field(default=2, ge=1, le=5, description="Number of examples")


class QuizSubmission(BaseModel):
    """Quiz answer submission."""
    quiz_id: str = Field(..., description="Quiz ID")
    answers: dict = Field(..., description="Student answers by question number")


# Initialize generators
flashcard_generator = FlashcardGenerator()
quiz_generator = QuizGenerator()
explanation_generator = ExplanationGenerator()


@router.post("/flashcards")
async def generate_flashcards(request: FlashcardRequest):
    """Generate flashcards from a problem and solution."""
    try:
        logger.info("Generating flashcards", problem=request.problem[:50])
        
        flashcards = await flashcard_generator.generate_flashcards(
            problem=request.problem,
            solution=request.solution,
            concepts=request.concepts,
            difficulty=request.difficulty,
            count=request.count
        )
        
        # Generate spaced repetition schedule
        schedule = await flashcard_generator.generate_spaced_repetition_schedule(flashcards)
        
        return {
            "success": True,
            "flashcards": flashcards,
            "schedule": schedule,
            "export_formats": ["anki", "csv", "json"]
        }
        
    except Exception as e:
        logger.error("Failed to generate flashcards", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flashcards/export")
async def export_flashcards(
    flashcards: List[dict],
    format_type: str = "anki"
):
    """Export flashcards in specified format."""
    try:
        if format_type not in ["anki", "csv", "json"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Choose from: anki, csv, json"
            )
            
        exported = flashcard_generator.format_for_export(flashcards, format_type)
        
        return {
            "success": True,
            "format": format_type,
            "data": exported,
            "filename": f"flashcards.{format_type if format_type != 'anki' else 'txt'}"
        }
        
    except Exception as e:
        logger.error("Failed to export flashcards", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quiz")
async def generate_quiz(request: QuizRequest):
    """Generate a quiz on a mathematical topic."""
    try:
        logger.info("Generating quiz", topic=request.topic)
        
        quiz = await quiz_generator.generate_quiz(
            topic=request.topic,
            concepts=request.concepts,
            difficulty=request.difficulty,
            question_count=request.question_count,
            question_types=request.question_types
        )
        
        # Remove answer key from response (store it server-side in production)
        quiz_response = {k: v for k, v in quiz.items() if k != "answer_key"}
        
        return {
            "success": True,
            "quiz": quiz_response,
            "submission_endpoint": f"/educational/quiz/{quiz['id']}/submit"
        }
        
    except Exception as e:
        logger.error("Failed to generate quiz", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quiz/{quiz_id}/submit")
async def submit_quiz(submission: QuizSubmission):
    """Submit and grade a quiz."""
    try:
        # In production, retrieve quiz from storage
        # For now, we'll return a mock grading
        
        logger.info("Grading quiz submission", quiz_id=submission.quiz_id)
        
        # Mock grading result
        results = {
            "quiz_id": submission.quiz_id,
            "total_points": 100,
            "earned_points": 85,
            "percentage": 85.0,
            "questions": {
                "1": {"correct": True, "points_earned": 10, "points_possible": 10},
                "2": {"correct": True, "points_earned": 10, "points_possible": 10},
                "3": {"correct": False, "points_earned": 0, "points_possible": 10},
                "4": {"correct": True, "points_earned": 8, "points_possible": 10},
                "5": {"correct": True, "points_earned": 10, "points_possible": 10}
            },
            "feedback": [
                "Great job! You understand the core concepts well.",
                "Review question 3 - remember to check your calculations."
            ]
        }
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error("Failed to grade quiz", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain/concept")
async def explain_concept(request: ExplanationRequest):
    """Generate explanation for a mathematical concept."""
    try:
        logger.info("Explaining concept", concept=request.concept)
        
        explanation = await explanation_generator.generate_concept_explanation(
            concept=request.concept,
            context=request.context,
            examples_count=request.examples_count
        )
        
        # Generate analogy
        analogy = await explanation_generator.generate_analogy(
            request.concept,
            target_audience="general"
        )
        
        explanation["analogy"] = analogy
        
        return {
            "success": True,
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error("Failed to explain concept", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain/visual")
async def explain_visual(
    mathematical_object: str,
    include_construction: bool = True
):
    """Generate visual description for mathematical object."""
    try:
        logger.info("Generating visual description", object=mathematical_object)
        
        description = await explanation_generator.generate_visual_description(
            mathematical_object=mathematical_object,
            include_construction=include_construction
        )
        
        return {
            "success": True,
            "visual_description": description
        }
        
    except Exception as e:
        logger.error("Failed to generate visual description", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/practice-session")
async def generate_practice_session(
    topic: str,
    duration_minutes: int = 30,
    difficulty: str = "intermediate"
):
    """Generate a practice session with mixed content."""
    try:
        logger.info("Generating practice session", topic=topic)
        
        # Calculate content distribution
        flashcard_count = duration_minutes // 3
        quiz_questions = duration_minutes // 2
        
        # Generate session content
        session = {
            "topic": topic,
            "duration_minutes": duration_minutes,
            "difficulty": difficulty,
            "components": {
                "warmup_flashcards": flashcard_count // 2,
                "quiz_questions": quiz_questions,
                "review_flashcards": flashcard_count // 2
            },
            "estimated_completion": f"{duration_minutes} minutes",
            "learning_objectives": [
                f"Master key concepts in {topic}",
                f"Practice problem-solving techniques",
                f"Identify areas for improvement"
            ]
        }
        
        return {
            "success": True,
            "practice_session": session
        }
        
    except Exception as e:
        logger.error("Failed to generate practice session", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
