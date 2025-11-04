#!/bin/bash
# Start the Gradio UI for Wolfram Math Service

echo "🧮 Wolfram Math Service - Gradio UI"
echo "===================================="
echo ""

# Check if API server is running
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "✅ API Server is running on port 8000"
else
    echo "⚠️  Warning: API server not detected on port 8000"
    echo ""
    echo "Please start the API server first:"
    echo "  python main.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Starting Gradio UI..."
echo "📡 UI will be available at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start Gradio app
python gradio_app.py
