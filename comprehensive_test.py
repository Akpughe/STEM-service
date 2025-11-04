"""Comprehensive test of Wolfram Math Service with challenging problems."""
import requests
import json
from typing import Dict, List
import time

# Test questions
QUESTIONS = [
    {
        "id": 1,
        "category": "Advanced Mathematics",
        "title": "Complex Analysis & Contour Integration",
        "query": "Evaluate the contour integral ∮ dz/(z² + 1)² over the unit circle centered at the origin, and verify your result using the residue theorem."
    },
    {
        "id": 2,
        "category": "Advanced Mathematics",
        "title": "Differential Geometry",
        "query": "Find the Gaussian curvature of the surface given by the parametric equations: x = u cos v, y = u sin v, z = u², where u > 0 and v ∈ [0, 2π]."
    },
    {
        "id": 3,
        "category": "Advanced Mathematics",
        "title": "Abstract Algebra",
        "query": "Show that the group Z₄ × Z₂ is isomorphic to the dihedral group D₄, and find all its subgroups."
    },
    {
        "id": 4,
        "category": "Advanced Mathematics",
        "title": "Number Theory",
        "query": "Prove that there are infinitely many primes of the form 4n+3, and find the smallest such prime greater than 100."
    },
    {
        "id": 5,
        "category": "Advanced Mathematics",
        "title": "Advanced Calculus - Multiple Integrals",
        "query": "Evaluate ∭ (x² + y² + z²) dx dy dz over the region bounded by the sphere x² + y² + z² = 4 and the cone z = √(x² + y²)."
    },
    {
        "id": 6,
        "category": "Theoretical Physics",
        "title": "Quantum Mechanics - Perturbation Theory",
        "query": "Calculate the first-order correction to the energy of a particle in a 1D infinite well potential V(x) = -αδ(x - a/2) using perturbation theory, where δ is the Dirac delta function."
    },
    {
        "id": 7,
        "category": "Theoretical Physics",
        "title": "General Relativity - Schwarzschild Metric",
        "query": "Derive the geodesic equation for a particle moving in Schwarzschild spacetime and find the effective potential for equatorial orbits."
    },
    {
        "id": 8,
        "category": "Theoretical Physics",
        "title": "Statistical Mechanics - Bose-Einstein Condensation",
        "query": "For a 3D ideal Bose gas, derive the expression for the critical temperature T_c in terms of particle density n and the Bose function g_{3/2}(z)."
    },
    {
        "id": 9,
        "category": "Theoretical Physics",
        "title": "Electrodynamics - Maxwell's Equations",
        "query": "Solve for the electromagnetic field of a uniformly moving point charge using the Lienard-Wiechert potentials, and show that it satisfies the retarded wave equation."
    },
    {
        "id": 10,
        "category": "Theoretical Physics",
        "title": "Quantum Field Theory",
        "query": "Compute the Feynman diagram for electron-electron scattering in QED up to one-loop order and identify the contributing diagrams."
    },
    {
        "id": 11,
        "category": "Engineering Applications",
        "title": "Control Systems - State Space",
        "query": "Design a state feedback controller for the system ẋ = [0 1; -2 -3]x + [0; 1]u to place poles at s = -1 ± j, and find the required gain matrix K."
    },
    {
        "id": 12,
        "category": "Engineering Applications",
        "title": "Signal Processing - Fourier Analysis",
        "query": "Find the Fourier transform of the function f(t) = e^{-|t|} * sinc(t), and determine its bandwidth and power spectral density."
    },
    {
        "id": 13,
        "category": "Engineering Applications",
        "title": "Fluid Dynamics - Navier-Stokes",
        "query": "Solve the Navier-Stokes equations for steady, incompressible flow between two parallel plates with a pressure gradient, and find the velocity profile."
    },
    {
        "id": 14,
        "category": "Engineering Applications",
        "title": "Structural Mechanics - Finite Element",
        "query": "For a cantilever beam under end load, derive the stiffness matrix for a single beam element and assemble the global system for a 3-element discretization."
    },
    {
        "id": 15,
        "category": "Engineering Applications",
        "title": "Thermodynamics - Irreversible Processes",
        "query": "Calculate the entropy production rate for heat conduction through a composite wall with thermal conductivities k₁ and k₂, and temperatures T₁ and T₃ at the boundaries."
    }
]

