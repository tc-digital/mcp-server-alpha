# Send Email Tool - Quick Reference

## Quick Start

### 1. Set Up Power Automate Flow

1. Create flow: **When a HTTP request is received** → **Send an email (V2)**
2. Use this JSON schema in the HTTP trigger:

```json
{
    "type": "object",
    "properties": {
        "to_email": {"type": "string"},
        "subject": {"type": "string"},
        "body": {"type": "string"}
    },
    "required": ["to_email", "subject", "body"]
}
```

3. Copy the webhook URL from the trigger

### 2. Configure Environment Variable

**Option A: In Claude Desktop config file**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "mcp-server-alpha": {
      "command": "python",
      "args": ["-m", "mcp_server_alpha.server"],
      "env": {
        "POWER_AUTOMATE_WEBHOOK_URL": "https://prod-xx.eastus.logic.azure.com:443/workflows/..."
      }
    }
  }
}
```

**After editing, completely quit and restart Claude Desktop.**

**Option B: System environment variable**

```bash
export POWER_AUTOMATE_WEBHOOK_URL='https://prod-xx.eastus.logic.azure.com:443/workflows/...'
```

### 3. Use in Claude Desktop

Simply ask Claude to send an email:

```
Send an email to john@example.com with subject "Meeting Notes" 
and body "Here are the key points from today's meeting..."
```

## Usage Examples

### Email a Summary
```
Email a summary of our conversation to manager@company.com 
with subject "Weekly Update"
```

### Research Report
```
Send the research findings to team@company.com with subject 
"Market Analysis Q1 2024". Include the key metrics we discussed.
```

### Quick Note
```
Email sarah@company.com: "Don't forget about the 2pm meeting"
Subject: "Meeting Reminder"
```

## Input Parameters

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| `to_email` | string | Yes | Valid email format |
| `subject` | string | Yes | Max 500 chars, non-empty |
| `body` | string | Yes | Max 50,000 chars, non-empty |

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "webhook URL not configured" | Missing env var | Set `POWER_AUTOMATE_WEBHOOK_URL` and **restart Claude Desktop** |
| "Invalid email format" | Bad email | Use valid email like `user@domain.com` |
| "subject cannot be empty" | Empty subject | Provide non-empty subject |
| "body cannot be empty" | Empty body | Provide non-empty body |

**Troubleshooting**: For detailed diagnostic steps, see [TROUBLESHOOTING_CLAUDE_DESKTOP.md](TROUBLESHOOTING_CLAUDE_DESKTOP.md)

## Validation Rules

✅ **Email**: Must match pattern `user@domain.com`  
✅ **Subject**: 1-500 characters  
✅ **Body**: 1-50,000 characters  
✅ **All fields**: No whitespace-only values

## Security

- Never hardcode webhook URLs
- Use environment variables
- Keep webhook URL secret
- Add authentication in Power Automate (optional but recommended)

## Full Documentation

See [POWER_AUTOMATE_INTEGRATION.md](POWER_AUTOMATE_INTEGRATION.md) for:
- Detailed setup instructions
- Troubleshooting guide
- Advanced configurations
- Security best practices
- Monitoring and analytics

---

**Need Help?**
1. Check [POWER_AUTOMATE_INTEGRATION.md](POWER_AUTOMATE_INTEGRATION.md)
2. Review Power Automate flow run history
3. Test webhook with curl
4. Check MCP server logs
