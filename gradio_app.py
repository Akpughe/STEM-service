"""Gradio UI for Wolfram Math Service."""
import gradio as gr
import requests
from typing import Tuple
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINT = "/api/v1/math/solve"

# Example Questions
EXAMPLE_QUESTIONS = [
    ["Evaluate the contour integral ∮ dz/(z² + 1)² over the unit circle centered at the origin, and verify your result using the residue theorem.", "graduate", True, True],
    ["Find the Gaussian curvature of the surface given by the parametric equations: x = u cos v, y = u sin v, z = u², where u > 0 and v ∈ [0, 2π].", "graduate", True, True],
    ["Evaluate ∭ (x² + y² + z²) dx dy dz over the region bounded by the sphere x² + y² + z² = 4 and the cone z = √(x² + y²).", "graduate", True, True],
    ["Calculate the first-order correction to the energy of a particle in a 1D infinite well potential V(x) = -αδ(x - a/2) using perturbation theory, where δ is the Dirac delta function.", "graduate", True, True],
    ["Solve the Navier-Stokes equations for steady, incompressible flow between two parallel plates with a pressure gradient, and find the velocity profile.", "graduate", True, True],
    ["Calculate 2x + 3 = 11", "undergraduate", True, False],
]


def format_latex(text: str) -> str:
    """Format text to ensure LaTeX is properly displayed in Gradio."""
    if not text:
        return ""
    # Gradio supports LaTeX in markdown, so we just return the text as-is
    return text


def format_steps(steps: list) -> str:
    """Format step-by-step solution."""
    if not steps or len(steps) == 0:
        return ""

    formatted = "## 👣 Step-by-Step Solution\n\n"
    for i, step in enumerate(steps, 1):
        step_num = step.get('step_number', i)
        description = step.get('description', '')
        math = step.get('math', '')

        content = description if description else math
        if content:
            formatted += f"**Step {step_num}:**\n\n{content}\n\n---\n\n"

    return formatted


def format_educational_content(edu_content: dict) -> str:
    """Format educational content."""
    if not edu_content:
        return ""

    formatted = "## 🎓 Educational Insights\n\n"

    if edu_content.get('summary'):
        formatted += f"**Summary:** {edu_content['summary']}\n\n"

    if edu_content.get('key_insights') and len(edu_content['key_insights']) > 0:
        formatted += "### 💡 Key Insights:\n\n"
        for insight in edu_content['key_insights']:
            formatted += f"- {insight}\n"
        formatted += "\n"

    if edu_content.get('common_mistakes') and len(edu_content['common_mistakes']) > 0:
        formatted += "### ⚠️ Common Mistakes:\n\n"
        for mistake in edu_content['common_mistakes']:
            formatted += f"- {mistake}\n"
        formatted += "\n"

    if edu_content.get('tips') and len(edu_content['tips']) > 0:
        formatted += "### 💭 Tips:\n\n"
        for tip in edu_content['tips']:
            formatted += f"- {tip}\n"
        formatted += "\n"

    if edu_content.get('real_world_applications') and len(edu_content['real_world_applications']) > 0:
        formatted += "### 🌍 Real World Applications:\n\n"
        for app in edu_content['real_world_applications']:
            formatted += f"- {app}\n"
        formatted += "\n"

    return formatted if len(formatted) > 30 else ""


