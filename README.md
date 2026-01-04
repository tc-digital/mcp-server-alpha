# Research Assistant with LangGraph

An intelligent, autonomous research assistant powered by LangGraph and OpenAI that demonstrates visible reasoning chains and multi-tool orchestration.

## 🎯 What It Does

This research assistant can:
- **🔍 Research any topic** using web search and information gathering
- **🧮 Perform calculations** for mathematical and financial queries
- **📊 Analyze data** to find patterns and insights
- **📝 Summarize content** to extract key information
- **🌤️ Get weather forecasts** for any US location by zip code or coordinates
- **📧 Send emails** via Power Automate flow webhooks
- **💭 Show its reasoning** with visible thought chains

## 🏗️ Architecture

```
src/mcp_server_alpha/
├── models/          # Research models (Query, Result, ThoughtChain, etc.)
├── tools/           # Research tools (search, calculator, analyzer, summarizer, weather, send_email)
├── agents/          # LangGraph agent with reasoning chains
├── orchestration/   # Workflow engine for complex tasks
├── adapters/        # Multi-channel adapters (chat, voice, API)
└── server.py        # MCP server implementation
```

### Key Components

#### 1. **Research Agent** (`agents/research_agent.py`)
- LangGraph-based autonomous agent
- Uses OpenAI (gpt-4o-mini by default) for reasoning
- Visible thought process and reasoning chains
- Tool orchestration based on research needs

#### 2. **Research Tools** (`tools/`)
- **Web Search**: Find information on any topic (mock, ready for real API)
- **Calculator**: Perform mathematical calculations
- **Data Analyzer**: Statistical analysis and pattern finding
- **Summarizer**: Extract key information from text
- **Weather Forecast**: Get real-time weather forecasts using weather.gov API
- **Send Email**: Trigger Power Automate flow to send emails via webhook

#### 3. **Reasoning Chain** (`models/reasoning.py`)
- Tracks agent's thought process
- Shows observations, analysis, synthesis, and conclusions
- Helps understand how the agent reaches answers

#### 4. **Config-Driven System**
- Easy to add new tools and integrations
- No code changes needed for new capabilities
- Pluggable architecture

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation

```bash
# Clone and install
git clone https://github.com/tc-digital/mcp-server-alpha.git
cd mcp-server-alpha

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Running the Research Assistant

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-...'

# Run the example
python examples/research_example.py
```

### Example Research Queries

The assistant can handle various types of research:

```python
# Factual research
"What are the key differences between machine learning and deep learning?"

# Calculations
"Calculate compound interest on $10,000 at 5% for 3 years"

# Data analysis
"Analyze this dataset: [10, 15, 20, 25, 30] and show statistics"

# Weather forecasts
"What's the weather forecast for zip code 10001?"
"Get the hourly weather forecast for San Francisco (94102)"

# Send email via Power Automate
"Send an email to john@example.com with subject 'Meeting Notes' and body 'Here are the notes from today's meeting...'"

# Multi-step research
"Research renewable energy trends and calculate the growth rate"
```

## 💡 Usage

### Basic Research

```python
from mcp_server_alpha.agents import ResearchAgent

# Initialize agent
agent = ResearchAgent()

# Research a topic
result = await agent.research("What is quantum computing?")

print(result["response"])  # Agent's answer
print(result["reasoning_chain"])  # Thought process
```

### With Reasoning Visibility

```python
# The agent shows its reasoning
result = await agent.research("Compare Python and JavaScript")

# See how it thinks
for step in result["reasoning_chain"]:
    print(step)
# Output:
# 💭 I need to search for information about Python...
# 🔧 Using web_search tool: {'query': 'Python programming language'}
# 💭 Based on these sources, I can conclude...
```

### Interactive Mode

```python
# Maintains context across questions
state = None

questions = [
    "What is machine learning?",
    "What are the main types?",  # Remembers context
    "Which one should I learn first?"  # Continues conversation
]

for question in questions:
    result = await agent.research(question, state)
    state = result["state"]  # Preserve context
    print(result["response"])
```

## 🔧 Extending the Assistant

### Adding a New Tool

1. Create tool in `src/mcp_server_alpha/tools/`:

```python
# my_new_tool.py
async def my_tool(param: str) -> dict:
    """Tool description."""
    # Implementation
    return {"result": "..."}
```

2. Add to agent tools in `agents/tools.py`:

```python
@tool
async def my_tool_wrapper(param: str) -> str:
    """Tool for LangChain."""
    result = await my_tool(param)
    return result["result"]
```

3. Agent automatically uses it when relevant!

### Integrating Real APIs

The tools are designed to be easily upgraded:

