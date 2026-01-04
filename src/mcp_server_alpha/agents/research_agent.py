"""LangGraph-based research assistant agent."""
import os
from typing import Annotated, Any, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from .tools import ResearchTools


class AgentState(TypedDict):
    """State for the research agent."""

    messages: Annotated[list[BaseMessage], add_messages]


class ResearchAgent:
    """
    LangGraph-based research assistant agent.

    This agent autonomously researches topics using multiple tools:
    - Web search for information gathering
    - Calculator for mathematical operations
    - Text summarization for condensing information
    - Data analysis for insights

    Features:
    - Visible reasoning chain showing thought process
    - Tool orchestration based on research needs
    - Context-aware across research sessions
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """
        Initialize the research agent.

        Args:
            api_key: OpenAI API key (or None to use OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: LLM temperature for response generation
        """
        # Initialize LLM
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key param"
            )

        # Get tools
        research_tools = ResearchTools()
        self.tools = research_tools.get_tools()

        # Bind tools to LLM
        self.llm = ChatOpenAI(
            model=model, temperature=temperature, api_key=api_key
        ).bind_tools(self.tools)

        # Create agent graph
        self.graph = self._create_agent_graph()

    def _create_agent_graph(self) -> StateGraph:
        """Create the LangGraph agent workflow."""
        # Define the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))

        # Set entry point
        workflow.set_entry_point("agent")

        # Add edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def _agent_node(self, state: AgentState) -> dict[str, Any]:
        """Agent reasoning node with visible thought process."""
        messages = list(state["messages"])

        # Add system message with research context if not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            system_msg = SystemMessage(
                content="""You are an advanced research assistant with autonomous \
reasoning capabilities.

Your role is to:
1. **Research topics thoroughly** using web search, data analysis, and calculation tools
2. **Show your reasoning process** - explain what you're thinking and why
3. **Break down complex questions** into manageable research tasks
4. **Synthesize information** from multiple sources
5. **Provide clear, well-reasoned answers** with evidence

When researching:
- Start by understanding what information you need
- Use web_search to find relevant information
- Use summarize_text to condense long content
- Use calculate for any mathematical operations
- Use analyze_data to find patterns and insights

Always explain your thought process:
- "I need to search for X because..."
- "Let me analyze this data to understand..."
- "Based on these sources, I can conclude..."

Be curious, thorough, and show your reasoning chain!"""
            )
            messages.insert(0, system_msg)

        # Get LLM response
        response = self.llm.invoke(messages)

        # Return only the new response - add_messages will handle appending
        return {"messages": [response]}

    def _should_continue(self, state: AgentState) -> Literal["tools", "__end__"]:
        """Decide whether to continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the last message has tool calls, continue to tools
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"

        # Otherwise, end
        return END

    async def research(
        self, query: str, state: AgentState | None = None
    ) -> dict[str, Any]:
        """
        Research a topic and return findings with reasoning chain.

        Args:
            query: Research question or topic
            state: Optional previous state to maintain context

        Returns:
            Dict with response, reasoning chain, and updated state
        """
        # Initialize state if needed
        if state is None:
            state = {"messages": []}

        # Add user message
        user_message = HumanMessage(content=query)

        # Run agent with the user message
        result = await self.graph.ainvoke(
            {"messages": state["messages"] + [user_message]}
        )

        # Extract response
        response_messages = result["messages"]
        last_ai_message = None
        for msg in reversed(response_messages):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                last_ai_message = msg
                break

        response_text = (
            last_ai_message.content
            if last_ai_message and hasattr(last_ai_message, "content")
            else "I'm here to help with research!"
        )

        # Extract reasoning from messages
        reasoning_steps = self._extract_reasoning(result["messages"])

        return {
            "response": response_text,
            "reasoning_chain": reasoning_steps,
            "state": result,
        }

    def _extract_reasoning(self, messages: list[BaseMessage]) -> list[str]:
        """Extract reasoning steps from conversation."""
        reasoning = []

        for msg in messages:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    # Agent decided to use tools
                    for tool_call in msg.tool_calls:
                        reasoning.append(
                            f"🔧 Using {tool_call['name']} tool: {tool_call.get('args', {})}"
                        )
                elif msg.content:
                    # Agent's reasoning or conclusion
                    if any(
                        keyword in msg.content.lower()
                        for keyword in [
                            "because",
                            "therefore",
                            "let me",
                            "i need to",
                            "based on",
                        ]
                    ):
                        reasoning.append(f"💭 {msg.content[:200]}...")

        return reasoning
