"""Test script for Wolfram Math Service API."""
import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print("Health Check:", response.json())
        assert response.status_code == 200


async def test_solve_simple():
    """Test simple math problem solving."""
    async with httpx.AsyncClient() as client:
        data = {
            "query": "What is the derivative of x^3 + 2x^2 + 5?",
            "show_steps": True,
            "include_educational": True
        }
        response = await client.post(f"{BASE_URL}/api/v1/math/solve", json=data)
        result = response.json()
        
        print("\n=== Simple Problem Test ===")
        print(f"Query: {data['query']}")
        print(f"Success: {result.get('success')}")
        if result.get('explanation'):
            print(f"Explanation: {result['explanation'][:200]}...")
        print(json.dumps(result.get('result', {}), indent=2)[:500])


async def test_solve_system_of_equations():
    """Test solving systems of equations."""
    async with httpx.AsyncClient() as client:
        data = {
            "query": "Solve the system: 2x + y = 5, x - y = 1",
            "show_steps": True,
            "student_level": "college",
            "include_educational": False
        }
        response = await client.post(f"{BASE_URL}/api/v1/math/solve", json=data)
        result = response.json()

        print("\n=== System of Equations Test ===")
        print(f"Query: {data['query']}")
        print(f"Success: {result.get('success')}")

        # Should not ask for clarification
        assert result.get('success') == True, f"Expected success, got error: {result.get('error')}"
        assert result.get('error') is None, f"Unexpected error: {result.get('error')}"

        # Should have a result
        assert 'result' in result, "Missing result field"
        assert result['result'].get('success') == True, "Wolfram API call failed"

        # Should contain the solution
        final_answer = result['result'].get('final_answer', '')
        assert 'x = 2' in final_answer and 'y = 1' in final_answer, f"Expected solution x=2, y=1, got: {final_answer}"


async def test_solve_integral():
    """Test integral with steps."""
    async with httpx.AsyncClient() as client:
        data = {
            "query": "integrate x^2 * sin(x) dx",
            "show_steps": True,
            "student_level": "undergraduate"
        }
        response = await client.post(f"{BASE_URL}/api/v1/math/solve", json=data)
        result = response.json()
        
        print("\n=== Integration Test ===")
        print(f"Query: {data['query']}")
        print(f"Success: {result.get('success')}")
        if result.get('steps'):
            print(f"Steps found: {len(result['steps'])}")
            for i, step in enumerate(result['steps'][:3]):
                print(f"  Step {i+1}: {step}")


async def test_engineering_problem():
    """Test engineering circuit problem."""
    async with httpx.AsyncClient() as client:
        data = {
            "query": "Calculate impedance of 10 ohm resistor in series with 100mH inductor at 1kHz",
            "include_educational": False
        }
        response = await client.post(f"{BASE_URL}/api/v1/math/solve", json=data)
        result = response.json()
        
        print("\n=== Engineering Problem Test ===")
        print(f"Query: {data['query']}")
        print(f"Success: {result.get('success')}")
        print(f"Result: {json.dumps(result.get('result', {}), indent=2)[:500]}")


async def test_plot():
    """Test plotting functionality."""
    async with httpx.AsyncClient() as client:
        data = {
            "expression": "sin(x) + 0.5*cos(2*x)",
            "variable": "x",
            "range_min": -10,
            "range_max": 10
        }
        response = await client.post(f"{BASE_URL}/api/v1/math/plot", data=data)
        result = response.json()
        
        print("\n=== Plot Test ===")
        print(f"Expression: {data['expression']}")
        print(f"Success: {result.get('success')}")
        if result.get('plot'):
            print(f"Plot generated: {len(result['plot'])} bytes")


async def test_flashcards():
    """Test flashcard generation."""
    async with httpx.AsyncClient() as client:
        data = {
            "problem": "Find the derivative of f(x) = x^3 + 2x^2 - 5x + 3",
            "solution": "f'(x) = 3x^2 + 4x - 5",
            "concepts": ["derivatives", "power rule", "polynomial functions"],
            "count": 5
        }
        response = await client.post(f"{BASE_URL}/api/v1/educational/flashcards", json=data)
        result = response.json()
        
        print("\n=== Flashcard Generation Test ===")
        print(f"Success: {result.get('success')}")
        if result.get('flashcards'):
            print(f"Flashcards generated: {len(result['flashcards'])}")
            for i, card in enumerate(result['flashcards'][:2]):
                print(f"\nCard {i+1}:")
                print(f"  Q: {card['question']}")
                print(f"  A: {card['answer']}")


async def test_quiz():
    """Test quiz generation."""
    async with httpx.AsyncClient() as client:
        data = {
            "topic": "Calculus - Derivatives",
            "concepts": ["power rule", "chain rule", "product rule"],
            "question_count": 5,
            "difficulty": "intermediate"
        }
        response = await client.post(f"{BASE_URL}/api/v1/educational/quiz", json=data)
        result = response.json()
        
        print("\n=== Quiz Generation Test ===")
        print(f"Topic: {data['topic']}")
        print(f"Success: {result.get('success')}")
        if result.get('quiz'):
            quiz = result['quiz']
            print(f"Quiz ID: {quiz.get('id')}")
            print(f"Questions: {len(quiz.get('questions', []))}")
            print(f"Total Points: {quiz.get('total_points')}")
            
            # Show first question
            if quiz.get('questions'):
                q = quiz['questions'][0]
                print(f"\nSample Question:")
                print(f"  Type: {q.get('type')}")
                print(f"  Question: {q.get('question')}")
                if q.get('options'):
                    print(f"  Options: {json.dumps(q['options'], indent=4)}")


async def test_concept_explanation():
    """Test concept explanation."""
    async with httpx.AsyncClient() as client:
        data = {
            "concept": "chain rule",
            "context": "calculus derivatives",
            "examples_count": 2
        }
        response = await client.post(f"{BASE_URL}/api/v1/educational/explain/concept", json=data)
        result = response.json()
        
        print("\n=== Concept Explanation Test ===")
        print(f"Concept: {data['concept']}")
        print(f"Success: {result.get('success')}")
        if result.get('explanation'):
            exp = result['explanation']
            print(f"Explanation: {exp.get('explanation', '')[:300]}...")
            if exp.get('analogy'):
                print(f"Analogy: {exp['analogy'][:200]}...")


async def main():
    """Run all tests."""
    print("Testing Wolfram Math Service API...")
    print("=" * 50)
    
    try:
        # Check if service is running
        await test_health_check()
        
        # Test math solving
        await test_solve_simple()
        await test_solve_integral()
        await test_engineering_problem()
        
        # Test plotting
        await test_plot()
        
        # Test educational features
        await test_flashcards()
        await test_quiz()
        await test_concept_explanation()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except httpx.ConnectError:
        print("ERROR: Could not connect to service.")
        print("Make sure the service is running on http://localhost:8000")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
