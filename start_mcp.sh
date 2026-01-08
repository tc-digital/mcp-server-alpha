#!/bin/bash
#
# Dynamic MCP server startup script
# This script automatically detects its location and starts the MCP server
# Works with Claude Desktop and other MCP clients
#
# Usage: ./start_mcp.sh [--no-venv]
#   --no-venv: Skip virtual environment activation (use system Python)
#

# Ensure script is executed, not sourced
# Note: BASH_SOURCE[0] != $0 when sourced (they're equal when executed)
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo "Error: This script must be executed, not sourced."
    echo "Usage: ./start_mcp.sh"
    return 1 2>/dev/null || exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check for --no-venv flag
NO_VENV=false
if [[ "$1" == "--no-venv" ]]; then
    NO_VENV=true
fi

# Check if virtual environment exists
if [[ -d "$SCRIPT_DIR/venv" ]]; then
    # Activate virtual environment if it exists
    source "$SCRIPT_DIR/venv/bin/activate"
elif [[ "$NO_VENV" != true ]]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/venv"
    echo ""
    echo "The MCP server requires dependencies to be installed."
    echo "Please run one of the following:"
    echo "  1. ./setup.sh          - Create venv and install dependencies (recommended)"
    echo "  2. ./start_mcp.sh --no-venv - Skip venv check (if dependencies installed globally)"
    echo ""
    exit 1
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Start the MCP server
exec python -m mcp_server_alpha.server
