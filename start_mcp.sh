#!/bin/bash
#
# Dynamic MCP server startup script
# This script automatically detects its location and starts the MCP server
# Works with Claude Desktop and other MCP clients
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if virtual environment exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    # Activate virtual environment if it exists
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "Warning: Virtual environment not found at $SCRIPT_DIR/venv"
    echo "The server may not work correctly without dependencies installed."
    echo "Run ./setup.sh to create the virtual environment."
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Start the MCP server
exec python -m mcp_server_alpha.server
