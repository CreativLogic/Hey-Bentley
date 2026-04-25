"""
Bentley Voice — Notion MCP Integration
Read and write pages/databases via the Notion API.
"""
from notion_client import Client
from datetime import datetime
from config import NOTION_API_KEY, NOTION_DEFAULT_DB_ID
from rich.console import Console

console = Console()

_client = None


def get_client() -> Client:
    global _client
    if not _client:
        if not NOTION_API_KEY:
            raise ValueError(
                "NOTION_API_KEY is not set. Add it to your .env file."
            )
        _client = Client(auth=NOTION_API_KEY)
    return _client


# ── READ ──────────────────────────────────────────────────────────────────

def read_page(page_id: str) -> str:
    """Fetch all text blocks from a Notion page and return as markdown."""
    client  = get_client()
    blocks  = client.blocks.children.list(block_id=page_id)
    lines   = []

    for block in blocks.get("results", []):
        btype = block.get("type", "")
        data  = block.get(btype, {})
        rich_texts = data.get("rich_text", [])
        text = "".join(t.get("plain_text", "") for t in rich_texts)

        if btype == "heading_1":
            lines.append(f"# {text}")
        elif btype == "heading_2":
            lines.append(f"## {text}")
        elif btype == "heading_3":
            lines.append(f"### {text}")
        elif btype == "bulleted_list_item":
            lines.append(f"- {text}")
        elif btype == "numbered_list_item":
            lines.append(f"1. {text}")
        elif btype == "code":
            lang = data.get("language", "")
            lines.append(f"```{lang}\n{text}\n```")
        elif btype == "paragraph":
            lines.append(text)
        elif btype == "divider":
            lines.append("---")

    return "\n\n".join(lines)


def search_notion(query: str, max_results: int = 5) -> list[dict]:
    """Search Notion for pages matching the query."""
    client  = get_client()
    results = client.search(query=query, page_size=max_results)
    pages   = []
    for r in results.get("results", []):
        title = _extract_title(r)
        pages.append({"id": r["id"], "title": title, "url": r.get("url", "")})
    return pages


def _extract_title(page: dict) -> str:
    props = page.get("properties", {})
    for key in ["Name", "Title", "title", "name"]:
        prop = props.get(key, {})
        rich = prop.get("title", []) or prop.get("rich_text", [])
        if rich:
            return rich[0].get("plain_text", "Untitled")
    return "Untitled"


# ── WRITE ─────────────────────────────────────────────────────────────────

def _md_to_blocks(markdown: str) -> list[dict]:
    """Convert markdown text to Notion block objects (basic conversion)."""
    blocks = []
    for line in markdown.split("\n"):
        if line.startswith("# "):
            blocks.append(_heading(line[2:], 1))
        elif line.startswith("## "):
            blocks.append(_heading(line[3:], 2))
        elif line.startswith("### "):
            blocks.append(_heading(line[4:], 3))
        elif line.startswith("- "):
            blocks.append(_bullet(line[2:]))
        elif line.startswith("1. "):
            blocks.append(_numbered(line[3:]))
        elif line.startswith("---"):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        else:
            blocks.append(_paragraph(line))
    return blocks


def _rich(text: str) -> list:
    return [{"type": "text", "text": {"content": text}}]


def _heading(text, level):
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {"rich_text": _rich(text)}}


def _paragraph(text):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": _rich(text)}}


def _bullet(text):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": _rich(text)}}


def _numbered(text):
    return {"object": "block", "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": _rich(text)}}


def create_page(title: str, content: str, database_id: str = "") -> str:
    """Create a new Notion page with markdown content. Returns the page URL."""
    client = get_client()
    db_id  = database_id or NOTION_DEFAULT_DB_ID
    if not db_id:
        raise ValueError("No Notion database ID set. Check NOTION_DEFAULT_DATABASE_ID in .env")

    blocks = _md_to_blocks(content)

    page = client.pages.create(
        parent={"database_id": db_id},
        properties={
            "Name": {"title": _rich(title)},
        },
        children=blocks[:100],  # Notion API limit per request
    )
    return page.get("url", page["id"])


def update_page(page_id: str, content: str) -> str:
    """Append new markdown content blocks to an existing Notion page."""
    client = get_client()
    blocks = _md_to_blocks(content)
    client.blocks.children.append(block_id=page_id, children=blocks[:100])
    return f"Page {page_id} updated."
