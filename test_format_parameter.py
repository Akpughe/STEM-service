"""Test script for format parameter with comprehensive math problems."""
import asyncio
import httpx
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
ANSWERS_FOLDER = "answers"


# Comprehensive list of math problems covering various topics
MATH_PROBLEMS = [
    {
        "id": "001_derivative_polynomial",
        "query": "What is the derivative of x^3 + 2x^2 + 5?",
        "category": "Calculus - Derivatives"
    },
    {
        "id": "002_derivative_chain_rule",
        "query": "Find the derivative of sin(x^2 + 3x)",
        "category": "Calculus - Chain Rule"
    },
    {
        "id": "003_derivative_product_rule",
        "query": "What is the derivative of x^2 * e^x?",
        "category": "Calculus - Product Rule"
    },
    {
        "id": "004_integral_polynomial",
        "query": "Integrate x^3 + 2x + 1 dx",
        "category": "Calculus - Integration"
    },
    {
        "id": "005_integral_trig",
        "query": "Find the integral of sin(x) * cos(x) dx",
        "category": "Calculus - Trigonometric Integration"
    },
    {
        "id": "006_integral_by_parts",
        "query": "Integrate x * e^x dx",
        "category": "Calculus - Integration by Parts"
    },
    {
        "id": "007_limit",
        "query": "Find the limit as x approaches 0 of (sin(x))/x",
        "category": "Calculus - Limits"
    },
    {
        "id": "008_system_linear",
        "query": "Solve the system: 2x + y = 5, x - y = 1",
        "category": "Algebra - Systems of Equations"
    },
    {
        "id": "009_system_three_variables",
        "query": "Solve the system: x + y + z = 6, 2x - y + z = 3, x + 2y - z = 1",
        "category": "Algebra - Systems of Equations (3 variables)"
    },
    {
        "id": "010_quadratic",
        "query": "Solve x^2 - 5x + 6 = 0",
        "category": "Algebra - Quadratic Equations"
    },
    {
        "id": "011_quadratic_formula",
        "query": "Solve 2x^2 + 7x - 15 = 0 using the quadratic formula",
        "category": "Algebra - Quadratic Formula"
    },
    {
        "id": "012_exponential",
        "query": "Solve e^x = 10",
        "category": "Algebra - Exponential Equations"
    },
    {
        "id": "013_logarithm",
        "query": "Solve log(x) + log(x-3) = 1",
        "category": "Algebra - Logarithmic Equations"
    },
    {
        "id": "014_partial_fractions",
        "query": "Decompose (x+1)/((x-1)(x+2)) into partial fractions",
        "category": "Algebra - Partial Fractions"
    },
    {
        "id": "015_matrix_multiplication",
        "query": "Multiply the matrices [[1,2],[3,4]] and [[5,6],[7,8]]",
        "category": "Linear Algebra - Matrix Operations"
    },
    {
        "id": "016_determinant",
        "query": "Find the determinant of [[2,3],[1,4]]",
        "category": "Linear Algebra - Determinants"
    },
    {
        "id": "017_trig_identity",
        "query": "Simplify sin^2(x) + cos^2(x)",
        "category": "Trigonometry - Identities"
    },
    {
        "id": "018_trig_equation",
        "query": "Solve sin(x) = 0.5 for x in [0, 2π]",
        "category": "Trigonometry - Equations"
    },
    {
        "id": "019_series_sum",
        "query": "Find the sum of the series 1 + 2 + 3 + ... + 100",
        "category": "Series and Sequences"
    },
    {
        "id": "020_geometric_series",
        "query": "Find the sum of the geometric series 1 + 1/2 + 1/4 + 1/8 + ... (infinite)",
        "category": "Series - Geometric"
    },
    {
        "id": "021_complex_numbers",
        "query": "Simplify (2+3i)(4-i)",
        "category": "Complex Numbers"
    },
    {
        "id": "022_polar_form",
        "query": "Convert 1+i to polar form",
        "category": "Complex Numbers - Polar Form"
    },
    {
        "id": "023_factorial",
        "query": "Calculate 10!",
        "category": "Combinatorics"
    },
    {
        "id": "024_permutation",
        "query": "How many ways can you arrange 5 books on a shelf?",
        "category": "Combinatorics - Permutations"
    },
    {
        "id": "025_combination",
        "query": "How many ways can you choose 3 items from 10?",
        "category": "Combinatorics - Combinations"
    }
]


async def create_answers_folder():
    """Create the answers folder if it doesn't exist."""
    folder_path = Path(ANSWERS_FOLDER)
    folder_path.mkdir(exist_ok=True)
    print(f"✓ Created/verified answers folder: {folder_path.absolute()}")
    return folder_path


async def solve_problem(client: httpx.AsyncClient, problem: Dict[str, Any]) -> Dict[str, Any]:
    """Solve a single math problem using the API.

    Args:
        client: HTTP client
        problem: Problem dictionary with id, query, and category

    Returns:
        API response with solution
    """
    data = {
        "query": problem["query"],
        "show_steps": True,
        "include_educational": True,
        "format": "latex"
    }

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/math/solve",
            json=data,
            timeout=60.0
        )
        result = response.json()
        result["problem_id"] = problem["id"]
        result["category"] = problem["category"]
        return result
    except Exception as e:
        return {
            "success": False,
            "problem_id": problem["id"],
            "category": problem["category"],
            "query": problem["query"],
            "error": str(e)
        }


