# Power Automate Email Integration Guide

This guide explains how to set up and use the `send_email` MCP tool with Power Automate to send emails from Claude Desktop.

## Overview

The `send_email` tool allows Claude Desktop to trigger a Power Automate flow that sends emails. This enables workflows such as:
- Emailing meeting summaries
- Sending research reports
- Forwarding conversation highlights
- Delivering automated notifications

## Architecture

```
Claude Desktop → MCP Server → HTTP POST → Power Automate → Email Service
```

## Setup Instructions

### 1. Create a Power Automate Flow

1. Go to [Power Automate](https://make.powerautomate.com/)
2. Click **"Create"** → **"Automated cloud flow"**
3. Choose **"When a HTTP request is received"** trigger
4. Configure the trigger with the following JSON schema:

```json
{
    "type": "object",
    "properties": {
        "to_email": {
            "type": "string",
            "description": "Recipient email address"
        },
        "subject": {
            "type": "string",
            "description": "Email subject"
        },
        "body": {
            "type": "string",
            "description": "Email body content"
        }
    },
    "required": [
        "to_email",
        "subject",
        "body"
    ]
}
```

5. Add a **"Send an email (V2)"** action (from Office 365 Outlook)
6. Map the dynamic content:
   - **To**: `to_email` (from HTTP request)
   - **Subject**: `subject` (from HTTP request)
   - **Body**: `body` (from HTTP request)
7. **Save** the flow
8. Copy the **HTTP POST URL** from the trigger

### 2. Configure the MCP Server

Set the Power Automate webhook URL as an environment variable:

#### On macOS/Linux:
```bash
export POWER_AUTOMATE_WEBHOOK_URL='https://prod-xx.eastus.logic.azure.com:443/workflows/...'
```

Add to your `~/.bashrc` or `~/.zshrc` for persistence.

#### On Windows:
```powershell
$env:POWER_AUTOMATE_WEBHOOK_URL='https://prod-xx.eastus.logic.azure.com:443/workflows/...'
```

Or set permanently via System Environment Variables.

#### In Claude Desktop Configuration

Add to your Claude Desktop MCP configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

**Important**: After editing the config file, **completely quit and restart Claude Desktop** (don't just close the window).

**Troubleshooting**: If you get "webhook URL not configured" error, see [TROUBLESHOOTING_CLAUDE_DESKTOP.md](TROUBLESHOOTING_CLAUDE_DESKTOP.md) for detailed diagnostic steps.

### 3. Test the Integration

In Claude Desktop, try:

```
Send an email to john@example.com with subject "Test Email" and body "This is a test email from Claude Desktop via Power Automate."
```

Claude will:
1. Recognize the email sending request
2. Call the `send_email` tool
3. Send HTTP POST to your Power Automate webhook
4. Power Automate will send the actual email

## Usage Examples

### Example 1: Email a Meeting Summary

```
I need to email a summary of our conversation to sarah@company.com.
Subject: "Meeting Summary - Project Alpha"
Include the key points we discussed about the timeline and deliverables.
```

### Example 2: Send Research Report

```
Please email the research findings to team@company.com.
Subject: "Market Research Results - Q1 2024"
Include a summary of the competitive analysis we just discussed.
```

### Example 3: Forward Conversation

```
Email this conversation to manager@company.com with subject "Weekly Status Update".
```

## Input Parameters

The `send_email` tool accepts three required parameters:

| Parameter | Type | Required | Max Length | Description |
|-----------|------|----------|------------|-------------|
| `to_email` | string | Yes | N/A | Valid email address in format `user@domain.com` |
| `subject` | string | Yes | 500 chars | Email subject line |
| `body` | string | Yes | 50,000 chars | Email body content (plain text or HTML) |

## Validation Rules

The tool performs the following validations:

1. **Email Format**: Must match pattern `user@domain.com`
2. **Non-Empty Fields**: All three fields must contain non-whitespace content
3. **Length Limits**: Subject ≤ 500 chars, Body ≤ 50,000 chars
4. **Webhook Configuration**: `POWER_AUTOMATE_WEBHOOK_URL` must be set

## Error Handling

### Common Errors

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Power Automate webhook URL not configured" | Environment variable not set | Set `POWER_AUTOMATE_WEBHOOK_URL` |
| "Invalid email format: ..." | Email doesn't match pattern | Provide valid email address |
| "subject cannot be empty" | Subject is blank | Provide non-empty subject |
| "body cannot be empty" | Body is blank | Provide non-empty body |
| "webhook error: 400" | Power Automate rejected request | Check flow configuration |
| "Network error" | Cannot reach webhook | Check network/URL |

## Security Best Practices

### 1. Protect Your Webhook URL
- Never commit webhook URLs to source control
- Use environment variables
- Rotate URLs periodically
- Consider IP restrictions in Power Automate

### 2. Add Authentication
In Power Automate flow, add authentication:
- Add **"Compose"** action after HTTP trigger
- Check for shared secret in headers
- Use **"Condition"** to validate
- Return 401 if invalid

Example:
```
Trigger: When HTTP request received
↓
Compose: Get header 'X-API-Key'
↓
Condition: Is API key valid?
  If Yes → Send Email
  If No → Respond with 401
```

### 3. Rate Limiting
- Power Automate has built-in rate limits
- Consider adding additional throttling in your flow
- Monitor usage in Power Automate analytics

### 4. Content Validation
Add validation in Power Automate:
- Check email length limits
- Sanitize HTML content if needed
- Validate recipient domains
- Add approval steps for sensitive recipients

## Troubleshooting

### Issue: Emails not arriving

**Check:**
1. Verify webhook URL is correct
2. Check Power Automate flow run history
3. Verify email is not in spam/junk
4. Check Office 365 send limits

**Debug:**
```bash
# Test webhook URL directly
curl -X POST "$POWER_AUTOMATE_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "subject": "Test",
    "body": "Test body"
  }'
```

### Issue: "Network error" in tool

**Check:**
1. Network connectivity
2. Webhook URL accessibility
3. Firewall/proxy settings
4. Power Automate flow status

### Issue: Tool not appearing in Claude Desktop

**Check:**
1. MCP server is running
2. Configuration file is valid JSON
3. Server process started successfully
4. Check Claude Desktop logs

## Advanced Configuration

### Custom Email Templates

Modify the Power Automate flow to use templates:

1. Add **"Compose"** action after trigger
2. Build HTML email template using dynamic content
3. Use in "Send email" body field

Example template:
```html
<html>
<body>
  <h1>@{triggerBody()?['subject']}</h1>
  <div>@{triggerBody()?['body']}</div>
  <hr>
  <p><em>Sent via Claude Desktop + Power Automate</em></p>
</body>
</html>
```

### Multiple Recipients

Modify trigger schema to accept array:
```json
{
  "to_email": {
    "type": "array",
    "items": {
      "type": "string"
    }
  }
}
```

Update send action:
- **To**: `join(triggerBody()?['to_email'], ';')`

### CC and BCC Support

Extend the schema:
```json
{
  "cc_email": {
    "type": "string"
  },
  "bcc_email": {
    "type": "string"
  }
}
```

Map in send action accordingly.

### Attachments

For attachments, use OneDrive or SharePoint:
1. Store file in OneDrive
2. Get sharing link
3. Include link in email body
4. Or use Power Automate to attach from storage

## Monitoring and Analytics

### Track Usage

1. Power Automate Analytics:
   - Flow runs per day
   - Success/failure rates
   - Average execution time

2. Add logging in Power Automate:
   - Log to SharePoint list
   - Log to Azure Table Storage
   - Send to Application Insights

### Example Logging

Add **"Compose"** action before email:
```json
{
  "timestamp": "@{utcNow()}",
  "recipient": "@{triggerBody()?['to_email']}",
  "subject": "@{triggerBody()?['subject']}",
  "status": "sent"
}
```

Then **"Add row"** to SharePoint list.

## Limitations

### Power Automate Limits
- 100,000 runs per month (per flow, free tier)
- 50,000 runs per day
- Email size limits (Office 365)
- Rate limiting applies

### Tool Limits
- Subject: 500 characters
- Body: 50,000 characters
- No attachment support directly

## Support

For issues:
1. Check Power Automate flow run history
2. Review MCP server logs
3. Test webhook URL directly with curl
4. Check environment variable configuration

## License

This integration is part of mcp-server-alpha. See LICENSE for details.

---

**Built with ❤️ using MCP and Power Automate**
