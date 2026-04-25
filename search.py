"""
Bentley Voice — Web Search
Uses DuckDuckGo (no API key required).
"""
from duckduckgo_search import DDGS
from config import SEARCH_MAX_RESULTS
from rich.console import Console

console = Console()


def web_search(query: str, max_results: int = SEARCH_MAX_RESULTS) -> list[dict]:
    """
    Returns a list of dicts: [{title, href, body}, ...]
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        console.print(f"[red]Search error:[/red] {e}")
        return []


def format_search_summary(results: list[dict]) -> str:
    """Convert results to a spoken-friendly summary string."""
    if not results:
        return "I could not find anything for that query."

    lines = []
    for i, r in enumerate(results[:3], 1):
        title = r.get("title", "No title")
        body  = r.get("body", "")[:200]
        lines.append(f"{i}. {title}. {body}")

    return " ... ".join(lines)


def format_search_markdown(query: str, results: list[dict]) -> str:
    """Convert results to a markdown-formatted string for saving."""
    md = f"# Search Results: {query}\n\n"
    for r in results:
        title = r.get("title", "No title")
        href  = r.get("href", "")
        body  = r.get("body", "")
        md += f"## [{title}]({href})\n\n{body}\n\n---\n\n"
    return md