**Web Search**: Replace mock with Google Custom Search, Bing, or DuckDuckGo API

```python
# tools/search.py
import requests

async def web_search_tool(query: str, max_results: int = 5):
    # Replace mock with real API
    response = requests.get(
        "https://api.search.com/search",
        params={"q": query, "limit": max_results}
    )
    return response.json()["results"]
```

**Weather Forecast**: Already integrated with real weather.gov API!

```python
# Query by zip code
result = await weather_forecast_tool("10001", "forecast")

# Query by coordinates  
result = await weather_forecast_tool("39.7456,-97.0892", "hourly")

# Returns structured forecast data
{
  "success": true,
  "location": {
    "latitude": 40.7484,
    "longitude": -73.9967,
    "city": "New York",
    "state": "NY"
  },
  "forecast_type": "forecast",
  "periods": [
    {
      "name": "Tonight",
      "temperature": 45,
      "temperatureUnit": "F",
      "windSpeed": "5 mph",
      "windDirection": "SW",
      "shortForecast": "Partly Cloudy",
      "detailedForecast": "Partly cloudy, with a low around 45..."
    }
  ]
}
```

**Send Email via Power Automate**: Already integrated with configurable webhook!

See the [Power Automate Integration Guide](POWER_AUTOMATE_INTEGRATION.md) for detailed setup instructions.

```python
# First, set the Power Automate webhook URL
export POWER_AUTOMATE_WEBHOOK_URL='https://prod-xx.eastus.logic.azure.com:443/workflows/...'

# Send email via the tool
result = await send_email_tool(
    to_email="recipient@example.com",
    subject="Meeting Summary",
    body="Here is the summary of our meeting today..."
)

# Returns structured result
{
  "success": true,
  "message": "Email sent successfully",
  "to_email": "recipient@example.com",
  "subject": "Meeting Summary"
}
```

For complete setup instructions, troubleshooting, and advanced configuration, see [POWER_AUTOMATE_INTEGRATION.md](POWER_AUTOMATE_INTEGRATION.md).

**Other integrations**:
- Document analysis (PDF, Word, etc.)
- Database queries
- Code execution (sandboxed)
- Image analysis
- Chart generation
- And more...

## 🎮 Example Output

```
📋 Research Query 1:
   What are the key differences between machine learning and deep learning?
----------------------------------------------------------------------

🤖 Agent Response:
   Machine learning is a broader field that includes various algorithms
   for learning from data, while deep learning is a subset that uses
   neural networks with multiple layers...

💭 Reasoning Chain:
   🔧 Using web_search tool: {'query': 'machine learning vs deep learning'}
   💭 Let me analyze these search results to identify key differences...
   💭 Based on these sources, I can conclude that the main differences are...
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server_alpha --cov-report=html

# Run specific tests
pytest tests/unit/test_agent.py
```

## 🛠️ Tech Stack

- **LangGraph**: Workflow orchestration and agent framework
- **LangChain**: Tool integration and LLM interfaces
- **OpenAI**: GPT-4o-mini for reasoning (or any OpenAI model)
- **Pydantic**: Type-safe models and validation
- **Python 3.10+**: Modern async/await patterns

## 🔐 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `POWER_AUTOMATE_WEBHOOK_URL`: Power Automate flow webhook URL for sending emails (optional, required for send_email tool)

### Agent Parameters

```python
ResearchAgent(
    model="gpt-4o-mini",  # or "gpt-4o", "gpt-4-turbo"
    temperature=0.7,      # 0.0-1.0, higher = more creative
    api_key="sk-..."      # or use env var
)
```

## 🌟 Features

### Current
- ✅ Autonomous research with reasoning chains
- ✅ Multi-tool orchestration
- ✅ Context-aware conversations
- ✅ Visible thought process
- ✅ Extensible tool system
- ✅ OpenAI integration
- ✅ Real-time weather forecasts via weather.gov API
- ✅ Email sending via Power Automate flow webhooks

### Coming Soon
- 🔄 Real web search integration (Google, Bing)
- 📄 Document analysis (PDF, Word, markdown)
- 💾 Memory/RAG for long-term knowledge
- 🎨 Visualization generation
- 🔗 More integrations (GitHub, databases, etc.)
- 🌐 Web UI for interactive research

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tool or enhancement
4. Write tests
5. Submit a pull request

## 📄 License

Proprietary - TC Digital

## 💬 Support

- Open an issue for bugs or questions
- Check examples/ directory for more usage patterns
- See docs/ for detailed documentation

---

**Built with ❤️ using LangGraph and OpenAI**

*From insurance MCP server to autonomous research assistant - showcasing the power of modular, agentic architecture!*
