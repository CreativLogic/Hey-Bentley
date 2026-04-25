"""
Bentley Voice — File Manager
Read and write markdown files locally.
"""
from pathlib import Path
from datetime import datetime
from config import FILES_DIR
from rich.console import Console

console = Console()


def _safe_path(filename: str) -> Path:
    """Ensure filename is safe and ends with .md"""
    name = Path(filename).stem  # strip extension
    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
    safe = safe.strip().replace(" ", "-")
    return FILES_DIR / f"{safe}.md"


def write_file(filename: str, content: str, overwrite: bool = False) -> str:
    """
    Write a markdown file. Returns the path written.
    If file exists and overwrite=False, appends a timestamp suffix.
    """
    path = _safe_path(filename)

    if path.exists() and not overwrite:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = FILES_DIR / f"{path.stem}-{stamp}.md"

    path.write_text(content, encoding="utf-8")
    console.print(f"[green]File written:[/green] {path}")
    return str(path)


def read_file(filename: str) -> str:
    """Read a markdown file. Returns content string or an error message."""
    path = _safe_path(filename)
    if not path.exists():
        # Try partial match
        matches = list(FILES_DIR.glob(f"*{Path(filename).stem}*.md"))
        if matches:
            path = matches[0]
        else:
            return f"No file named '{filename}' found in {FILES_DIR}."

    return path.read_text(encoding="utf-8")


def list_files() -> list[str]:
    """Return a list of all markdown filenames in the files directory."""
    return sorted(p.name for p in FILES_DIR.glob("*.md"))


def delete_file(filename: str) -> str:
    """Delete a markdown file. Returns confirmation or error."""
    path = _safe_path(filename)
    if not path.exists():
        return f"File '{filename}' does not exist."
    path.unlink()
    return f"Deleted {path.name}."