def format_solution_as_markdown(problem: Dict[str, Any], result: Dict[str, Any]) -> str:
    """Format the solution as a markdown file with LaTeX.

    Args:
        problem: Problem dictionary
        result: API response

    Returns:
        Formatted markdown string
    """
    lines = []

    # Header
    lines.append(f"# Problem {problem['id']}")
    lines.append(f"**Category:** {problem['category']}")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Question
    lines.append("## Question")
    lines.append(f"```")
    lines.append(problem['query'])
    lines.append("```")
    lines.append("")

    # Success status
    lines.append(f"**Status:** {'✓ Success' if result.get('success') else '✗ Failed'}")
    lines.append("")

    if not result.get('success'):
        lines.append("## Error")
        lines.append(f"```")
        lines.append(result.get('error', 'Unknown error'))
        lines.append("```")
        return "\n".join(lines)

    # Result/Answer
    if result.get('result'):
        lines.append("## Result")
        result_data = result['result']

        # Final answer
        if result_data.get('final_answer'):
            lines.append("### Final Answer")
            lines.append(f"```latex")
            lines.append(result_data['final_answer'])
            lines.append("```")
            lines.append("")

        # Original query result
        if result_data.get('original_query'):
            lines.append("### Original Query")
            lines.append(f"```")
            lines.append(result_data['original_query'])
            lines.append("```")
            lines.append("")

    # Step-by-step solution
    if result.get('steps') or (result.get('result') and result['result'].get('steps')):
        lines.append("## Step-by-Step Solution")
        steps = result.get('steps') or result['result'].get('steps', [])

        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, dict):
                    step_num = step.get('step_number', '?')
                    description = step.get('description', '')
                    math = step.get('math', '')

                    lines.append(f"### Step {step_num}")
                    if description:
                        lines.append(f"**Description:** {description}")
                        lines.append("")
                    if math:
                        lines.append(f"```latex")
                        lines.append(math)
                        lines.append("```")
                        lines.append("")
        else:
            lines.append(f"```")
            lines.append(str(steps))
            lines.append("```")
            lines.append("")

    # Explanation
    if result.get('explanation'):
        lines.append("## Explanation")
        lines.append(result['explanation'])
        lines.append("")

    # Visualizations
    if result.get('visualizations'):
        lines.append("## Visualizations")
        for viz in result['visualizations']:
            if isinstance(viz, dict):
                title = viz.get('title', 'Visualization')
                image = viz.get('image', {})
                lines.append(f"### {title}")
                if isinstance(image, dict) and image.get('src'):
                    lines.append(f"![{title}]({image['src']})")
                lines.append("")

    # Educational content
    if result.get('educational_content'):
        lines.append("## Educational Content")
        edu = result['educational_content']

        if edu.get('key_concepts'):
            lines.append("### Key Concepts")
            concepts = edu['key_concepts']
            if isinstance(concepts, list):
                for concept in concepts:
                    lines.append(f"- {concept}")
            else:
                lines.append(str(concepts))
            lines.append("")

        if edu.get('practice_problems'):
            lines.append("### Practice Problems")
            problems = edu['practice_problems']
            if isinstance(problems, list):
                for i, prob in enumerate(problems, 1):
                    lines.append(f"{i}. {prob}")
            else:
                lines.append(str(problems))
            lines.append("")

    # Raw result for reference
    lines.append("---")
    lines.append("## Raw API Response")
    lines.append("```json")
    lines.append(json.dumps(result, indent=2))
    lines.append("```")

    return "\n".join(lines)


async def save_solution(folder_path: Path, problem: Dict[str, Any], result: Dict[str, Any]):
    """Save the solution to a file.

    Args:
        folder_path: Path to answers folder
        problem: Problem dictionary
        result: API response
    """
    filename = f"{problem['id']}.md"
    filepath = folder_path / filename

    content = format_solution_as_markdown(problem, result)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    status = "✓" if result.get('success') else "✗"
    print(f"  {status} Saved: {filename}")


async def test_all_problems():
    """Test all math problems and save solutions."""
    print("=" * 80)
    print("MATH PROBLEMS TEST WITH LATEX FORMAT")
    print("=" * 80)
    print(f"Total problems: {len(MATH_PROBLEMS)}")
    print(f"Format: LaTeX")
    print(f"Show steps: Yes")
    print("=" * 80)
    print()

    # Create answers folder
    folder_path = await create_answers_folder()
    print()

    # Test API health
    print("Checking API health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health/", timeout=10.0)
            health = response.json()
            print(f"✓ API is healthy: {health}")
            print()
    except Exception as e:
        print(f"✗ API health check failed: {e}")
        print("Make sure the server is running with: python main.py")
        return

    # Solve all problems
    print("Solving problems...")
    print("-" * 80)

    successful = 0
    failed = 0

    async with httpx.AsyncClient() as client:
        for i, problem in enumerate(MATH_PROBLEMS, 1):
            print(f"\n[{i}/{len(MATH_PROBLEMS)}] {problem['category']}")
            print(f"Problem: {problem['query']}")

            result = await solve_problem(client, problem)
            await save_solution(folder_path, problem, result)

            if result.get('success'):
                successful += 1
            else:
                failed += 1

            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.5)

    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total problems: {len(MATH_PROBLEMS)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/len(MATH_PROBLEMS)*100):.1f}%")
    print(f"\nAnswers saved to: {folder_path.absolute()}")
    print("=" * 80)


async def main():
    """Main entry point."""
    try:
        await test_all_problems()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
