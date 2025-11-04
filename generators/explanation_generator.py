"""Explanation generator for mathematical concepts and solutions."""
from typing import Dict, Any, List, Optional
import structlog

from api.openai import GPT5Client

logger = structlog.get_logger()


class ExplanationGenerator:
    """Generate educational explanations for mathematical content."""
    
    def __init__(self):
        self.gpt5_client = GPT5Client()
        
    async def generate_step_explanation(
        self,
        steps: List[Dict[str, Any]],
        problem: str,
        student_level: str = "undergraduate"
    ) -> List[Dict[str, Any]]:
        """Generate explanations for each step in a solution.
        
        Args:
            steps: List of solution steps
            problem: Original problem
            student_level: Educational level
            
        Returns:
            Steps with explanations
        """
        enhanced_steps = []
        
        for i, step in enumerate(steps):
            explanation = await self._explain_single_step(
                step, 
                problem, 
                i, 
                len(steps),
                student_level
            )
            
            enhanced_step = {
                **step,
                "explanation": explanation["explanation"],
                "why_this_step": explanation["why"],
                "common_errors": explanation["common_errors"]
            }
            
            enhanced_steps.append(enhanced_step)
            
        return enhanced_steps
        
    async def _explain_single_step(
        self,
        step: Dict[str, Any],
        problem: str,
        step_index: int,
        total_steps: int,
        student_level: str
    ) -> Dict[str, Any]:
        """Explain a single solution step.
        
        Args:
            step: Step to explain
            problem: Original problem
            step_index: Step number
            total_steps: Total number of steps
            student_level: Educational level
            
        Returns:
            Step explanation
        """
        prompt = f"""Explain this step in solving the problem for a {student_level} student:
        
        Problem: {problem}
        Step {step_index + 1} of {total_steps}: {step.get('description', step.get('math', ''))}
        
        Provide:
        1. A clear explanation of what this step does
        2. Why this step is necessary
        3. One common error students make at this step
        
        Be concise but thorough."""
        
        messages = [
            {"role": "system", "content": "You are a patient math tutor."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.6)
            
            # Parse response into components
            lines = response.strip().split('\n')
            
            explanation = ""
            why = ""
            common_error = ""
            
            current_section = None
            for line in lines:
                if "explanation" in line.lower() or line.startswith("1."):
                    current_section = "explanation"
                elif "why" in line.lower() or line.startswith("2."):
                    current_section = "why"
                elif "error" in line.lower() or line.startswith("3."):
                    current_section = "error"
                elif line.strip():
                    if current_section == "explanation":
                        explanation += line + " "
                    elif current_section == "why":
                        why += line + " "
                    elif current_section == "error":
                        common_error += line + " "
                        
            return {
                "explanation": explanation.strip() or response,
                "why": why.strip() or "This step follows from the previous work.",
                "common_errors": [common_error.strip()] if common_error else []
            }
            
        except Exception as e:
            logger.error("Failed to explain step", error=str(e))
            return {
                "explanation": "Step explanation unavailable",
                "why": "",
                "common_errors": []
            }
            
    async def generate_concept_explanation(
        self,
        concept: str,
        context: Optional[str] = None,
        examples_count: int = 2
    ) -> Dict[str, Any]:
        """Generate explanation for a mathematical concept.
        
        Args:
            concept: Concept to explain
            context: Optional context where concept appears
            examples_count: Number of examples to include
            
        Returns:
            Concept explanation
        """
        prompt = f"""Explain the mathematical concept: {concept}
        
        {f'In the context of: {context}' if context else ''}
        
        Include:
        1. Definition in simple terms
        2. Why it's important
        3. {examples_count} clear examples
        4. Common misconceptions
        5. Related concepts
        
        Make it accessible to undergraduate students."""
        
        messages = [
            {"role": "system", "content": "You are explaining mathematical concepts clearly."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.7)
            
            return {
                "concept": concept,
                "explanation": response,
                "examples": await self._extract_examples(response),
                "related_concepts": await self._extract_related_concepts(response)
            }
            
        except Exception as e:
            logger.error("Failed to explain concept", error=str(e))
            return {
                "concept": concept,
                "explanation": f"Unable to generate explanation for {concept}",
                "examples": [],
                "related_concepts": []
            }
            
    async def _extract_examples(self, text: str) -> List[str]:
        """Extract examples from explanation text.
        
        Args:
            text: Explanation text
            
        Returns:
            List of examples
        """
        examples = []
        lines = text.split('\n')
        
        in_example = False
        current_example = ""
        
        for line in lines:
            if any(marker in line.lower() for marker in ["example", "for instance", "e.g."]):
                in_example = True
                current_example = line
            elif in_example and line.strip():
                current_example += " " + line
            elif in_example and not line.strip():
                if current_example:
                    examples.append(current_example.strip())
                    current_example = ""
                in_example = False
                
        if current_example:
            examples.append(current_example.strip())
            
        return examples[:3]  # Limit to 3 examples
        
    async def _extract_related_concepts(self, text: str) -> List[str]:
        """Extract related concepts from text.
        
        Args:
            text: Explanation text
            
        Returns:
            List of related concepts
        """
        prompt = f"""From this explanation, extract 2-4 related mathematical concepts mentioned.
        Return only a comma-separated list.
        
        Text: {text[:500]}..."""
        
        messages = [
            {"role": "system", "content": "Extract mathematical concepts."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.3, max_completion_tokens=50)
            concepts = [c.strip() for c in response.split(",")]
            return concepts[:4]
        except:
            return []
            
    async def generate_analogy(
        self,
        concept: str,
        target_audience: str = "general"
    ) -> str:
        """Generate an analogy for a mathematical concept.
        
        Args:
            concept: Mathematical concept
            target_audience: Target audience type
            
        Returns:
            Analogy explanation
        """
        audience_context = {
            "general": "everyday life",
            "engineering": "engineering applications",
            "physics": "physical phenomena",
            "computer_science": "programming and algorithms",
            "business": "business and finance"
        }
        
        context = audience_context.get(target_audience, "everyday life")
        
        prompt = f"""Create a clear analogy to explain {concept} using {context}.
        
        The analogy should:
        - Be relatable and easy to understand
        - Accurately represent the mathematical concept
        - Help build intuition
        
        Format: Start with "Think of it like..." and keep it under 100 words."""
        
        messages = [
            {"role": "system", "content": "You create intuitive analogies for math concepts."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.8)
            return response
        except:
            return f"Think of {concept} as a mathematical tool that helps us understand relationships."
            
    async def generate_visual_description(
        self,
        mathematical_object: str,
        include_construction: bool = True
    ) -> Dict[str, Any]:
        """Generate description for visualizing mathematical objects.
        
        Args:
            mathematical_object: Object to visualize
            include_construction: Include construction steps
            
        Returns:
            Visual description
        """
        prompt = f"""Describe how to visualize: {mathematical_object}
        
        Include:
        1. What it looks like
        2. Key visual features
        3. How it changes with parameters
        {f'4. Step-by-step construction' if include_construction else ''}
        
        Be specific about shapes, colors, and spatial relationships."""
        
        messages = [
            {"role": "system", "content": "You describe mathematical visualizations clearly."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.6)
            
            return {
                "object": mathematical_object,
                "description": response,
                "key_features": self._extract_visual_features(response),
                "construction_steps": self._extract_construction_steps(response) if include_construction else []
            }
            
        except Exception as e:
            logger.error("Failed to generate visual description", error=str(e))
            return {
                "object": mathematical_object,
                "description": "Visual description unavailable",
                "key_features": [],
                "construction_steps": []
            }
            
    def _extract_visual_features(self, text: str) -> List[str]:
        """Extract key visual features from description.
        
        Args:
            text: Description text
            
        Returns:
            List of features
        """
        features = []
        
        # Look for descriptive keywords
        keywords = ["looks like", "appears", "shaped", "color", "size", "position", "angle"]
        
        lines = text.split('.')
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                features.append(line.strip())
                
        return features[:5]
        
    def _extract_construction_steps(self, text: str) -> List[str]:
        """Extract construction steps from description.
        
        Args:
            text: Description text
            
        Returns:
            List of steps
        """
        steps = []
        
        lines = text.split('\n')
        for line in lines:
            # Look for step indicators
            if any(indicator in line.lower() for indicator in ["step", "first", "then", "next", "finally"]):
                steps.append(line.strip())
                
        return steps
