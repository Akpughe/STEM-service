"""Result enhancement processor for educational content."""
from typing import Dict, Any, List, Optional
import structlog
import json

from api.openai import GPT5Client

logger = structlog.get_logger()


class ResultEnhancer:
    """Enhance Wolfram results with educational content."""
    
    def __init__(self):
        self.gpt5_client = GPT5Client()
        
    async def enhance_result(
        self,
        wolfram_result: Dict[str, Any],
        original_query: str,
        student_level: str = "undergraduate",
        include_educational: bool = True
    ) -> Dict[str, Any]:
        """Enhance Wolfram result with explanations and educational content.
        
        Args:
            wolfram_result: Raw Wolfram API result
            original_query: Original user query
            student_level: Educational level
            include_educational: Whether to include educational content
            
        Returns:
            Enhanced result
        """
        # Get basic enhancement
        enhancement = await self.gpt5_client.enhance_wolfram_result(
            wolfram_result,
            original_query,
            student_level
        )
        
        # Build complete enhanced result
        enhanced_result = {
            "original_query": original_query,
            "wolfram_result": wolfram_result,
            "explanation": enhancement.get("explanation", ""),
            "concepts": enhancement.get("concepts", []),
            "difficulty": enhancement.get("difficulty_level", "intermediate"),
            "prerequisites": enhancement.get("prerequisites", [])
        }
        
        # Add educational content if requested
        if include_educational:
            enhanced_result["educational_content"] = await self._generate_educational_content(
                wolfram_result,
                original_query,
                student_level
            )
            
        # Add practice problems
        enhanced_result["practice_problems"] = await self._generate_practice_problems(
            original_query,
            wolfram_result,
            enhanced_result["difficulty"]
        )
        
        return enhanced_result
        
    async def _generate_educational_content(
        self,
        wolfram_result: Dict[str, Any],
        original_query: str,
        student_level: str
    ) -> Dict[str, Any]:
        """Generate educational content.
        
        Args:
            wolfram_result: Wolfram result
            original_query: Original query
            student_level: Student level
            
        Returns:
            Educational content
        """
        content = {
            "summary": "",
            "key_insights": [],
            "common_mistakes": [],
            "tips": [],
            "real_world_applications": []
        }
        
        # Generate summary
        summary_prompt = f"""Create a brief summary (2-3 sentences) of this {student_level}-level 
        math problem and its solution:
        
        Problem: {original_query}
        Solution: {self._extract_solution(wolfram_result)}"""
        
        messages = [
            {"role": "system", "content": "You are a concise math educator."},
            {"role": "user", "content": summary_prompt}
        ]
        
        try:
            # Generate summary with better error handling
            try:
                summary = await self.gpt5_client.complete(messages, temperature=0.5, max_completion_tokens=150)
                content["summary"] = summary.strip() if summary else ""
            except Exception as e:
                logger.warning("Failed to generate summary", error=str(e))
                content["summary"] = f"This is a {student_level}-level math problem involving equation solving."

            # Generate other educational content with individual error handling
            try:
                content["key_insights"] = await self._generate_key_insights(wolfram_result, original_query)
            except Exception as e:
                logger.warning("Failed to generate key insights", error=str(e))
                content["key_insights"] = ["Solving equations involves isolating the variable using inverse operations."]

            try:
                content["common_mistakes"] = await self._generate_common_mistakes(original_query)
            except Exception as e:
                logger.warning("Failed to generate common mistakes", error=str(e))
                content["common_mistakes"] = ["Forgetting to perform the same operation on both sides of the equation."]

            try:
                content["tips"] = await self._generate_tips(original_query, wolfram_result)
            except Exception as e:
                logger.warning("Failed to generate tips", error=str(e))
                content["tips"] = ["Always check your solution by substituting it back into the original equation."]

            try:
                content["real_world_applications"] = await self._generate_applications(original_query)
            except Exception as e:
                logger.warning("Failed to generate applications", error=str(e))
                content["real_world_applications"] = ["Equation solving is used in physics, engineering, and financial calculations."]

        except Exception as e:
            logger.error("Failed to generate educational content", error=str(e))
            
        return content
        
    def _extract_solution(self, wolfram_result: Dict[str, Any]) -> str:
        """Extract solution from Wolfram result.
        
        Args:
            wolfram_result: Wolfram result
            
        Returns:
            Solution string
        """
        if "final_answer" in wolfram_result:
            return str(wolfram_result["final_answer"])
        elif "result" in wolfram_result:
            return str(wolfram_result["result"])
        elif "pods" in wolfram_result and wolfram_result["pods"]:
            # Look for Result pod
            for pod in wolfram_result["pods"]:
                if pod.get("id") == "Result" or "result" in pod.get("title", "").lower():
                    subpods = pod.get("subpods", [])
                    if subpods:
                        return subpods[0].get("plaintext", "No solution found")
        return "Solution not available"
        
    async def _generate_key_insights(
        self,
        wolfram_result: Dict[str, Any],
        original_query: str
    ) -> List[str]:
        """Generate key insights.
        
        Args:
            wolfram_result: Wolfram result
            original_query: Original query
            
        Returns:
            List of insights
        """
        prompt = f"""List 2-3 key mathematical insights from this problem and solution.
        Each insight should be one clear sentence.
        
        Problem: {original_query}
        Solution: {self._extract_solution(wolfram_result)}
        
        Format: Return only a JSON array of strings."""
        
        messages = [
            {"role": "system", "content": "You are a math educator focused on insights."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.5)
            insights = json.loads(response)
            return insights[:3]
        except:
            return []
            
    async def _generate_common_mistakes(self, original_query: str) -> List[str]:
        """Generate common mistakes.
        
        Args:
            original_query: Original query
            
        Returns:
            List of common mistakes
        """
        prompt = f"""List 2-3 common mistakes students make with this type of problem.
        Be specific and brief.
        
        Problem type: {original_query}
        
        Format: Return only a JSON array of strings."""
        
        messages = [
            {"role": "system", "content": "You are a math educator."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.5)
            mistakes = json.loads(response)
            return mistakes[:3]
        except:
            return []
            
    async def _generate_tips(
        self,
        original_query: str,
        wolfram_result: Dict[str, Any]
    ) -> List[str]:
        """Generate solving tips.
        
        Args:
            original_query: Original query
            wolfram_result: Wolfram result
            
        Returns:
            List of tips
        """
        # Simple tips based on problem type
        tips = []
        query_lower = original_query.lower()
        
        if "integral" in query_lower:
            tips.append("Look for substitution opportunities to simplify the integral")
            tips.append("Check if integration by parts might be helpful")
        elif "derivative" in query_lower:
            tips.append("Apply chain rule carefully for composite functions")
            tips.append("Remember the product rule for multiplied functions")
        elif "solve" in query_lower:
            tips.append("Isolate the variable step by step")
            tips.append("Check your solution by substituting back")
            
        return tips[:2]
        
    async def _generate_applications(self, original_query: str) -> List[str]:
        """Generate real-world applications.
        
        Args:
            original_query: Original query
            
        Returns:
            List of applications
        """
        prompt = f"""List 1-2 real-world applications of this mathematical concept.
        Be specific and relatable.
        
        Concept from: {original_query}
        
        Format: Return only a JSON array of strings."""
        
        messages = [
            {"role": "system", "content": "You are a math educator connecting math to real life."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.7)
            applications = json.loads(response)
            return applications[:2]
        except:
            return []
            
    async def _generate_practice_problems(
        self,
        original_query: str,
        wolfram_result: Dict[str, Any],
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate practice problems.
        
        Args:
            original_query: Original query
            wolfram_result: Wolfram result
            difficulty: Difficulty level
            
        Returns:
            List of practice problems
        """
        prompt = f"""Generate 3 practice problems similar to this one.
        Vary the difficulty slightly around {difficulty} level.
        
        Original problem: {original_query}
        
        Format each problem as JSON with fields:
        - problem: The problem statement
        - hint: A helpful hint
        - difficulty: easy/medium/hard
        
        Return a JSON array of 3 problems."""
        
        messages = [
            {"role": "system", "content": "You are a math problem generator."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.gpt5_client.complete(messages, temperature=0.8)
            problems = json.loads(response)
            
            # Add problem numbers
            for i, problem in enumerate(problems):
                problem["number"] = i + 1
                
            return problems[:3]
        except Exception as e:
            logger.error("Failed to generate practice problems", error=str(e))
            return []
            
    async def format_for_display(
        self,
        enhanced_result: Dict[str, Any],
        format_type: str = "markdown"
    ) -> str:
        """Format enhanced result for display.
        
        Args:
            enhanced_result: Enhanced result
            format_type: Output format
            
        Returns:
            Formatted string
        """
        if format_type == "markdown":
            return self._format_markdown(enhanced_result)
        elif format_type == "html":
            return self._format_html(enhanced_result)
        else:
            return json.dumps(enhanced_result, indent=2)
            
    def _format_markdown(self, result: Dict[str, Any]) -> str:
        """Format as Markdown.
        
        Args:
            result: Enhanced result
            
        Returns:
            Markdown string
        """
        md = []
        
        # Header
        md.append(f"# Problem: {result['original_query']}\n")
        
        # Solution
        if "wolfram_result" in result:
            solution = self._extract_solution(result["wolfram_result"])
            md.append(f"## Solution\n\n{solution}\n")
            
        # Explanation
        if result.get("explanation"):
            md.append(f"## Explanation\n\n{result['explanation']}\n")
            
        # Educational content
        if "educational_content" in result:
            edu = result["educational_content"]
            
            if edu.get("summary"):
                md.append(f"### Summary\n\n{edu['summary']}\n")
                
            if edu.get("key_insights"):
                md.append("### Key Insights\n")
                for insight in edu["key_insights"]:
                    md.append(f"- {insight}")
                md.append("")
                
            if edu.get("common_mistakes"):
                md.append("### Common Mistakes to Avoid\n")
                for mistake in edu["common_mistakes"]:
                    md.append(f"- {mistake}")
                md.append("")
                
        # Practice problems
        if result.get("practice_problems"):
            md.append("## Practice Problems\n")
            for problem in result["practice_problems"]:
                md.append(f"**Problem {problem['number']}** ({problem.get('difficulty', 'medium')})")
                md.append(f"{problem['problem']}")
                if problem.get("hint"):
                    md.append(f"*Hint: {problem['hint']}*")
                md.append("")
                
        return "\n".join(md)
        
    def _format_html(self, result: Dict[str, Any]) -> str:
        """Format as HTML.
        
        Args:
            result: Enhanced result
            
        Returns:
            HTML string
        """
        # Simple HTML formatting - enhance as needed
        html = f"""
        <div class="math-result">
            <h1>Problem: {result['original_query']}</h1>
            
            <div class="solution">
                <h2>Solution</h2>
                <p>{self._extract_solution(result.get('wolfram_result', {}))}</p>
            </div>
            
            <div class="explanation">
                <h2>Explanation</h2>
                <p>{result.get('explanation', '')}</p>
            </div>
        </div>
        """
        
        return html
