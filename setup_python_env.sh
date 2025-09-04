#!/bin/bash

echo "=== Setting up Python virtual environment ==="
echo ""

PYTHON_CMD="$(command -v python3)"

# check if python3 is installed
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ python3 not found"
    exit 1
fi

# create virtual environment if not exists
if [ ! -d ".venv" ]; then
    "$PYTHON_CMD" -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ create virtual environment failed"
        exit 1
    fi
fi


# activate virtual environment
echo "activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ activate virtual environment failed"
    exit 1
fi


# install Python dependencies
echo "installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Python environment setup completed"
    echo ""
    echo "Virtual environment created and activated, dependencies installed."
    echo ""
    echo "Next steps:"
    echo "1. Run Python scripts: python script.py"
    echo "2. Exit virtual environment: deactivate"
    echo ""
else
    echo ""
    echo "❌ Python dependencies installation failed"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi
