# Research Assistant with LangGraph

An intelligent, autonomous research assistant powered by LangGraph and OpenAI that demonstrates visible reasoning chains and multi-tool orchestration.

## 🚀 Quick Start

Get up and running in under 2 minutes!

### Option 1: Automated Setup Script (Recommended)

**Linux/macOS:**
```bash
git clone https://github.com/tc-digital/mcp-server-alpha.git
cd mcp-server-alpha
./setup.sh
```

**Windows:**
```cmd
git clone https://github.com/tc-digital/mcp-server-alpha.git
cd mcp-server-alpha
setup.bat
```

The scripts will:
- ✅ Create and activate a virtual environment
- ✅ Install all dependencies automatically
- ✅ Check your environment configuration
- ✅ Optionally start the MCP server

### Option 2: Docker (Containerized Deployment)

```bash
# Build the Docker image
docker build -t mcp-server-alpha .

# Run with environment variables
docker run -it --rm \
  -e OPENAI_API_KEY='your-api-key-here' \
  -e POWER_AUTOMATE_WEBHOOK_URL='your-webhook-url' \
  mcp-server-alpha
```

For Docker Compose, create a `docker-compose.yml`:
```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POWER_AUTOMATE_WEBHOOK_URL=${POWER_AUTOMATE_WEBHOOK_URL}
    # Uncomment if you add HTTP API endpoints:
    # ports:
    #   - "8000:8000"
```

Then run: `docker-compose up`

### Option 3: Manual Installation

**Prerequisites:**
- Python 3.10 or higher
- OpenAI API key

```bash
# Clone and navigate
git clone https://github.com/tc-digital/mcp-server-alpha.git
cd mcp-server-alpha

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Environment Variables

Set these environment variables before running:

```bash
# Required for OpenAI-powered research
export OPENAI_API_KEY='sk-...'

# Optional for send_email tool
export POWER_AUTOMATE_WEBHOOK_URL='https://prod-...'
```

**Windows (cmd):**
```cmd
set OPENAI_API_KEY=sk-...
set POWER_AUTOMATE_WEBHOOK_URL=https://prod-...
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:POWER_AUTOMATE_WEBHOOK_URL="https://prod-..."
```

### Running the Server

**MCP Server (for Claude Desktop):**
```bash
python -m mcp_server_alpha.server
```

**Research Example:**
```bash
python examples/research_example.py
```

### Troubleshooting

**Issue: "OPENAI_API_KEY not set"**
- Solution: Set the environment variable before running (see Environment Variables above)

**Issue: "Python 3.10 or higher is required"**
- Solution: Upgrade Python or use Docker

**Issue: "Module not found" errors**
- Solution: Ensure virtual environment is activated and dependencies are installed
  ```bash
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -e ".[dev]"
  ```

**Issue: Docker build fails**
- Solution: Ensure Docker is installed and running, then try: `docker system prune` and rebuild

**Claude Desktop Integration Issues:**
- See [TROUBLESHOOTING_CLAUDE_DESKTOP.md](TROUBLESHOOTING_CLAUDE_DESKTOP.md)

## 🎯 What It Does

This research assistant can:
- **🔍 Research any topic** using web search and information gathering
- **🧮 Perform calculations** for mathematical and financial queries
- **📊 Analyze data** to find patterns and insights
- **📝 Summarize content** to extract key information
- **🌤️ Get weather forecasts** for any US location by zip code or coordinates
- **📧 Send emails** via Power Automate flow webhooks
- **🤖 Autonomous reasoning agent** for complex multi-step tasks (NEW!)
- **💭 Show its reasoning** with visible thought chains

## 🆕 Reasoning Agent Meta-Tool

The **Reasoning Agent** is a meta-tool that orchestrates other MCP tools using LangGraph for autonomous planning and execution. Perfect for complex tasks requiring multiple steps and decision-making.

**Example**: *"Research renewable energy trends, analyze the data, and calculate the growth rate"*

The agent will:
1. 🔍 Search for renewable energy information
2. 📊 Analyze the data found
3. 🧮 Calculate growth rates
4. 💡 Synthesize results into a comprehensive answer

**📖 [Full Reasoning Agent Documentation](REASONING_AGENT.md)**

## 🏗️ Architecture

```
src/mcp_server_alpha/
├── models/          # Research models (Query, Result, ThoughtChain, etc.)
├── tools/           # Research tools (search, calculator, analyzer, summarizer, weather, send_email)
├── agents/          # LangGraph agent with reasoning chains + Reasoning Orchestrator (NEW)
├── orchestration/   # Workflow engine for complex tasks
├── adapters/        # Multi-channel adapters (chat, voice, API)
└── server.py        # MCP server implementation
```

### Key Components

#### 1. **Reasoning Agent Orchestrator** (`agents/reasoning_orchestrator.py`) - NEW!
- Meta-tool that orchestrates other MCP tools using LangGraph
- Autonomous goal decomposition and task planning
- Multi-step execution with branching logic
- Step-by-step progress tracking with visible reasoning

#### 2. **Research Agent** (`agents/research_agent.py`)
- LangGraph-based autonomous agent
- Uses OpenAI (gpt-4o-mini by default) for reasoning
- Visible thought process and reasoning chains
- Tool orchestration based on research needs

#### 3. **Research Tools** (`tools/`)
- **Web Search**: Find information on any topic (mock, ready for real API)
- **Calculator**: Perform mathematical calculations
- **Data Analyzer**: Statistical analysis and pattern finding
- **Summarizer**: Extract key information from text
- **Weather Forecast**: Get real-time weather forecasts using weather.gov API
- **Send Email**: Trigger Power Automate flow to send emails via webhook

#### 4. **Reasoning Chain** (`models/reasoning.py`)
- Tracks agent's thought process
- Shows observations, analysis, synthesis, and conclusions
- Helps understand how the agent reaches answers

#### 5. **Config-Driven System**
- Easy to add new tools and integrations
- No code changes needed for new capabilities
- Pluggable architecture

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

# Multi-step research with reasoning agent
"Research renewable energy trends and calculate the growth rate"
```

