#!/bin/bash
source /home/alicia/mcp_copilot/venv/bin/activate
cd /home/alicia/mcp_copilot/src
exec python -m mcp_server_alpha.server
