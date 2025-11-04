"""Query classification and routing system."""
from typing import Dict, Any, List, Optional, Tuple
import re
import structlog
from enum import Enum

logger = structlog.get_logger()


class QueryType(Enum):
    """Types of mathematical queries."""
    SIMPLE_CALCULATION = "simple_calculation"
    STEP_BY_STEP_MATH = "step_by_step_math"
    PLOTTING = "plotting"
    EQUATION_SOLVING = "equation_solving"
    DATA_ANALYSIS = "data_analysis"
    PHYSICS_ENGINEERING = "physics_engineering"
    SYMBOLIC_MATH = "symbolic_math"
    COMPLEX_ANALYSIS = "complex_analysis"
    NATURAL_LANGUAGE = "natural_language"


class WolframAPI(Enum):
    """Wolfram API types for routing."""
    LLM = "llm"
    FULL_RESULTS = "full_results"
    SHOW_STEPS = "show_steps"
    LANGUAGE_EVAL = "language_eval"


class QueryClassifier:
    """Classify and route queries to appropriate Wolfram APIs."""
    
    def __init__(self):
        # Keywords for classification
        self.step_keywords = [
            "step", "steps", "show work", "derive", "proof", "explain how",
            "walkthrough", "solution process", "show me how"
        ]
        
        self.plot_keywords = [
            "plot", "graph", "visualize", "draw", "sketch", "chart",
            "diagram", "curve", "function graph", "3d plot"
        ]
        
        self.solve_keywords = [
            "solve", "find", "calculate", "compute", "evaluate",
            "what is", "determine", "find the value"
        ]
        
        self.engineering_keywords = [
            "circuit", "impedance", "resistance", "capacitor", "inductor",
            "frequency", "transfer function", "bode", "nyquist", "control",
            "signal", "filter", "amplifier", "voltage", "current"
        ]
        
        self.calculus_keywords = [
            "derivative", "integral", "limit", "differentiate", "integrate",
            "d/dx", "∫", "lim", "partial derivative", "gradient"
        ]
        
        self.complex_analysis_keywords = [
            "contour integral", "residue theorem", "complex analysis", "analytic function",
            "holomorphic", "meromorphic", "pole", "residue", "cauchy", "laurent series",
            "complex plane", "∮", "line integral", "path integral", "branch cut"
        ]
        
    def classify_query(self, query: str) -> Tuple[QueryType, WolframAPI]:
        """Classify query and determine appropriate API.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (QueryType, WolframAPI)
        """
        query_lower = query.lower()
        
        # Check for plotting requests
        if self._contains_keywords(query_lower, self.plot_keywords):
            return QueryType.PLOTTING, WolframAPI.LANGUAGE_EVAL
            
        # Check for step-by-step requests
        if self._contains_keywords(query_lower, self.step_keywords):
            return QueryType.STEP_BY_STEP_MATH, WolframAPI.SHOW_STEPS
            
        # Check for complex analysis (highest priority for advanced topics)
        if self._contains_keywords(query_lower, self.complex_analysis_keywords):
            return QueryType.COMPLEX_ANALYSIS, WolframAPI.FULL_RESULTS
            
        # Check for engineering/physics
        if self._contains_keywords(query_lower, self.engineering_keywords):
            return QueryType.PHYSICS_ENGINEERING, WolframAPI.LLM
            
        # Check for calculus
        if self._contains_keywords(query_lower, self.calculus_keywords):
            if any(word in query_lower for word in self.step_keywords):
                return QueryType.STEP_BY_STEP_MATH, WolframAPI.SHOW_STEPS
            else:
                return QueryType.SYMBOLIC_MATH, WolframAPI.FULL_RESULTS
                
        # Check for equation solving
        if "=" in query or self._contains_keywords(query_lower, ["equation", "solve for"]):
            # Use full results for systems of equations to get proper solutions
            if self._is_system_of_equations(query):
                return QueryType.EQUATION_SOLVING, WolframAPI.FULL_RESULTS
            else:
                return QueryType.EQUATION_SOLVING, WolframAPI.SHOW_STEPS
            
        # Check if it's a simple calculation
        if self._is_simple_calculation(query):
            return QueryType.SIMPLE_CALCULATION, WolframAPI.LLM
            
        # Default to natural language
        return QueryType.NATURAL_LANGUAGE, WolframAPI.LLM
        
    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any keywords.
        
        Args:
            text: Text to check
            keywords: List of keywords
            
        Returns:
            True if any keyword found
        """
        return any(keyword in text for keyword in keywords)
        
    def _is_simple_calculation(self, query: str) -> bool:
        """Check if query is a simple calculation.
        
        Args:
            query: Query to check
            
        Returns:
            True if simple calculation
        """
        # Pattern for simple math expressions
        simple_patterns = [
            r'^\d+[\s\+\-\*/\^]+\d+',  # Basic arithmetic
            r'^\d+\s*\*\s*10\^\d+',  # Scientific notation
            r'^sqrt\(',  # Square root
            r'^log\(',  # Logarithm
        ]
        
        return any(re.search(pattern, query.strip()) for pattern in simple_patterns)
        
    def get_api_params(
        self, 
        query_type: QueryType, 
        api_type: WolframAPI
    ) -> Dict[str, Any]:
        """Get appropriate API parameters for query type.
        
        Args:
            query_type: Type of query
            api_type: API to use
            
        Returns:
            API-specific parameters
        """
        params = {}
        
        if api_type == WolframAPI.SHOW_STEPS:
            params["show_steps"] = True
            params["format_type"] = "plaintext"
            
        elif api_type == WolframAPI.FULL_RESULTS:
            params["format_types"] = ["plaintext", "image"]
            if query_type == QueryType.PLOTTING:
                params["include_pod_id"] = ["Plot", "3DPlot", "ContourPlot"]
                
        elif api_type == WolframAPI.LANGUAGE_EVAL:
            if query_type == QueryType.PLOTTING:
                params["output_format"] = "image"
            else:
                params["output_format"] = "string"
                
        return params
        
    def preprocess_for_api(
        self,
        query: str,
        query_type: QueryType,
        api_type: WolframAPI
    ) -> str:
        """Preprocess query for specific API.

        Args:
            query: Original query
            query_type: Type of query
            api_type: Target API

        Returns:
            Preprocessed query
        """
        processed = query.strip()

        # Remove question words for direct APIs
        if api_type in [WolframAPI.LANGUAGE_EVAL, WolframAPI.FULL_RESULTS]:
            question_words = ["what is", "how to", "can you", "please"]
            for word in question_words:
                if processed.lower().startswith(word):
                    processed = processed[len(word):].strip()

        # Special handling for systems of equations
        if query_type == QueryType.EQUATION_SOLVING and self._is_system_of_equations(query):
            processed = self._format_system_query(query)

        # Format for Language API
        if api_type == WolframAPI.LANGUAGE_EVAL:
            if query_type == QueryType.PLOTTING:
                # Ensure proper Plot syntax
                if not processed.startswith(("Plot", "Plot3D")):
                    # Extract function and add Plot command
                    match = re.search(r'y\s*=\s*(.+)', processed)
                    if match:
                        processed = f"Plot[{match.group(1)}, {{x, -10, 10}}]"

        return processed

    def _is_system_of_equations(self, query: str) -> bool:
        """Check if query represents a system of equations.

        Args:
            query: Query to check

        Returns:
            True if system of equations
        """
        # Count equals signs
        equals_count = query.count('=')

        # Check for system keywords
        has_system_keywords = any(word in query.lower() for word in ["system", "systems", "simultaneous"])

        # Check for multiple equations separated by commas or 'and'
        has_multiple_equations = ',' in query or ' and ' in query.lower()

        return equals_count > 1 or has_system_keywords or has_multiple_equations

    def _format_system_query(self, query: str) -> str:
        """Format system of equations query for Wolfram API.

        Args:
            query: Original system query

        Returns:
            Formatted query for Wolfram
        """
        import re

        # Extract equations from query
        # Remove "Solve the system:" or similar prefixes
        clean_query = re.sub(r'^.*?system:?\s*', '', query, flags=re.IGNORECASE).strip()

        # Split equations by comma or 'and'
        if ',' in clean_query:
            equations = [eq.strip() for eq in clean_query.split(',')]
        elif ' and ' in clean_query.lower():
            equations = [eq.strip() for eq in re.split(r'\s+and\s+', clean_query, flags=re.IGNORECASE)]
        else:
            # Single equation with multiple = signs
            equations = [eq.strip() for eq in clean_query.split('=') if eq.strip()]
            if len(equations) == 3:  # Like "2x + y = 5 = x - y = 1" (unlikely but possible)
                equations = [f"{equations[0]} = {equations[1]}", f"{equations[1]} = {equations[2]}"]

        # Clean up equations - replace single = with == for Wolfram
        wolfram_equations = []
        variables = set()

        for eq in equations:
            if '=' in eq:
                # Find variables in equation
                vars_in_eq = re.findall(r'\b[a-zA-Z]\b', eq)
                variables.update(vars_in_eq)

                # Replace single = with == for Wolfram syntax
                wolfram_eq = eq.replace(' = ', ' == ')
                if not wolfram_eq.startswith('==') and not '==' in wolfram_eq:
                    wolfram_eq = wolfram_eq.replace('=', '==', 1)
                wolfram_equations.append(wolfram_eq)

        if len(wolfram_equations) > 1:
            # Format as proper Wolfram system: Solve[{eq1, eq2}, {x, y}]
            eq_list = ', '.join(wolfram_equations)
            var_list = ', '.join(sorted(variables))
            return f"Solve[{{ {eq_list} }}, {{ {var_list} }}]"
        else:
            # Single equation, keep original format
            return query
        
    def requires_clarification(self, query: str) -> Optional[List[str]]:
        """Check if query needs clarification.

        Args:
            query: User query

        Returns:
            List of clarification questions or None
        """
        clarifications = []

        # Check for systems of equations (multiple equations)
        if "solve" in query.lower():
            # Count equals signs to detect systems
            equals_count = query.count('=')
            has_system_keywords = any(word in query.lower() for word in ["system", "systems", "simultaneous"])

            # If it's a system (multiple equations or explicit system keywords), don't ask for variable clarification
            if equals_count > 1 or has_system_keywords:
                pass  # Systems don't need variable clarification
            # Check for ambiguous variable names only for single equations
            elif re.search(r'\b[a-z]\b', query):
                variables = re.findall(r'\b[a-z]\b', query)
                if len(set(variables)) > 1:
                    clarifications.append(
                        f"Which variable should I solve for: {', '.join(set(variables))}?"
                    )

        # Check for missing ranges in plots
        if "plot" in query.lower() and not re.search(r'from|between|\d+\s*to\s*\d+', query):
            clarifications.append(
                "What range would you like for the plot? (e.g., from -10 to 10)"
            )

        return clarifications if clarifications else None
