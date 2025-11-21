#!/bin/bash
# Setup script for Computer Use Desktop Agent

echo "=== Computer Use Desktop Agent Setup ==="
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi
echo "✓ Python 3 is installed"
echo ""

# Create virtual environment (optional but recommended)
echo "2. Do you want to create a virtual environment? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
    echo "Activate it with: source venv/bin/activate"
    echo ""
fi

# Install dependencies
echo "3. Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Create .env file
echo "4. Setting up environment variables..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Anthropic API Key (get from https://console.anthropic.com/)
ANTHROPIC_API_KEY=your_api_key_here

# Orchestrator configuration
ORCHESTRATOR_HOST=localhost
ORCHESTRATOR_PORT=8000
EOF
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create logs directory
echo "5. Creating logs directory..."
mkdir -p logs
echo "✓ Logs directory created"
echo ""

# Platform-specific instructions
echo "6. Platform-specific setup:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   macOS detected"
    echo "   "
    echo "   ⚠️  IMPORTANT: Grant accessibility permissions"
    echo "   "
    echo "   Go to: System Preferences → Security & Privacy → Privacy → Accessibility"
    echo "   Add Terminal (or your Python interpreter) to the allowed apps"
    echo ""
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   Windows detected"
    echo "   You may need to run the script as administrator"
    echo ""
else
    echo "   Linux detected"
    echo "   Ensure X11 or Wayland is properly configured"
    echo ""
fi

echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Run test: python3 test_agent.py"
echo "  3. Start orchestrator: python3 orchestrator.py"
echo "  4. Run example: python3 example_notepad.py"
echo ""
echo "For more information, see README.md"