def test_question(question: Dict) -> Dict:
    """Test a single question."""
    print(f"\n{'='*80}")
    print(f"Testing Q{question['id']}: {question['title']}")
    print(f"Category: {question['category']}")
    print(f"Query: {question['query']}")
    print(f"{'='*80}\n")

    # Prepare request
    url = "http://localhost:8000/api/v1/math/solve"
    payload = {
        "query": question["query"],
        "show_steps": True,
        "student_level": "graduate",
        "include_educational": True
    }

    try:
        # Send request with timeout
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        elapsed_time = time.time() - start_time

        # Parse response
        result = response.json()

        # Add metadata
        result["question_id"] = question["id"]
        result["question_title"] = question["title"]
        result["category"] = question["category"]
        result["elapsed_time"] = elapsed_time
        result["status_code"] = response.status_code

        # Print summary
        print(f"Status: {'✓ SUCCESS' if result.get('success') else '✗ FAILED'}")
        print(f"Time: {elapsed_time:.2f}s")

        if result.get('success'):
            print(f"\nResult Summary:")
            if result.get('result'):
                res = result['result']
                if res.get('final_answer'):
                    print(f"  Final Answer: {res.get('final_answer')[:200]}...")
                if res.get('steps'):
                    print(f"  Steps: {len(res.get('steps'))} steps provided")

            if result.get('explanation'):
                print(f"  Explanation: {result['explanation'][:200]}...")

            if result.get('educational_content'):
                print(f"  Educational Content: ✓ Included")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")

        return result

    except requests.exceptions.Timeout:
        print(f"✗ TIMEOUT after 120s")
        return {
            "question_id": question["id"],
            "question_title": question["title"],
            "category": question["category"],
            "success": False,
            "error": "Request timeout after 120 seconds",
            "elapsed_time": 120
        }
    except Exception as e:
        print(f"✗ EXCEPTION: {str(e)}")
        return {
            "question_id": question["id"],
            "question_title": question["title"],
            "category": question["category"],
            "success": False,
            "error": str(e),
            "elapsed_time": 0
        }

def analyze_results(results: List[Dict]) -> Dict:
    """Analyze test results."""
    total = len(results)
    successful = sum(1 for r in results if r.get('success'))
    failed = total - successful

    # Categorize by solution source
    wolfram_only = []
    wolfram_gpt = []
    gpt_only = []
    failed_list = []

    for result in results:
        if not result.get('success'):
            failed_list.append(result)
        else:
            # Check if GPT fallback was used (indicated in explanation or result)
            used_gpt = False
            if result.get('explanation'):
                # GPT was used for enhancement
                used_gpt = True

            if result.get('result', {}).get('solution_source') == 'gpt':
                gpt_only.append(result)
            elif used_gpt:
                wolfram_gpt.append(result)
            else:
                wolfram_only.append(result)

    # Calculate statistics
    avg_time = sum(r.get('elapsed_time', 0) for r in results) / total

    analysis = {
        "total_questions": total,
        "successful": successful,
        "failed": failed,
        "success_rate": f"{(successful/total)*100:.1f}%",
        "average_time": f"{avg_time:.2f}s",
        "wolfram_only_count": len(wolfram_only),
        "wolfram_plus_gpt_count": len(wolfram_gpt),
        "gpt_only_count": len(gpt_only),
        "failed_count": len(failed_list),
        "categories": {
            "wolfram_only": [r['question_id'] for r in wolfram_only],
            "wolfram_plus_gpt": [r['question_id'] for r in wolfram_gpt],
            "gpt_only": [r['question_id'] for r in gpt_only],
            "failed": [r['question_id'] for r in failed_list]
        }
    }

    return analysis

def main():
    """Run comprehensive test."""
    print("=" * 80)
    print("WOLFRAM MATH SERVICE - COMPREHENSIVE TEST")
    print("Testing 15 Challenging Questions")
    print("=" * 80)

    # Run all tests
    results = []
    for question in QUESTIONS:
        result = test_question(question)
        results.append(result)
        # Small delay between requests
        time.sleep(1)

    # Analyze results
    print("\n" + "=" * 80)
    print("TEST ANALYSIS")
    print("=" * 80)

    analysis = analyze_results(results)

    print(f"\nOverall Results:")
    print(f"  Total Questions: {analysis['total_questions']}")
    print(f"  Successful: {analysis['successful']}")
    print(f"  Failed: {analysis['failed']}")
    print(f"  Success Rate: {analysis['success_rate']}")
    print(f"  Average Response Time: {analysis['average_time']}")

    print(f"\nSolution Sources:")
    print(f"  Wolfram Only: {analysis['wolfram_only_count']} questions")
    print(f"  Wolfram + GPT Enhancement: {analysis['wolfram_plus_gpt_count']} questions")
    print(f"  GPT Only (Wolfram failed): {analysis['gpt_only_count']} questions")
    print(f"  Failed: {analysis['failed_count']} questions")

    print(f"\nQuestion IDs by Category:")
    print(f"  Wolfram Only: {analysis['categories']['wolfram_only']}")
    print(f"  Wolfram + GPT: {analysis['categories']['wolfram_plus_gpt']}")
    print(f"  GPT Only: {analysis['categories']['gpt_only']}")
    print(f"  Failed: {analysis['categories']['failed']}")

    # Save results to JSON
    output = {
        "analysis": analysis,
        "detailed_results": results
    }

    with open('test_results_comprehensive.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nDetailed results saved to: test_results_comprehensive.json")

    return output

if __name__ == "__main__":
    main()
