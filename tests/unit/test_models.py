"""Tests for research models."""
from mcp_server_alpha.models import ReasoningType, ResearchQuery, ResearchQueryType, ThoughtChain


def test_research_query_creation():
    """Test creating a research query."""
    query = ResearchQuery(
        query="What is machine learning?",
        query_type=ResearchQueryType.FACTUAL,
        depth=2,
        max_sources=10,
    )

    assert query.query == "What is machine learning?"
    assert query.query_type == ResearchQueryType.FACTUAL
    assert query.depth == 2
    assert query.max_sources == 10


def test_thought_chain_creation():
    """Test creating a thought chain."""
    chain = ThoughtChain(query="Test query")

    assert chain.query == "Test query"
    assert len(chain.steps) == 0
    assert chain.final_conclusion is None


def test_thought_chain_add_step():
    """Test adding steps to thought chain."""
    chain = ThoughtChain(query="Test query")

    step1 = chain.add_step(
        ReasoningType.OBSERVATION, "I observe X", ["evidence 1"]
    )
    step2 = chain.add_step(ReasoningType.ANALYSIS, "Analyzing Y")

    assert len(chain.steps) == 2
    assert step1.step_id == 1
    assert step2.step_id == 2
    assert step1.thought == "I observe X"
    assert len(step1.evidence) == 1
