# src/utils/text_utils.py

import re
from rich.console import Console

console = Console()


def highlight_matches(text: str, matches: list[str]) -> str:
    """Highlights matches within a text string using Rich."""
    highlighted_text = text
    for match in matches:
        # Escape special characters in the match for regex
        escaped_match = re.escape(match)
        # Use re.sub with a replacement function for more control
        highlighted_text = re.sub(
            f"({escaped_match})",  # Capture the match
            r"[bold yellow]\1[/bold yellow]",  # Highlight with bold yellow
            highlighted_text,
            flags=re.IGNORECASE,
        )
    return highlighted_text


def extract_context(text: str, matches: list[str], context_length: int = 20) -> str:
    """Extracts context around matches, highlighting the matches."""
    snippets = []
    for match in matches:
        for match_obj in re.finditer(re.escape(match), text, re.IGNORECASE):
            start = max(0, match_obj.start() - context_length)
            end = min(len(text), match_obj.end() + context_length)
            snippet = text[start:end]
            highlighted_snippet = highlight_matches(snippet, [match])
            snippets.append(highlighted_snippet)
    return "\n".join(snippets)
