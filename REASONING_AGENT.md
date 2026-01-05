# Reasoning Agent Orchestrator

## Overview

The Reasoning Agent Orchestrator is a meta-tool in the MCP server that uses LangGraph to autonomously plan and execute complex multi-step tasks by orchestrating existing MCP tools.

## Features

- **Natural Language Goal Processing**: Accepts complex goals in plain English
- **Autonomous Planning**: Uses LangGraph to decompose goals into actionable sub-tasks
- **Multi-Tool Orchestration**: Coordinates multiple MCP tools (search, calculator, analyzer, summarizer, weather, email)
- **Visible Reasoning Chain**: Shows step-by-step decision-making process for transparency
- **Execution Tracking**: Provides detailed execution steps and tool usage summaries
- **Branching Logic**: Makes decisions based on intermediate results

## Architecture

The reasoning agent operates as a meta-tool within the MCP framework:

```
┌─────────────────────────────────────────────────────┐
│           MCP Client (Claude Desktop)               │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              MCP Server (server.py)                 │
├─────────────────────────────────────────────────────┤
│  Tools:                                             │
│  • web_search          • summarize_text             │
│  • calculate           • weather_forecast           │
│  • analyze_data        • send_email                 │
│  • reasoning_agent  ◄──── Meta-tool                 │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│       ReasoningOrchestrator (orchestrator)          │
├─────────────────────────────────────────────────────┤
│  • Goal analysis                                    │
│  • Task decomposition                               │
│  • Tool selection and coordination                  │
│  • Result synthesis                                 │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│       ResearchAgent (LangGraph)                     │
├─────────────────────────────────────────────────────┤
│  • LLM reasoning (OpenAI GPT-4o-mini)               │
│  • Tool invocation                                  │
│  • State management                                 │
│  • Reasoning chain tracking                         │
└─────────────────────────────────────────────────────┘
```

## Usage

### Via MCP Client (Claude Desktop)

Once the MCP server is configured in Claude Desktop, you can use the reasoning agent directly:

```
Use the reasoning_agent tool to:
"Research renewable energy trends, analyze the data, and calculate the growth rate over the last 5 years"
```

The agent will:
1. Search for renewable energy trends
2. Extract relevant data from search results
3. Analyze the data to identify patterns
4. Calculate the growth rate
5. Provide a comprehensive answer

### Configuration in Claude Desktop

Add to your `claude_desktop_config.json`:

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

**Important**: The reasoning agent requires an OpenAI API key to function.

### Programmatic Usage

```python
from mcp_server_alpha.agents import ReasoningOrchestrator

# Initialize orchestrator
orchestrator = ReasoningOrchestrator(
    model="gpt-4o-mini",
    temperature=0.7
)

# Execute a complex goal
result = await orchestrator.execute(
    goal="Research machine learning trends and calculate the average growth rate"
)

# Access results
print(f"Result: {result['result']}")
print(f"Steps taken: {len(result['steps'])}")
print(f"Tools used: {len(result['tool_calls'])}")

# View execution details
for step in result['steps']:
    print(f"Step {step['step']}: {step['description']}")
```

## Example Goals

The reasoning agent can handle various complex tasks:

### Multi-Tool Coordination
```
"Research quantum computing breakthroughs, analyze the data, 
and provide a summary of the key findings"
```

### Data Analysis
```
"Analyze this dataset: [100, 150, 200, 250, 300], 
find the trend, and calculate the projected value for the next period"
```

### Information Synthesis
```
"Search for information about electric vehicle adoption rates, 
calculate the year-over-year growth, and summarize the findings"
```

### Weather and Decision Making
```
"Get the weather forecast for New York (10001), 
and if it's going to rain, suggest indoor activities"
```

## Response Format

The reasoning agent returns a structured response:

```json
{
  "success": true,
  "result": "Final answer or result",
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

## Key Components

### 1. ReasoningOrchestrator (`agents/reasoning_orchestrator.py`)
- Main orchestration logic
- Goal enhancement and context management
- Step and tool call extraction
- Result synthesis

### 2. ResearchAgent (`agents/research_agent.py`)
- LangGraph-based autonomous agent
- LLM reasoning with OpenAI
- Tool invocation and state management
- Reasoning chain tracking

### 3. MCP Server Integration (`server.py`)
- Exposes reasoning_agent as an MCP tool
- Handles lazy initialization
- Formats responses for MCP clients
- Error handling and graceful degradation

## Benefits

1. **Automation**: Complex tasks executed autonomously without manual tool selection
2. **Transparency**: Visible reasoning shows how decisions are made
3. **Flexibility**: Handles diverse goals without pre-defined workflows
4. **Extensibility**: Easy to add new tools to the agent's toolkit
5. **Client Agnostic**: Works with any MCP client (Claude Desktop, API, custom clients)

## Future Enhancements

- **Streaming Support**: Stream intermediate results in real-time
- **User Prompts**: Request additional information when needed
- **Checkpoints**: Allow users to review/approve decisions before execution
- **Visualization**: Display execution flow as a dynamic graph
- **Persistent Context**: Maintain context across multiple sessions
- **Tool Learning**: Improve tool selection based on usage patterns

## Testing

Run the test suite:

```bash
pytest tests/unit/test_reasoning_orchestrator.py -v
```

Run the example:

```bash
export OPENAI_API_KEY='your-api-key-here'
python examples/reasoning_agent_example.py
```

## Dependencies

- **LangGraph**: Workflow orchestration and state management
- **LangChain**: LLM interfaces and tool integration
- **OpenAI**: GPT-4o-mini for reasoning (configurable)
- **MCP SDK**: Protocol implementation

## Error Handling

The reasoning agent gracefully handles errors:

- **Missing API Key**: Returns error message instead of crashing
- **Tool Failures**: Continues with available tools
- **LLM Errors**: Reports error while maintaining server stability
- **Invalid Goals**: Provides feedback on goal clarity

## Best Practices

1. **Be Specific**: Clearer goals lead to better execution
2. **Use Context**: Provide relevant context for follow-up tasks
3. **Monitor Costs**: LLM calls incur costs; use appropriate models
4. **Review Output**: Verify reasoning chain for complex tasks
5. **Iterative Refinement**: Adjust goals based on initial results

## Support

- Check examples/ directory for more usage patterns
- See main README.md for general MCP server setup
- Open issues for bugs or feature requests

---

**Built with ❤️ using LangGraph and OpenAI**
