# Format Parameter Test Suite

This test suite demonstrates the new `format` parameter added to the solve endpoints. It tests 25 diverse math problems across various categories and saves the solutions in LaTeX format with step-by-step solutions.

## Features

- **25 Comprehensive Math Problems** covering:
  - Calculus (Derivatives, Integrals, Limits)
  - Algebra (Systems of Equations, Quadratics, Exponentials, Logarithms)
  - Linear Algebra (Matrices, Determinants)
  - Trigonometry (Identities, Equations)
  - Series and Sequences
  - Complex Numbers
  - Combinatorics

- **LaTeX Format Output**: All solutions use LaTeX formatting for mathematical expressions
- **Step-by-Step Solutions**: Each problem includes detailed solution steps
- **Organized Output**: Solutions are saved as individual Markdown files in the `answers/` folder
- **Educational Content**: Includes explanations, key concepts, and practice problems

## Prerequisites

1. Make sure the FastAPI server is running:
   ```bash
   python main.py
   ```

2. The server should be accessible at `http://localhost:8000`

## Running the Test

Execute the test script:

```bash
python test_format_parameter.py
```

## Output

The test will:
1. Create an `answers/` folder (if it doesn't exist)
2. Solve all 25 math problems using the API
3. Save each solution as a Markdown file: `answers/XXX_problem_name.md`
4. Display progress and summary statistics

### Example Output Structure

```
answers/
├── 001_derivative_polynomial.md
├── 002_derivative_chain_rule.md
├── 003_derivative_product_rule.md
├── ...
└── 025_combination.md
```

### Solution File Format

Each solution file contains:
- **Problem Information**: ID, category, timestamp
- **Question**: The original math problem
- **Result**: Final answer in LaTeX format
- **Step-by-Step Solution**: Detailed solution steps
- **Explanation**: Educational explanation of the solution
- **Visualizations**: Any graphs or diagrams (if applicable)
- **Educational Content**: Key concepts and practice problems
- **Raw API Response**: Complete JSON response for debugging

## Test Categories

| Category | Problems |
|----------|----------|
| Calculus - Derivatives | 3 problems |
| Calculus - Integration | 3 problems |
| Calculus - Limits | 1 problem |
| Algebra - Systems of Equations | 2 problems |
| Algebra - Quadratics | 2 problems |
| Algebra - Exponentials & Logs | 3 problems |
| Linear Algebra | 2 problems |
| Trigonometry | 2 problems |
| Series & Sequences | 2 problems |
| Complex Numbers | 2 problems |
| Combinatorics | 3 problems |

## Configuration

You can modify the test by editing `test_format_parameter.py`:

- **BASE_URL**: Change the API endpoint URL
- **MATH_PROBLEMS**: Add, remove, or modify test problems
- **Format Parameter**: Change from "latex" to "plaintext", "mathml", or "image"
- **Show Steps**: Toggle `show_steps` parameter
- **Educational Content**: Toggle `include_educational` parameter

## Example: Modifying the Format

To test with a different format, edit the `solve_problem` function:

```python
data = {
    "query": problem["query"],
    "show_steps": True,
    "include_educational": True,
    "format": "mathml"  # Change to: "plaintext", "latex", "mathml", or "image"
}
```

## Troubleshooting

### API Connection Error
- Ensure the FastAPI server is running: `python main.py`
- Check that the server is accessible at `http://localhost:8000/health`

### Timeout Errors
- Increase the timeout in the `solve_problem` function
- Some complex problems may take longer to solve

### Failed Solutions
- Check the individual solution files for error details
- The test will continue even if some problems fail
- Review the summary statistics at the end

## Sample Solution Output

Here's what a typical solution file looks like:

```markdown
# Problem 001_derivative_polynomial
**Category:** Calculus - Derivatives
**Date:** 2025-11-04 20:30:15

## Question
```
What is the derivative of x^3 + 2x^2 + 5?
```

**Status:** ✓ Success

## Result
### Final Answer
```latex
3x^2 + 4x
```

## Step-by-Step Solution
### Step 1
**Description:** Apply the power rule to x^3
```latex
d/dx(x^3) = 3x^2
```

### Step 2
**Description:** Apply the power rule to 2x^2
```latex
d/dx(2x^2) = 4x
```

### Step 3
**Description:** The derivative of a constant is 0
```latex
d/dx(5) = 0
```

### Step 4
**Description:** Combine all terms
```latex
3x^2 + 4x + 0 = 3x^2 + 4x
```
...
```

## Notes

- The `answers/` folder is ignored by git (see `.gitignore`)
- Each test run will overwrite existing solution files
- All API calls use a 60-second timeout
- Solutions are formatted in UTF-8 encoding
