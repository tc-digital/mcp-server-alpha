"""Data analysis tool."""
from typing import Any


async def analyze_data_tool(
    data: list[Any], analysis_type: str = "statistical"
) -> dict[str, Any]:
    """
    Analyze data and provide insights.

    Args:
        data: Data to analyze (list of numbers, strings, or dicts)
        analysis_type: Type of analysis (statistical, trend, pattern, etc.)

    Returns:
        Dictionary with analysis results
    """
    if not data:
        return {
            "analysis_type": analysis_type,
            "insights": [],
            "error": "No data provided",
        }

    insights = []

    # Basic statistical analysis for numeric data
    if all(isinstance(x, (int, float)) for x in data):
        numeric_data = [float(x) for x in data]

        mean_val = sum(numeric_data) / len(numeric_data)
        sorted_data = sorted(numeric_data)
        median_val = sorted_data[len(sorted_data) // 2]
        min_val = min(numeric_data)
        max_val = max(numeric_data)

        insights.append(f"Mean: {mean_val:.2f}")
        insights.append(f"Median: {median_val:.2f}")
        insights.append(f"Range: {min_val:.2f} to {max_val:.2f}")
        insights.append(f"Count: {len(numeric_data)}")

    else:
        # For non-numeric data, provide basic info
        insights.append(f"Total items: {len(data)}")
        insights.append(f"Data types: {set(type(x).__name__ for x in data)}")

    return {
        "analysis_type": analysis_type,
        "insights": insights,
        "data_summary": {
            "count": len(data),
            "sample": data[:3] if len(data) > 3 else data,
        },
    }
