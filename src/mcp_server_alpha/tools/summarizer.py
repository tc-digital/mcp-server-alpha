"""Text summarization tool."""
from typing import Any


async def summarize_tool(
    text: str, max_length: int = 200, style: str = "concise"
) -> dict[str, Any]:
    """
    Summarize text content.

    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        style: Summary style (concise, detailed, bullet_points)

    Returns:
        Dictionary with summary and metadata
    """
    # Mock implementation - in production, use LLM or extractive summarization

    # Simple mock: take first portion of text
    words = text.split()
    if len(words) <= max_length // 5:  # Rough word estimate
        summary = text
    else:
        summary = " ".join(words[: max_length // 5]) + "..."

    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": len(summary) / len(text) if text else 0,
        "style": style,
    }