def solve_math_problem(
    query: str,
    student_level: str,
    show_steps: bool,
    include_educational: bool
) -> Tuple[str, str, str, str]:
    """
    Solve a mathematical problem using the Wolfram Math Service API.

    Returns:
        Tuple of (final_answer, explanation, steps, educational_content)
    """
    if not query or query.strip() == "":
        return (
            "❌ Please enter a mathematical question.",
            "",
            "",
            ""
        )

    try:
        # Prepare request payload
        payload = {
            "query": query,
            "show_steps": show_steps,
            "student_level": student_level.lower(),
            "include_educational": include_educational
        }

        # Make API request
        response = requests.post(
            f"{API_BASE_URL}{API_ENDPOINT}",
            json=payload,
            timeout=120
        )

        # Check response status
        if response.status_code != 200:
            return (
                f"❌ API Error: HTTP {response.status_code}",
                f"Server returned status code {response.status_code}",
                "",
                ""
            )

        # Parse response
        data = response.json()

        if not data.get('success'):
            error_msg = data.get('error', 'Unknown error occurred')
            return (
                f"❌ Error",
                f"**Error:** {error_msg}",
                "",
                ""
            )

        # Extract results
        result = data.get('result', {})
        final_answer = result.get('final_answer', 'Solution computed successfully.')
        explanation = data.get('explanation', '')
        steps = data.get('steps', [])
        educational = data.get('educational_content', {})

        # Format outputs
        answer_display = f"## 🎯 Final Answer\n\n{final_answer}"

        explanation_display = ""
        if explanation:
            explanation_display = f"## 📖 Detailed Explanation\n\n{explanation}"

        steps_display = format_steps(steps) if steps else ""

        educational_display = format_educational_content(educational) if educational else ""

        return (
            answer_display,
            explanation_display,
            steps_display,
            educational_display
        )

    except requests.exceptions.Timeout:
        return (
            "⏱️ Request Timeout",
            "The request took too long (>120 seconds). The problem might be too complex.",
            "",
            ""
        )
    except requests.exceptions.ConnectionError:
        return (
            "🔌 Connection Error",
            f"Could not connect to the API server at {API_BASE_URL}.\n\nMake sure the server is running:\n```bash\npython main.py\n```",
            "",
            ""
        )
    except Exception as e:
        return (
            "❌ Unexpected Error",
            f"**Error:** {str(e)}",
            "",
            ""
        )


# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
}

.output-markdown h2 {
    color: #667eea;
    border-bottom: 2px solid #667eea;
    padding-bottom: 10px;
    margin-top: 20px;
}

.output-markdown h3 {
    color: #764ba2;
}

#final-answer {
    background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
    border-left: 4px solid #667eea;
    padding: 20px;
    border-radius: 8px;
    font-size: 1.1em;
}

#component-0 {
    max-width: 1200px;
    margin: auto;
}
"""

# Create Gradio interface
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple",
    ),
    css=custom_css,
    title="Wolfram Math Service"
) as demo:

    gr.Markdown(
        """
        # 🧮 Wolfram Math Service
        ### Advanced Mathematical Problem Solver

        Solve complex mathematical, physics, and engineering problems using Wolfram Alpha + GPT-5.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            # Input Section
            query_input = gr.Textbox(
                label="📝 Enter Your Mathematical Question",
                placeholder="Example: Evaluate the contour integral ∮ dz/(z² + 1)² over the unit circle...",
                lines=5,
                max_lines=10
            )

            with gr.Row():
                student_level = gr.Dropdown(
                    label="🎓 Student Level",
                    choices=["Undergraduate", "Graduate", "PhD", "Professional"],
                    value="Graduate"
                )

                show_steps = gr.Checkbox(
                    label="👣 Show Step-by-Step Solution",
                    value=True
                )

                include_educational = gr.Checkbox(
                    label="📚 Include Educational Content",
                    value=True
                )

            solve_btn = gr.Button(
                "🚀 Solve Problem",
                variant="primary",
                size="lg"
            )

            gr.Markdown("### 📚 Quick Test Examples")
            gr.Markdown("Click any example below to load it:")

    # Output Section
    with gr.Row():
        with gr.Column(scale=2):
            final_answer_output = gr.Markdown(
                label="Final Answer",
                elem_id="final-answer"
            )

    with gr.Accordion("📖 Detailed Explanation", open=True):
        explanation_output = gr.Markdown()

    with gr.Accordion("👣 Step-by-Step Solution", open=False):
        steps_output = gr.Markdown()

    with gr.Accordion("🎓 Educational Insights", open=False):
        educational_output = gr.Markdown()

    # Examples
    gr.Examples(
        examples=EXAMPLE_QUESTIONS,
        inputs=[query_input, student_level, show_steps, include_educational],
        label="Example Questions",
        examples_per_page=6
    )

    # Connect button to function
    solve_btn.click(
        fn=solve_math_problem,
        inputs=[query_input, student_level, show_steps, include_educational],
        outputs=[final_answer_output, explanation_output, steps_output, educational_output]
    )

    # Footer
    gr.Markdown(
        """
        ---
        **💡 Tips:**
        - Use LaTeX notation for mathematical expressions (e.g., \\\\(x^2\\\\), \\\\[\\\\frac{a}{b}\\\\])
        - Complex problems may take 30-60 seconds to solve
        - Try the example questions to see the system in action

        **🔧 Make sure your API server is running:**
        ```bash
        python main.py
        ```
        """
    )


if __name__ == "__main__":
    print("🧮 Starting Wolfram Math Service UI...")
    print(f"📡 API Server: {API_BASE_URL}")
    print("🌐 Launching Gradio interface...")
    print("")

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )
