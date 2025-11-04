"""Quiz generator for mathematical topics."""
from typing import Dict, Any, List, Optional
import structlog
import json
from datetime import datetime
import random

from api.openai import GPT5Client

logger = structlog.get_logger()


class QuizGenerator:
    """Generate quizzes from mathematical content."""
    
    def __init__(self):
        self.gpt5_client = GPT5Client()
        
    async def generate_quiz(
        self,
        topic: str,
        concepts: List[str],
        difficulty: str = "intermediate",
        question_count: int = 10,
        question_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a complete quiz on a topic.
        
        Args:
            topic: Main topic of the quiz
            concepts: Related concepts to cover
            difficulty: Difficulty level
            question_count: Number of questions
            question_types: Types of questions to include
            
        Returns:
            Complete quiz structure
        """
        if question_types is None:
            question_types = ["multiple_choice", "true_false", "short_answer", "problem_solving"]
            
        quiz = {
            "id": f"quiz_{datetime.now().timestamp()}",
            "title": f"Quiz: {topic}",
            "topic": topic,
            "concepts": concepts,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat(),
            "time_limit": question_count * 3,  # 3 minutes per question
            "questions": [],
            "total_points": 0
        }
        
        # Distribute question types
        questions_per_type = self._distribute_questions(question_count, question_types)
        
        # Generate questions for each type
        for q_type, count in questions_per_type.items():
            questions = await self._generate_questions_by_type(
                topic, concepts, q_type, count, difficulty
            )
            quiz["questions"].extend(questions)
            
        # Shuffle questions
        random.shuffle(quiz["questions"])
        
        # Assign question numbers and calculate total points
        for i, question in enumerate(quiz["questions"]):
            question["number"] = i + 1
            quiz["total_points"] += question.get("points", 1)
            
        # Generate answer key
        quiz["answer_key"] = self._generate_answer_key(quiz["questions"])
        
        return quiz
        
    def _distribute_questions(
        self, 
        total: int, 
        types: List[str]
    ) -> Dict[str, int]:
        """Distribute questions across types.
        
        Args:
            total: Total questions
            types: Question types
            
        Returns:
            Distribution map
        """
        base_per_type = total // len(types)
        remainder = total % len(types)
        
        distribution = {}
        for i, q_type in enumerate(types):
            distribution[q_type] = base_per_type
            if i < remainder:
                distribution[q_type] += 1
                
        return distribution
        
    async def _generate_questions_by_type(
        self,
        topic: str,
        concepts: List[str],
        question_type: str,
        count: int,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate questions of a specific type.
        
        Args:
            topic: Quiz topic
            concepts: Concepts to cover
            question_type: Type of question
            count: Number of questions
            difficulty: Difficulty level
            
        Returns:
            List of questions
        """
        if question_type == "multiple_choice":
            return await self._generate_multiple_choice(topic, concepts, count, difficulty)
        elif question_type == "true_false":
            return await self._generate_true_false(topic, concepts, count, difficulty)
        elif question_type == "short_answer":
            return await self._generate_short_answer(topic, concepts, count, difficulty)
        elif question_type == "problem_solving":
            return await self._generate_problem_solving(topic, concepts, count, difficulty)
        else:
            return []
            
    async def _generate_multiple_choice(
        self,
        topic: str,
        concepts: List[str],
        count: int,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate multiple choice questions.
        
        Args:
            topic: Topic
            concepts: Concepts
            count: Number of questions
            difficulty: Difficulty
            
        Returns:
            List of MC questions
        """
        prompt = f"""Generate {count} multiple choice questions about {topic}.
        
        Concepts to cover: {', '.join(concepts)}
        Difficulty: {difficulty}
        
        Each question should:
        - Test understanding, not just memorization
        - Have 4 options (A, B, C, D)
        - Have exactly one correct answer
        - Include plausible distractors
        
        Format as JSON array with:
        - question: The question text
        - options: Object with keys A, B, C, D
        - correct_answer: The correct option letter
        - explanation: Why the answer is correct
        - concept: Main concept tested
        - points: Point value (1-3 based on difficulty)
        """
        
        messages = [
            {"role": "system", "content": "You are a quiz question generator."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.8)
            questions = json.loads(response)
            
            # Validate and format
            formatted = []
            for q in questions[:count]:
                if self._validate_mc_question(q):
                    formatted.append({
                        "type": "multiple_choice",
                        "question": q["question"],
                        "options": q["options"],
                        "correct_answer": q["correct_answer"],
                        "explanation": q["explanation"],
                        "concept": q.get("concept", topic),
                        "points": q.get("points", 1)
                    })
                    
            return formatted
            
        except Exception as e:
            logger.error("Failed to generate MC questions", error=str(e))
            return []
            
    def _validate_mc_question(self, question: Dict[str, Any]) -> bool:
        """Validate multiple choice question structure.
        
        Args:
            question: Question to validate
            
        Returns:
            True if valid
        """
        required = ["question", "options", "correct_answer", "explanation"]
        if not all(key in question for key in required):
            return False
            
        options = question.get("options", {})
        if not all(opt in options for opt in ["A", "B", "C", "D"]):
            return False
            
        if question.get("correct_answer") not in ["A", "B", "C", "D"]:
            return False
            
        return True
        
    async def _generate_true_false(
        self,
        topic: str,
        concepts: List[str],
        count: int,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate true/false questions.
        
        Args:
            topic: Topic
            concepts: Concepts
            count: Number of questions
            difficulty: Difficulty
            
        Returns:
            List of T/F questions
        """
        prompt = f"""Generate {count} true/false questions about {topic}.
        
        Concepts: {', '.join(concepts)}
        Difficulty: {difficulty}
        
        Mix of true and false statements.
        Test conceptual understanding.
        
        Format as JSON array with:
        - statement: The statement to evaluate
        - correct_answer: true or false
        - explanation: Why it's true/false
        - concept: Concept tested
        """
        
        messages = [
            {"role": "system", "content": "You are generating true/false questions."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.7)
            questions = json.loads(response)
            
            formatted = []
            for q in questions[:count]:
                if all(key in q for key in ["statement", "correct_answer", "explanation"]):
                    formatted.append({
                        "type": "true_false",
                        "question": q["statement"],
                        "correct_answer": bool(q["correct_answer"]),
                        "explanation": q["explanation"],
                        "concept": q.get("concept", topic),
                        "points": 1
                    })
                    
            return formatted
            
        except Exception as e:
            logger.error("Failed to generate T/F questions", error=str(e))
            return []
            
    async def _generate_short_answer(
        self,
        topic: str,
        concepts: List[str],
        count: int,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate short answer questions.
        
        Args:
            topic: Topic
            concepts: Concepts
            count: Number of questions
            difficulty: Difficulty
            
        Returns:
            List of short answer questions
        """
        prompt = f"""Generate {count} short answer questions about {topic}.
        
        Concepts: {', '.join(concepts)}
        Difficulty: {difficulty}
        
        Questions should:
        - Require 1-3 sentence answers
        - Test understanding and application
        - Be specific and clear
        
        Format as JSON array with:
        - question: The question
        - sample_answer: A good example answer
        - key_points: List of points that should be mentioned
        - concept: Main concept
        - points: 2-5 based on complexity
        """
        
        messages = [
            {"role": "system", "content": "You are generating short answer questions."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.7)
            questions = json.loads(response)
            
            formatted = []
            for q in questions[:count]:
                if all(key in q for key in ["question", "sample_answer"]):
                    formatted.append({
                        "type": "short_answer",
                        "question": q["question"],
                        "sample_answer": q["sample_answer"],
                        "key_points": q.get("key_points", []),
                        "concept": q.get("concept", topic),
                        "points": q.get("points", 3)
                    })
                    
            return formatted
            
        except Exception as e:
            logger.error("Failed to generate short answer questions", error=str(e))
            return []
            
    async def _generate_problem_solving(
        self,
        topic: str,
        concepts: List[str],
        count: int,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate problem-solving questions.
        
        Args:
            topic: Topic
            concepts: Concepts
            count: Number of questions
            difficulty: Difficulty
            
        Returns:
            List of problems
        """
        prompt = f"""Generate {count} problem-solving questions about {topic}.
        
        Concepts: {', '.join(concepts)}
        Difficulty: {difficulty}
        
        Each problem should:
        - Require showing work
        - Have clear setup and requirements
        - Test application of concepts
        
        Format as JSON array with:
        - problem: Problem statement
        - solution: Complete solution with steps
        - hints: List of 2-3 hints
        - concept: Main concept
        - points: 5-10 based on complexity
        """
        
        messages = [
            {"role": "system", "content": "You are generating math problems."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.8)
            questions = json.loads(response)
            
            formatted = []
            for q in questions[:count]:
                if all(key in q for key in ["problem", "solution"]):
                    formatted.append({
                        "type": "problem_solving",
                        "question": q["problem"],
                        "solution": q["solution"],
                        "hints": q.get("hints", []),
                        "concept": q.get("concept", topic),
                        "points": q.get("points", 8)
                    })
                    
            return formatted
            
        except Exception as e:
            logger.error("Failed to generate problems", error=str(e))
            return []
            
    def _generate_answer_key(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer key for quiz.
        
        Args:
            questions: Quiz questions
            
        Returns:
            Answer key
        """
        answer_key = {
            "answers": {},
            "explanations": {},
            "point_breakdown": {}
        }
        
        for q in questions:
            q_num = str(q["number"])
            
            if q["type"] == "multiple_choice":
                answer_key["answers"][q_num] = q["correct_answer"]
            elif q["type"] == "true_false":
                answer_key["answers"][q_num] = q["correct_answer"]
            elif q["type"] == "short_answer":
                answer_key["answers"][q_num] = q["sample_answer"]
            elif q["type"] == "problem_solving":
                answer_key["answers"][q_num] = q["solution"]
                
            answer_key["explanations"][q_num] = q.get("explanation", "")
            answer_key["point_breakdown"][q_num] = q.get("points", 1)
            
        return answer_key
        
    def grade_quiz(
        self,
        quiz: Dict[str, Any],
        student_answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Grade a completed quiz.
        
        Args:
            quiz: Original quiz
            student_answers: Student's answers
            
        Returns:
            Grading results
        """
        results = {
            "total_points": quiz["total_points"],
            "earned_points": 0,
            "percentage": 0,
            "questions": {},
            "feedback": []
        }
        
        answer_key = quiz["answer_key"]["answers"]
        
        for question in quiz["questions"]:
            q_num = str(question["number"])
            student_answer = student_answers.get(q_num)
            correct_answer = answer_key.get(q_num)
            
            is_correct = False
            points_earned = 0
            
            if question["type"] in ["multiple_choice", "true_false"]:
                is_correct = student_answer == correct_answer
                if is_correct:
                    points_earned = question["points"]
                    
            elif question["type"] == "short_answer":
                # For short answer, check key points
                if student_answer:
                    key_points = question.get("key_points", [])
                    points_hit = sum(1 for point in key_points if point.lower() in student_answer.lower())
                    partial_credit = points_hit / len(key_points) if key_points else 0.5
                    points_earned = int(question["points"] * partial_credit)
                    is_correct = partial_credit > 0.7
                    
            elif question["type"] == "problem_solving":
                # For problems, this would need manual grading
                # For now, mark as needs review
                points_earned = 0
                is_correct = None
                
            results["questions"][q_num] = {
                "correct": is_correct,
                "points_earned": points_earned,
                "points_possible": question["points"],
                "student_answer": student_answer,
                "correct_answer": correct_answer
            }
            
            results["earned_points"] += points_earned
            
        results["percentage"] = round(
            (results["earned_points"] / results["total_points"]) * 100, 1
        )
        
        # Generate feedback
        results["feedback"] = self._generate_feedback(results, quiz)
        
        return results
        
    def _generate_feedback(
        self,
        results: Dict[str, Any],
        quiz: Dict[str, Any]
    ) -> List[str]:
        """Generate feedback based on results.
        
        Args:
            results: Grading results
            quiz: Original quiz
            
        Returns:
            List of feedback items
        """
        feedback = []
        
        percentage = results["percentage"]
        
        if percentage >= 90:
            feedback.append("Excellent work! You have a strong grasp of the material.")
        elif percentage >= 80:
            feedback.append("Good job! You understand most concepts well.")
        elif percentage >= 70:
            feedback.append("Satisfactory performance. Review the missed concepts.")
        else:
            feedback.append("You may need additional practice with this material.")
            
        # Identify weak areas
        concepts_missed = {}
        for q_num, result in results["questions"].items():
            if not result["correct"]:
                question = next(q for q in quiz["questions"] if str(q["number"]) == q_num)
                concept = question.get("concept", "Unknown")
                concepts_missed[concept] = concepts_missed.get(concept, 0) + 1
                
        if concepts_missed:
            weak_concepts = sorted(concepts_missed.items(), key=lambda x: x[1], reverse=True)
            feedback.append(f"Focus on reviewing: {', '.join([c[0] for c in weak_concepts[:3]])}")
            
        return feedback
