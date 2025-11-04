# Gradio UI Guide

## 🎯 Quick Start

### Step 1: Start the API Server

```bash
python main.py
```

The server should start on `http://localhost:8000`

### Step 2: Launch the Gradio UI

**Option A - Using the startup script (recommended):**
```bash
./start_gradio.sh
```

**Option B - Direct launch:**
```bash
python gradio_app.py
```

### Step 3: Open in Browser

The UI will automatically open at:
```
http://localhost:7860
```

---

## ✨ Features

### 📝 Input Section
- **Text Area**: Enter any mathematical, physics, or engineering question
- **Student Level**: Choose from Undergraduate, Graduate, PhD, or Professional
- **Show Steps**: Toggle step-by-step solution display
- **Educational Content**: Toggle educational insights and explanations

### 📊 Output Section
- **🎯 Final Answer**: The solution with proper LaTeX rendering
- **📖 Detailed Explanation**: Complete derivation and methodology
- **👣 Step-by-Step Solution**: Numbered steps showing the work
- **🎓 Educational Insights**: Key concepts, tips, common mistakes, and real-world applications

### 📚 Example Questions

The UI includes 6 pre-loaded example questions:

1. **Complex Analysis** - Contour integral with residue theorem
2. **Differential Geometry** - Gaussian curvature calculation
3. **Multiple Integrals** - Triple integral over sphere/cone intersection
4. **Quantum Mechanics** - Perturbation theory
5. **Fluid Dynamics** - Navier-Stokes equations
6. **Simple Equation** - Basic algebra (for testing)

Click any example to load it instantly!

---

## 🎨 LaTeX Rendering

The UI supports full LaTeX notation:

**Inline math:** Use `\(` and `\)` or single `$`
```
\(x^2 + y^2 = r^2\)
```

**Display math:** Use `\[` and `\]` or double `$$`
```
\[\frac{d}{dx}(x^2) = 2x\]
```

**Examples:**
- Fractions: `\frac{numerator}{denominator}`
- Greek letters: `\alpha`, `\beta`, `\gamma`, `\Delta`, `\Omega`
- Integrals: `\int`, `\oint`, `\iint`, `\iiint`
- Summations: `\sum_{i=1}^{n}`
- Limits: `\lim_{x \to \infty}`

---

## 🔧 Troubleshooting

### UI won't start
```bash
# Check if Gradio is installed
pip install gradio

# Check for port conflicts
lsof -ti:7860
# If something is running, kill it:
lsof -ti:7860 | xargs kill
```

### Connection errors
```bash
# Make sure API server is running
lsof -ti:8000

# If not running, start it:
python main.py
```

### No LaTeX rendering
- Make sure your browser supports JavaScript
- Check browser console for errors (F12 → Console)
- Try refreshing the page (Cmd+R / Ctrl+R)

### Slow responses
- Complex problems can take 30-60 seconds
- Check your internet connection (Wolfram Alpha API requires internet)
- Monitor the API server logs for errors

---

## 🚀 Advanced Features

### Sharing the UI Publicly

To create a public shareable link (72-hour temporary URL):

Edit `gradio_app.py` and change:
```python
demo.launch(
    server_name="127.0.0.1",
    server_port=7860,
    share=True,  # Changed to True
    show_error=True,
    quiet=False
)
```

This will generate a public URL like: `https://abc123.gradio.live`

**⚠️ Warning:** Anyone with the link can access your UI and use your Wolfram/OpenAI API credits!

### Custom Port

Change the port if 7860 is in use:
```python
demo.launch(
    server_port=8888,  # Use any available port
    ...
)
```

### Dark Mode

Gradio automatically supports dark mode based on your system settings!

---

## 📊 Testing the UI

### Quick Test
1. Launch the UI
2. Click the "Simple Equation" example
3. Click "Solve Problem"
4. Should get result in ~5 seconds

### Complex Test
1. Click "Q1: Complex Analysis" example
2. Click "Solve Problem"
3. Wait 20-40 seconds
4. Should get detailed solution with LaTeX-rendered math

---

## 🎯 Best Practices

### Writing Questions
- Be specific and clear
- Include all necessary information
- Use proper mathematical notation
- Specify what you want to find

**Good examples:**
```
Solve for x: 2x + 5 = 13

Find the derivative of f(x) = x^3 + 2x^2 - 5x + 1

Evaluate the integral: ∫(x^2 + 3x) dx from 0 to 5

Calculate the eigenvalues of the matrix [[2, 1], [1, 2]]
```

**Bad examples:**
```
help me
solve this
what is the answer?
```

---

## 🛑 Stopping the UI

Press **Ctrl+C** in the terminal where Gradio is running.

To ensure all servers are stopped:
```bash
# Stop Gradio UI (port 7860)
lsof -ti:7860 | xargs kill

# Stop API server (port 8000)
lsof -ti:8000 | xargs kill

# Stop any HTTP servers (port 8080)
lsof -ti:8080 | xargs kill
```

---

## 📝 File Structure

```
wolfram-math-service/
├── gradio_app.py         # Main Gradio UI application
├── start_gradio.sh       # Convenient startup script
├── main.py               # FastAPI backend server
├── requirements.txt      # Python dependencies (includes gradio)
└── GRADIO_UI_GUIDE.md   # This guide
```

---

## 🎓 Examples Gallery

### Example 1: Simple Algebra
**Input:**
```
Solve: 3x - 7 = 14
```

**Output:**
- Final Answer: x = 7
- Explanation: Step-by-step algebraic solution
- Steps: 3 steps showing the work

### Example 2: Calculus
**Input:**
```
Find the derivative of f(x) = sin(x) * e^x
```

**Output:**
- Final Answer: f'(x) = e^x(sin(x) + cos(x))
- Explanation: Product rule application
- Educational: When to use product rule

### Example 3: Complex Analysis
**Input:**
```
Evaluate ∮ dz/(z² + 1)² over |z| = 1
```

**Output:**
- Final Answer: 0
- Explanation: Residue theorem application
- Steps: ~10 steps with pole identification, residue calculation
- Educational: Residue theorem explanation

---

## 🔗 Related Files

- **Test Results**: See `TEST_SUMMARY.md` for comprehensive test results
- **API Documentation**: See `README.md` for API details
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`

---

## 💡 Tips

1. **Use Examples**: Click example buttons to see proper question formatting
2. **Be Patient**: Complex problems take time (20-60 seconds)
3. **Check Steps**: Enable "Show Steps" for educational value
4. **Copy Results**: You can select and copy the LaTeX-rendered output
5. **Experiment**: Try different student levels to see how explanations change

---

## 🆘 Need Help?

1. Check API server is running: `lsof -ti:8000`
2. Check Gradio version: `python3 -c "import gradio; print(gradio.__version__)"`
3. View server logs in the terminal
4. Check `.env` file for correct API keys

---

**Happy problem solving! 🧮**