For Claude Desktop users, see the [Quick Start](#-quick-start) section for setup instructions.

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
# Configure in Claude Desktop config or as system environment variable
# Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json
# Add to "env" section: "POWER_AUTOMATE_WEBHOOK_URL": "https://..."

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

**Important**: After configuring Claude Desktop, completely quit and restart the application.

**Troubleshooting**: If you get configuration errors, see [TROUBLESHOOTING_CLAUDE_DESKTOP.md](TROUBLESHOOTING_CLAUDE_DESKTOP.md).

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

The following environment variables configure the server:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key for GPT models |
| `POWER_AUTOMATE_WEBHOOK_URL` | ⚠️ Optional | Power Automate webhook URL for send_email tool |

**Setting Environment Variables:**

**Linux/macOS (bash/zsh):**
```bash
export OPENAI_API_KEY='sk-...'
export POWER_AUTOMATE_WEBHOOK_URL='https://prod-...'
```

**Windows (cmd):**
```cmd
set OPENAI_API_KEY=sk-...
set POWER_AUTOMATE_WEBHOOK_URL=https://prod-...
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:POWER_AUTOMATE_WEBHOOK_URL="https://prod-..."
```

**Docker:**
```bash
docker run -e OPENAI_API_KEY='sk-...' -e POWER_AUTOMATE_WEBHOOK_URL='https://...' mcp-server-alpha
```

**Claude Desktop Configuration:**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "mcp-server-alpha": {
      "command": "python",
      "args": ["-m", "mcp_server_alpha.server"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "POWER_AUTOMATE_WEBHOOK_URL": "https://..."
      }
    }
  }
}
```

**Important**: After configuring Claude Desktop, completely quit and restart the application.

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
- ✅ **Reasoning Agent meta-tool for complex multi-step task orchestration (NEW!)**
- ✅ Multi-tool orchestration
- ✅ Context-aware conversations
- ✅ Visible thought process and step-by-step execution tracking
- ✅ Extensible tool system
- ✅ OpenAI integration
- ✅ Real-time weather forecasts via weather.gov API
- ✅ Email sending via Power Automate flow webhooks

### Coming Soon
- 🔄 Real web search integration (Google, Bing)
- 📄 Document analysis (PDF, Word, markdown)
- 💾 Memory/RAG for long-term knowledge
- 🎨 Visualization generation
- 🌊 Streaming progress updates for reasoning agent
- ✅ User prompt/parameter collection for reasoning agent
- 📊 Visual flowchart of reasoning agent execution
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
