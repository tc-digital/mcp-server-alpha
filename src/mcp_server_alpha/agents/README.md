# LangGraph Agent Integration

This directory contains the LangGraph-based conversational agent that adds intelligent LLM reasoning to the MCP server.

## Overview

The `InsuranceAgent` uses OpenAI's GPT models (or compatible APIs) to:
- **Understand natural language** queries about insurance products
- **Orchestrate tool calls** to search products, check eligibility, generate quotes
- **Maintain conversation context** across multiple turns
- **Explain complex information** in clear, conversational language

## Architecture

```
┌─────────────────────────────────────────┐
│         User (Natural Language)         │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        InsuranceAgent (LangGraph)       │
│  ┌────────────────────────────────────┐ │
│  │  OpenAI GPT (Reasoning & Planning) │ │
│  └─────────┬──────────────────────────┘ │
│            │ decides which tools to use │
│  ┌─────────▼──────────────────────────┐ │
│  │        Agent Tools Wrapper         │ │
│  │  • search_products                 │ │
│  │  • check_eligibility               │ │
│  │  • generate_quote                  │ │
│  │  • get_cross_sell_products         │ │
│  └─────────┬──────────────────────────┘ │
└────────────┼──────────────────────────────┘
             │
┌────────────▼──────────────────────────────┐
│      MCP Tools & Business Logic           │
│  (Existing deterministic tools)            │
└───────────────────────────────────────────┘
```

## Key Components

### `InsuranceAgent`
Main agent class that:
- Initializes LangGraph workflow
- Manages conversation state
- Coordinates LLM and tools

### `AgentTools`
Wraps MCP tools for LangChain compatibility:
- Converts async MCP tools to LangChain tool format
- Handles parameter extraction from natural language
- Formats tool responses for LLM consumption

### `AgentState`
Pydantic model tracking:
- Conversation messages
- Consumer information
- Current workflow state
- Metadata

## Usage

### Basic Setup

```python
from mcp_server_alpha.agents import InsuranceAgent
from mcp_server_alpha.config import ProductRegistry, ConfigLoader
from mcp_server_alpha.providers import ProviderRegistry, MockInsuranceProvider

# Set up registries
product_registry = ProductRegistry()
provider_registry = ProviderRegistry()

# Load products and providers
ConfigLoader.load_from_directory("products", product_registry)
provider_registry.register(MockInsuranceProvider("mock_co"))

# Create agent with OpenAI API key
agent = InsuranceAgent(
    product_registry=product_registry,
    provider_registry=provider_registry,
    model="gpt-4o-mini",  # or "gpt-4"
    temperature=0.7
)
```

### Conversational Interaction

```python
import asyncio

async def chat_example():
    # First message
    result = await agent.chat("Hi! I'm looking for health insurance.")
    print(result["response"])
    
    # Continue conversation with context
    state = result["state"]
    result = await agent.chat(
        "I'm 38 years old and live in California. Am I eligible?",
        state=state
    )
    print(result["response"])
    
    # Get quote
    state = result["state"]
    result = await agent.chat(
        "Can you give me a quote for 2 dependents?",
        state=state
    )
    print(result["response"])

asyncio.run(chat_example())
```

### Running the Example

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-...'

# Run the agent example
python examples/agent_example.py
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Agent Parameters

- `model`: OpenAI model name (default: "gpt-4o-mini")
  - `gpt-4o-mini`: Fast, cost-effective, good for most use cases
  - `gpt-4o`: More capable, higher quality reasoning
  - `gpt-4-turbo`: Balanced performance and cost
  
- `temperature`: Response creativity (0.0-1.0, default: 0.7)
  - Lower (0.0-0.3): More focused, deterministic responses
  - Medium (0.4-0.7): Balanced creativity and consistency
  - Higher (0.8-1.0): More creative, varied responses

## Features

### 1. Natural Language Understanding
Agent interprets user intent from conversational input:
- "What health plans do you have?" → searches health products
- "Am I eligible?" → checks eligibility with consumer info
- "How much would it cost?" → generates quote

### 2. Context Maintenance
State preserved across conversation turns:
- Remembers user's age, location from earlier messages
- Tracks which product user is interested in
- References previous quotes and recommendations

### 3. Tool Orchestration
Agent decides when and how to use tools:
- Calls multiple tools in logical sequence
- Extracts parameters from natural language
- Combines tool results into coherent responses

### 4. Clear Explanations
LLM generates human-friendly responses:
- Explains eligibility rules in plain language
- Breaks down quote components
- Suggests alternatives when not eligible

## AWS Bedrock Integration

To use AWS Bedrock instead of OpenAI:

```python
# Install AWS dependencies
# pip install langchain-aws

from langchain_aws import ChatBedrock

# Replace ChatOpenAI with ChatBedrock in insurance_agent.py
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
).bind_tools(self.tools)
```

Supported Bedrock models:
- Claude 3 (Opus, Sonnet, Haiku)
- Llama 2/3
- Cohere Command
- And more...

## Best Practices

### 1. API Key Security
- Never commit API keys to version control
- Use environment variables or secret managers
- Rotate keys regularly

### 2. Cost Management
- Use gpt-4o-mini for development/testing
- Monitor token usage with OpenAI dashboard
- Set rate limits for production

### 3. Error Handling
- Agent gracefully handles API failures
- Falls back to clear error messages
- Logs issues for debugging

### 4. Testing
- Test with sample conversations
- Validate tool parameter extraction
- Check response quality across different inputs

## Extending the Agent

### Adding New Tools

1. Create tool function in `tools.py`:
```python
@tool
async def new_tool(param: str) -> str:
    """Tool description for LLM."""
    # Implementation
    return result
```

2. Add to tool list in `AgentTools.get_tools()`:
```python
return [
    search_products,
    check_eligibility,
    new_tool,  # Add here
]
```

3. Update system prompt in `insurance_agent.py` to mention new tool

### Custom Models

Support for other LLM providers:
- **Anthropic Claude**: Use `langchain-anthropic`
- **Local models**: Use `langchain-community` with Ollama
- **Azure OpenAI**: Use `langchain-openai` with Azure endpoint

## Troubleshooting

### "OpenAI API key required"
- Set `OPENAI_API_KEY` environment variable
- Or pass `api_key` parameter to agent constructor

### "Rate limit exceeded"
- Wait before retrying
- Reduce frequency of requests
- Upgrade OpenAI plan

### "Tool call failed"
- Check tool parameters extracted correctly
- Verify registries initialized properly
- Review tool error messages in response

### Poor Response Quality
- Try gpt-4o instead of gpt-4o-mini
- Adjust temperature (lower for more focused)
- Refine system prompt for better guidance

## Performance Considerations

- **Latency**: Agent calls add ~1-3 seconds per interaction
- **Cost**: Approx $0.001-0.01 per conversation turn with gpt-4o-mini
- **Concurrency**: Agent is async-safe, supports multiple concurrent users
- **Caching**: Consider caching frequent queries to reduce API calls

## Future Enhancements

- [ ] Streaming responses for better UX
- [ ] Memory/RAG for long-term context
- [ ] Multi-agent collaboration
- [ ] Fine-tuned models for insurance domain
- [ ] A/B testing different models
- [ ] Analytics on conversation patterns
