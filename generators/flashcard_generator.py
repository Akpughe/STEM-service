"""Flashcard generator for mathematical concepts."""
from typing import Dict, Any, List
import structlog
import json
from datetime import datetime

from api.openai import GPT5Client

logger = structlog.get_logger()


class FlashcardGenerator:
    """Generate flashcards from mathematical problems and solutions."""
    
    def __init__(self):
        self.gpt5_client = GPT5Client()
        
    async def generate_flashcards(
        self,
        problem: str,
        solution: str,
        concepts: List[str],
        difficulty: str = "intermediate",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate flashcards from a problem and solution.
        
        Args:
            problem: Original problem
            solution: Problem solution
            concepts: Related concepts
            difficulty: Difficulty level
            count: Number of flashcards to generate
            
        Returns:
            List of flashcards
        """
        flashcards = []
        
        # Generate concept-based flashcards
        concept_cards = await self._generate_concept_cards(concepts, count // 2)
        flashcards.extend(concept_cards)
        
        # Generate problem-specific flashcards
        problem_cards = await self._generate_problem_cards(
            problem, 
            solution, 
            count - len(concept_cards)
        )
        flashcards.extend(problem_cards)
        
        # Add metadata to all cards
        for i, card in enumerate(flashcards):
            card["id"] = f"card_{datetime.now().timestamp()}_{i}"
            card["difficulty"] = difficulty
            card["created_at"] = datetime.now().isoformat()
            card["review_count"] = 0
            card["last_reviewed"] = None
            
        return flashcards
        
    async def _generate_concept_cards(
        self,
        concepts: List[str],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate concept-based flashcards.
        
        Args:
            concepts: List of concepts
            count: Number of cards
            
        Returns:
            List of flashcards
        """
        if not concepts:
            return []
            
        prompt = f"""Create {count} flashcards for these mathematical concepts: {', '.join(concepts)}
        
        Each flashcard should test understanding of a key concept.
        
        Format as JSON array with each card having:
        - question: Clear, specific question
        - answer: Concise, accurate answer
        - concept: The main concept being tested
        - type: "definition", "formula", or "application"
        
        Make questions progressively challenging."""
        
        messages = [
            {"role": "system", "content": "You are a math educator creating educational flashcards."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.7)
            cards = json.loads(response)
            
            # Validate and clean cards
            valid_cards = []
            for card in cards[:count]:
                if all(key in card for key in ["question", "answer"]):
                    valid_cards.append({
                        "question": card["question"],
                        "answer": card["answer"],
                        "concept": card.get("concept", concepts[0] if concepts else ""),
                        "type": card.get("type", "definition"),
                        "category": "concept"
                    })
                    
            return valid_cards
            
        except Exception as e:
            logger.error("Failed to generate concept cards", error=str(e))
            return []
            
    async def _generate_problem_cards(
        self,
        problem: str,
        solution: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate problem-specific flashcards.
        
        Args:
            problem: Original problem
            solution: Solution
            count: Number of cards
            
        Returns:
            List of flashcards
        """
        prompt = f"""Create {count} flashcards based on this problem and solution:
        
        Problem: {problem}
        Solution: {solution}
        
        Create cards that test:
        1. Understanding of the problem setup
        2. Key steps in the solution
        3. The final answer
        4. Alternative approaches (if applicable)
        
        Format as JSON array with:
        - question: The flashcard question
        - answer: The correct answer
        - hint: Optional hint for difficult questions
        - type: "problem_setup", "solution_step", "final_answer", or "alternative_method"
        """
        
        messages = [
            {"role": "system", "content": "You are creating flashcards from a solved problem."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.6)
            cards = json.loads(response)
            
            valid_cards = []
            for card in cards[:count]:
                if all(key in card for key in ["question", "answer"]):
                    valid_cards.append({
                        "question": card["question"],
                        "answer": card["answer"],
                        "hint": card.get("hint", ""),
                        "type": card.get("type", "solution_step"),
                        "category": "problem_specific"
                    })
                    
            return valid_cards
            
        except Exception as e:
            logger.error("Failed to generate problem cards", error=str(e))
            return []
            
    async def generate_spaced_repetition_schedule(
        self,
        flashcards: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate spaced repetition schedule for flashcards.
        
        Args:
            flashcards: List of flashcards
            
        Returns:
            Spaced repetition schedule
        """
        schedule = {
            "total_cards": len(flashcards),
            "daily_new_cards": min(5, len(flashcards)),
            "review_intervals": [1, 3, 7, 14, 30, 90],  # Days
            "cards_by_difficulty": {},
            "estimated_completion_days": 0
        }
        
        # Group by difficulty
        for card in flashcards:
            diff = card.get("difficulty", "intermediate")
            if diff not in schedule["cards_by_difficulty"]:
                schedule["cards_by_difficulty"][diff] = []
            schedule["cards_by_difficulty"][diff].append(card["id"])
            
        # Calculate estimated completion
        total_reviews = len(flashcards) * len(schedule["review_intervals"])
        schedule["estimated_completion_days"] = (
            len(flashcards) // schedule["daily_new_cards"] + 
            max(schedule["review_intervals"])
        )
        
        return schedule
        
    def format_for_export(
        self,
        flashcards: List[Dict[str, Any]],
        format_type: str = "anki"
    ) -> str:
        """Format flashcards for export to external systems.
        
        Args:
            flashcards: List of flashcards
            format_type: Export format (anki, csv, json)
            
        Returns:
            Formatted string
        """
        if format_type == "anki":
            return self._format_anki(flashcards)
        elif format_type == "csv":
            return self._format_csv(flashcards)
        else:
            return json.dumps(flashcards, indent=2)
            
    def _format_anki(self, flashcards: List[Dict[str, Any]]) -> str:
        """Format for Anki import.
        
        Args:
            flashcards: List of flashcards
            
        Returns:
            Anki-formatted string
        """
        lines = []
        for card in flashcards:
            # Anki format: question;answer;tags
            question = card["question"].replace(";", "\\;")
            answer = card["answer"].replace(";", "\\;")
            tags = f"{card.get('concept', '')} {card.get('type', '')} {card.get('difficulty', '')}"
            
            lines.append(f"{question};{answer};{tags.strip()}")
            
        return "\n".join(lines)
        
    def _format_csv(self, flashcards: List[Dict[str, Any]]) -> str:
        """Format as CSV.
        
        Args:
            flashcards: List of flashcards
            
        Returns:
            CSV string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["question", "answer", "hint", "concept", "type", "difficulty"],
            extrasaction="ignore"
        )
        
        writer.writeheader()
        for card in flashcards:
            writer.writerow(card)
            
        return output.getvalue()
        
    async def generate_review_session(
        self,
        flashcards: List[Dict[str, Any]],
        session_length: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate a review session from flashcards.
        
        Args:
            flashcards: Available flashcards
            session_length: Number of cards in session
            
        Returns:
            Review session cards
        """
        # Sort by priority (least recently reviewed first)
        sorted_cards = sorted(
            flashcards,
            key=lambda x: x.get("last_reviewed", "1900-01-01")
        )
        
        # Select cards for session
        session_cards = sorted_cards[:session_length]
        
        # Mix in some random cards for variety
        import random
        if len(flashcards) > session_length:
            random_cards = random.sample(
                flashcards[session_length:],
                min(3, len(flashcards) - session_length)
            )
            session_cards = session_cards[:-len(random_cards)] + random_cards
            
        # Shuffle the session
        random.shuffle(session_cards)
        
        return session_cards
