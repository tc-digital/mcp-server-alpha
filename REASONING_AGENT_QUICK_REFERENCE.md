# Reasoning Agent Quick Reference

## Quick Start

### Using in Claude Desktop

1. **Configure Claude Desktop** - Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-server-alpha": {
      "command": "python",
      "args": ["-m", "mcp_server_alpha.server"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

2. **Restart Claude Desktop completely** (quit and reopen)

3. **Use the reasoning_agent tool**:
```
Use the reasoning_agent tool with goal: 
"Research renewable energy trends and calculate the growth rate"
```

## Example Goals

### Research + Analysis
```
"Research quantum computing breakthroughs, analyze the key findings, 
and summarize the top 3 most significant developments"
```

### Multi-Step Calculation
```
"Find information about electric vehicle sales in 2023, 
calculate the year-over-year growth rate, 
and analyze if the trend is accelerating"
```

### Data Analysis
```
"Analyze this dataset: [100, 150, 200, 250, 300, 350], 
find the trend pattern, and calculate the projected value 
for the next 3 periods"
```

### Information Synthesis
```
"Search for information about machine learning frameworks, 
compare their features, and provide a summary of which 
is best for beginners"
```

## Response Structure

```json
{
  "success": true,
  "result": "The final answer or result",
  "execution_summary": {
    "total_steps": 5,
    "tools_used": ["web_search", "calculate", "analyze_data"],
    "tool_count": 3
  },
  "steps": [
    {
      "step": 1,
      "type": "reasoning",
      "description": "💭 I need to search for information..."
    },
    {
      "step": 2,
      "type": "tool_execution",
      "description": "🔧 Using web_search tool: {...}"
    }
  ],
  "tool_calls": [
    {
      "tool": "web_search",
      "arguments": {"query": "quantum computing", "max_results": 5}
    }
  ],
  "reasoning_chain": [
    "💭 First, I'll search for information...",
    "🔧 Using web_search tool: {...}",
    "💭 Based on the results..."
  ]
}
```

## Available Tools (Orchestrated by Reasoning Agent)

- **web_search** - Search for information online
- **calculate** - Perform mathematical calculations
- **analyze_data** - Analyze datasets and find patterns
- **summarize_text** - Summarize long text content
- **weather_forecast** - Get weather forecasts (US only)
- **send_email** - Send emails via Power Automate

## Tips for Best Results

1. **Be Specific**: Clear goals lead to better execution
   - ✅ "Research renewable energy trends in 2023 and calculate the growth rate"
   - ❌ "Tell me about energy"

2. **Multi-Step Tasks**: Perfect for complex workflows
   - ✅ "Search for X, analyze the data, calculate Y, and summarize findings"
   - ❌ Single-tool tasks (use the specific tool directly instead)

3. **Context Matters**: Provide relevant details
   - ✅ "Analyze sales data [1000, 1100, 1200] and predict next quarter"
   - ❌ "Analyze data"

## Troubleshooting

### Error: "OpenAI API key required"
**Solution**: Add `OPENAI_API_KEY` to your Claude Desktop config env section

### Error: Server not responding
**Solution**: 
1. Completely quit Claude Desktop
2. Check config file syntax
3. Restart Claude Desktop
4. Check Claude Desktop logs

### No reasoning_agent tool visible
**Solution**:
1. Verify MCP server is running
2. Check Claude Desktop Developer Console
3. Restart Claude Desktop

## Programmatic Usage

```python
from mcp_server_alpha.agents import ReasoningOrchestrator

# Initialize
orchestrator = ReasoningOrchestrator(
    model="gpt-4o-mini",
    temperature=0.7
)

# Execute goal
result = await orchestrator.execute(
    goal="Research AI trends and calculate growth"
)

# Access results
print(result['result'])           # Final answer
print(result['steps'])            # Execution steps
print(result['tool_calls'])       # Tools used
print(result['reasoning_chain'])  # Reasoning process
```

## Cost Considerations

- Uses OpenAI API (charges apply)
- Model: gpt-4o-mini by default (cost-effective)
- Complex goals may require multiple LLM calls
- Monitor usage in OpenAI dashboard

## Future Enhancements

- 🌊 Real-time streaming of progress updates
- ✅ Dynamic user prompts for missing parameters
- 📊 Visual flowchart of execution
- 💾 Persistent context across sessions
- 🔄 Retry logic for failed tool calls

## More Information

- **Full Documentation**: [REASONING_AGENT.md](REASONING_AGENT.md)
- **Examples**: [examples/reasoning_agent_example.py](examples/reasoning_agent_example.py)
- **Tests**: [tests/unit/test_reasoning_orchestrator.py](tests/unit/test_reasoning_orchestrator.py)
- **Main README**: [README.md](README.md)
