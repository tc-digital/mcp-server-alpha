# Troubleshooting Claude Desktop Integration

## Issue: "Power Automate webhook URL not configured" Error

If you're seeing this error even after adding the webhook URL to Claude Desktop's configuration, follow these steps:

### Step 1: Verify Configuration File Location

Claude Desktop configuration is typically located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Note: The file might be named `claude_desktop_config.json` (not just `config.json`)

### Step 2: Verify Configuration Format

Your configuration should look exactly like this:

```json
{
  "mcpServers": {
    "mcp-server-alpha": {
      "command": "python",
      "args": ["-m", "mcp_server_alpha.server"],
      "env": {
        "POWER_AUTOMATE_WEBHOOK_URL": "https://prod-xx.eastus.logic.azure.com:443/workflows/YOUR_FLOW_ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR_SIGNATURE"
      }
    }
  }
}
```

**Important**: 
- Make sure the webhook URL is in quotes
- Replace the entire URL with your actual Power Automate webhook URL
- Do NOT include a comma after the closing brace if this is the last entry

### Step 3: Restart Claude Desktop Completely

After editing the configuration:
1. **Quit** Claude Desktop completely (don't just close the window)
   - macOS: `Cmd+Q` or Claude Desktop → Quit
   - Windows: Right-click taskbar icon → Exit
2. Wait 5 seconds
3. Start Claude Desktop again

### Step 4: Verify Python Command

Make sure the `python` command in your config points to the correct Python installation:

```bash
# Check which Python will be used
which python
# or
which python3

# Check if mcp_server_alpha is installed
python -m mcp_server_alpha.server --version 2>&1 | head -5
```

If you installed in a virtual environment, use the full path:
```json
{
  "mcpServers": {
    "mcp-server-alpha": {
      "command": "/full/path/to/venv/bin/python",
      "args": ["-m", "mcp_server_alpha.server"],
      "env": {
        "POWER_AUTOMATE_WEBHOOK_URL": "your-url-here"
      }
    }
  }
}
```

### Step 5: Check MCP Server Logs

Claude Desktop logs MCP server output. Check these locations:

**macOS**:
```bash
# View recent logs
tail -f ~/Library/Logs/Claude/mcp*.log

# or
cat ~/Library/Logs/Claude/mcp-server-mcp-server-alpha.log
```

**Windows**:
```powershell
# Check in
%LOCALAPPDATA%\Claude\logs\
```

Look for errors like:
- `ModuleNotFoundError: No module named 'mcp_server_alpha'`
- Environment variable issues
- Python path problems

### Step 6: Test Environment Variable Manually

Create a test script to verify the environment variable is being passed:

```python
# test_env.py
import os
import sys

print(f"Python: {sys.executable}")
print(f"POWER_AUTOMATE_WEBHOOK_URL: {os.getenv('POWER_AUTOMATE_WEBHOOK_URL')}")
print(f"All env vars: {list(os.environ.keys())}")
```

Run it the same way Claude Desktop would:
```bash
POWER_AUTOMATE_WEBHOOK_URL='your-url' python -m mcp_server_alpha.server
```

### Step 7: Alternative Configuration Methods

If environment variables in `claude_desktop_config.json` aren't working, try these alternatives:

#### Option A: Use System Environment Variables

**macOS/Linux** (in `~/.bashrc` or `~/.zshrc`):
```bash
export POWER_AUTOMATE_WEBHOOK_URL='https://prod-xx.eastus.logic.azure.com:443/workflows/...'
```

Then restart your terminal and Claude Desktop.

**Windows** (System Environment Variables):
1. Open System Properties → Environment Variables
2. Add new User Variable:
   - Name: `POWER_AUTOMATE_WEBHOOK_URL`
   - Value: Your webhook URL
3. Restart Claude Desktop

#### Option B: Use a Wrapper Script

Create `start_mcp_with_env.sh` (macOS/Linux):
```bash
#!/bin/bash
export POWER_AUTOMATE_WEBHOOK_URL='https://prod-xx.eastus.logic.azure.com:443/workflows/...'
exec python -m mcp_server_alpha.server
```

Make it executable:
```bash
chmod +x start_mcp_with_env.sh
```

Update Claude Desktop config:
```json
{
  "mcpServers": {
    "mcp-server-alpha": {
      "command": "/full/path/to/start_mcp_with_env.sh",
      "args": []
    }
  }
}
```

Windows (`start_mcp_with_env.bat`):
```batch
@echo off
set POWER_AUTOMATE_WEBHOOK_URL=https://prod-xx.eastus.logic.azure.com:443/workflows/...
python -m mcp_server_alpha.server
```

### Step 8: Verify MCP Server is Running

In Claude Desktop, type a message like:
```
What MCP tools are available?
```

Claude should list all available tools including `send_email`.

### Step 9: Test with a Simple Email

Once the webhook URL is recognized, test with:
```
Send a test email to your-email@example.com with subject "Test" and body "Testing the send_email tool"
```

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "webhook URL not configured" | Config not loaded | Restart Claude Desktop completely |
| "webhook URL not configured" | Wrong config file location | Check OS-specific path |
| "ModuleNotFoundError" | Package not installed | `pip install -e .` in repo directory |
| "command not found: python" | Python not in PATH | Use full path to Python |
| No error but tool not working | Wrong server name | Check `mcpServers` key matches |
| JSON parse error | Invalid JSON syntax | Validate JSON with online tool |

### Advanced Debugging

Enable verbose logging by modifying the server startup:

```python
# In src/mcp_server_alpha/server.py, add at the top:
import sys
import os

sys.stderr.write(f"=== ENVIRONMENT CHECK ===\n")
sys.stderr.write(f"POWER_AUTOMATE_WEBHOOK_URL: {os.getenv('POWER_AUTOMATE_WEBHOOK_URL')}\n")
sys.stderr.write(f"All env vars: {list(os.environ.keys())}\n")
sys.stderr.flush()
```

Then check Claude Desktop logs for the output.

### Still Not Working?

1. Share your configuration (with webhook URL redacted)
2. Share relevant logs from Claude Desktop
3. Verify Power Automate flow is active
4. Test the webhook URL directly with curl:

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "subject": "Test",
    "body": "Test body"
  }'
```

If curl works but Claude Desktop doesn't, the issue is with the MCP configuration.
