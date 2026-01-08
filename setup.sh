#!/bin/bash
#
# Automated setup script for mcp-server-alpha (Linux/macOS)
# This script creates a virtual environment, installs dependencies, and can start the server.
#

set -e  # Exit on error

echo "=== MCP Server Alpha - Automated Setup ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

# Get version info directly from Python for reliability
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10 or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
if pip install --upgrade pip 2>/dev/null; then
    echo -e "${GREEN}✓ pip upgraded${NC}"
else
    echo -e "${YELLOW}⚠ Warning: pip upgrade had issues, but continuing...${NC}"
fi
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
if pip install -e ".[dev]"; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Check for environment variables
echo "🔐 Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠ OPENAI_API_KEY not set${NC}"
    echo "  To use the research assistant, set your OpenAI API key:"
    echo "    export OPENAI_API_KEY='sk-...'"
else
    echo -e "${GREEN}✓ OPENAI_API_KEY is set${NC}"
fi

if [ -z "$POWER_AUTOMATE_WEBHOOK_URL" ]; then
    echo -e "${YELLOW}⚠ POWER_AUTOMATE_WEBHOOK_URL not set (optional)${NC}"
    echo "  To use the send_email tool, set your Power Automate webhook URL:"
    echo "    export POWER_AUTOMATE_WEBHOOK_URL='https://...'"
else
    echo -e "${GREEN}✓ POWER_AUTOMATE_WEBHOOK_URL is set${NC}"
fi
echo ""

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo ""
echo "  1. To activate the virtual environment manually:"
echo "     source venv/bin/activate"
echo ""
echo "  2. To run an example:"
echo "     python examples/research_example.py"
echo ""
echo "  3. To start the MCP server (for Claude Desktop integration):"
echo "     python -m mcp_server_alpha.server"
echo ""
echo "  4. To run tests:"
echo "     pytest"
echo ""

# Ask if user wants to start the server
read -p "Would you like to start the MCP server now? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting MCP server..."
    echo "   (Press Ctrl+C to stop)"
    echo ""
    exec python -m mcp_server_alpha.server
fi
