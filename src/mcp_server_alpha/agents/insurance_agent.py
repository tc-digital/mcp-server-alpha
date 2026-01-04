"""LangGraph-based insurance agent with OpenAI integration."""
import os
from typing import Any, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from ..config import ProductRegistry
from ..models import Consumer
from ..providers import ProviderRegistry
from .tools import AgentTools


class AgentState(BaseModel):
    """State for the insurance agent."""

    messages: list[BaseMessage] = Field(default_factory=list)
    consumer: Consumer | None = None
    current_product_id: str | None = None
    last_action: str | None = None


class InsuranceAgent:
    """
    LangGraph-based conversational agent for insurance product interactions.

    This agent uses OpenAI (or compatible LLMs) to:
    - Understand natural language queries about products
    - Guide users through product discovery and eligibility
    - Explain quotes and recommendations in conversational language
    - Maintain context across multi-turn conversations
    """

    def __init__(
        self,
        product_registry: ProductRegistry,
        provider_registry: ProviderRegistry,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """
        Initialize the insurance agent.

        Args:
            product_registry: Registry of available products
            provider_registry: Registry of insurance providers
            api_key: OpenAI API key (or None to use OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: LLM temperature for response generation
        """
        self.product_registry = product_registry
        self.provider_registry = provider_registry

        # Initialize LLM
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key param"
            )

        # Get tools
        agent_tools = AgentTools(product_registry, provider_registry)
        self.tools = agent_tools.get_tools()

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
        """Agent reasoning node."""
        messages = state.messages

        # Add system message with context if it's the first message
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            system_msg = SystemMessage(
                content="""You are a helpful insurance assistant. You help users:
1. Search for insurance products (health, dental, vision, life, etc.)
2. Check if they're eligible for specific products
3. Get quotes with pricing information
4. Discover related products that might interest them

Be conversational, friendly, and clear. When you need information about products or
eligibility, use the available tools. Always explain eligibility requirements and
quote details in simple terms.

When a user asks about products, use search_products first.
When checking eligibility or quotes, you'll need consumer information (age, state, zip code).
If the user doesn't provide this info, ask for it politely."""
            )
            messages = [system_msg] + messages

        # Get LLM response
        response = self.llm.invoke(messages)

        return {"messages": messages + [response]}

    def _should_continue(self, state: AgentState) -> Literal["tools", "__end__"]:
        """Decide whether to continue to tools or end."""
        messages = state.messages
        last_message = messages[-1]

        # If the last message has tool calls, continue to tools
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"

        # Otherwise, end
        return END

    async def chat(
        self,
        message: str,
        state: AgentState | None = None,
    ) -> dict[str, Any]:
        """
        Process a user message and return agent response.

        This method is defensive against LangGraph returning raw dicts
        instead of AgentState instances.
        """

        # 1. Initialize state if needed
        if state is None:
            state = AgentState()

        # 2. Append user message
        state.messages.append(HumanMessage(content=message))

        # 3. Invoke LangGraph
        raw_result = await self.graph.ainvoke(state)

        # 4. Rehydrate state defensively
        if isinstance(raw_result, AgentState):
            result_state = raw_result
        elif isinstance(raw_result, dict):
            result_state = AgentState(**raw_result)
        else:
            # Extremely defensive fallback (should never happen)
            result_state = AgentState(messages=state.messages)

        # 5. Extract the latest AI response that is NOT a tool call
        last_ai_message: AIMessage | None = None

        for msg in reversed(result_state.messages):
            if isinstance(msg, AIMessage):
                # Skip tool call messages
                if getattr(msg, "tool_calls", None):
                    continue
                last_ai_message = msg
                break

        # 6. Final response text
        response_text = (
            last_ai_message.content
            if last_ai_message and isinstance(last_ai_message.content, str)
            else "I'm here to help with insurance questions!"
        )

        # 7. Return response + updated state
        return {
            "response": response_text,
            "state": result_state,
        }


    def create_sample_consumer(
        self, age: int, state: str, zip_code: str, **kwargs: Any
    ) -> Consumer:
        """
        Helper to create a Consumer object from natural language input.

        Args:
            age: Consumer age
            state: State abbreviation (e.g., "CA")
            zip_code: ZIP code
            **kwargs: Additional profile attributes

        Returns:
            Consumer instance
        """
        import uuid
        from datetime import date, datetime

        from ..models import ConsumerProfile

        # Calculate birth year from age
        current_year = datetime.now().year
        birth_year = current_year - age

        profile = ConsumerProfile(
            age=age,
            state=state,
            zip_code=zip_code,
            income=kwargs.get("income"),
            employment_status=kwargs.get("employment_status"),
            household_size=kwargs.get("household_size", 1),
            has_medicare=kwargs.get("has_medicare", False),
            has_medicaid=kwargs.get("has_medicaid", False),
            tobacco_user=kwargs.get("tobacco_user", False),
        )

        return Consumer(
            id=str(uuid.uuid4()),
            first_name=kwargs.get("first_name", "User"),
            last_name=kwargs.get("last_name", ""),
            email=kwargs.get("email", "user@example.com"),
            date_of_birth=date(birth_year, 1, 1),
            profile=profile,
        )
