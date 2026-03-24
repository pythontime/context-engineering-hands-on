"""
ANSI-colored terminal output helpers.

No external dependencies (no rich, no colorama) — just ANSI escape codes.
Keeps the demo lightweight and the output code inspectable.
"""

from __future__ import annotations

import json
import sys
from typing import Any

# ── ANSI escape codes ────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

# Colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
WHITE = "\033[37m"

# Background
BG_DARK = "\033[48;5;236m"


def _print(text: str) -> None:
    """Print with flush for streaming compatibility."""
    print(text, flush=True)


# ── Public display methods ───────────────────────────────────────────


def tool_call(name: str, tool_input: dict[str, Any]) -> None:
    """Display a tool call the agent is making."""
    input_str = json.dumps(tool_input, indent=2) if tool_input else "{}"
    _print(f"\n  {YELLOW}⚡ Tool call:{RESET} {BOLD}{name}{RESET}")
    for line in input_str.split("\n"):
        _print(f"  {DIM}  {line}{RESET}")


def tool_result(name: str, result: str, truncate: int = 300) -> None:
    """Display a tool result (truncated for readability)."""
    preview = result[:truncate]
    if len(result) > truncate:
        preview += f"... ({len(result) - truncate} more chars)"
    _print(f"  {GREEN}✓ Result from {name}:{RESET}")
    for line in preview.split("\n"):
        _print(f"  {DIM}  {line}{RESET}")


def context_stats(
    turn_count: int,
    message_count: int,
    tool_call_count: int,
    input_tokens: int,
    output_tokens: int,
) -> None:
    """Display a context statistics box after each turn."""
    total = input_tokens + output_tokens
    box_width = 52
    _print(f"\n  {CYAN}{'─' * box_width}{RESET}")
    _print(f"  {CYAN}│{RESET} {BOLD}Context Stats{RESET}{' ' * (box_width - 17)}{CYAN}│{RESET}")
    _print(f"  {CYAN}{'─' * box_width}{RESET}")
    _print(f"  {CYAN}│{RESET}  Turns: {turn_count:<8} Messages: {message_count:<8} Tools: {tool_call_count:<5}{CYAN}│{RESET}")
    _print(f"  {CYAN}│{RESET}  Input: {input_tokens:<8} Output: {output_tokens:<8} Total: {total:<5}{CYAN}│{RESET}")
    _print(f"  {CYAN}{'─' * box_width}{RESET}")


def context_snapshot(messages: list[dict]) -> None:
    """
    Display the raw messages array — the actual context window.

    This is the /context command: students see exactly what the model receives.
    """
    _print(f"\n  {MAGENTA}{BOLD}📋 Context Window Snapshot{RESET}")
    _print(f"  {MAGENTA}{'─' * 52}{RESET}")
    _print(f"  {DIM}Total messages: {len(messages)}{RESET}\n")

    for i, msg in enumerate(messages):
        role = msg["role"]
        if role == "user":
            # Check if it's a tool_result or actual user message
            content = msg.get("content", "")
            if isinstance(content, list):
                # Tool result messages have list content
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        tool_id = block.get("tool_use_id", "?")
                        result_content = block.get("content", "")
                        preview = str(result_content)[:80]
                        _print(
                            f"  {GREEN}[{i}] tool_result{RESET} {DIM}(id: {tool_id[:12]}…){RESET}"
                        )
                        _print(f"      {DIM}{preview}...{RESET}")
                    else:
                        text = block.get("text", str(block))[:80]
                        _print(f"  {BLUE}[{i}] user{RESET}: {text}")
            else:
                text = str(content)[:80]
                _print(f"  {BLUE}[{i}] user{RESET}: {text}")

        elif role == "assistant":
            content = msg.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_use":
                            _print(
                                f"  {YELLOW}[{i}] assistant → tool_use{RESET}: "
                                f"{block.get('name', '?')}({json.dumps(block.get('input', {}))[:60]})"
                            )
                        elif block.get("type") == "text":
                            text = block.get("text", "")[:80]
                            _print(f"  {WHITE}[{i}] assistant{RESET}: {text}")
                    else:
                        _print(f"  {WHITE}[{i}] assistant{RESET}: {str(block)[:80]}")
            else:
                text = str(content)[:80]
                _print(f"  {WHITE}[{i}] assistant{RESET}: {text}")

    _print(f"\n  {MAGENTA}{'─' * 52}{RESET}")


def system_message(text: str) -> None:
    """Display a system/info message."""
    _print(f"  {CYAN}{text}{RESET}")


def error(text: str) -> None:
    """Display an error message."""
    _print(f"  {RED}✗ {text}{RESET}")


def welcome_banner() -> None:
    """Display the welcome banner on startup."""
    _print(f"""
  {CYAN}{BOLD}╔══════════════════════════════════════════════════╗
  ║     🔍 Agentic Document Retrieval Demo          ║
  ║     Context Engineering Hands-On                 ║
  ╚══════════════════════════════════════════════════╝{RESET}

  {DIM}This demo shows how context flows through an agent loop.
  Watch the messages array grow as the agent retrieves documents.{RESET}

  {BOLD}Commands:{RESET}
    /help     Show this help
    /context  Inspect the raw messages array (context window)
    /stats    Show cumulative token statistics
    /clear    Reset conversation and stats
    /docs     List available knowledge base documents
    /quit     Exit

  {DIM}Try: "What documents do you have?" or "Explain context engineering"{RESET}
""")


def assistant_text(text: str) -> None:
    """Display the assistant's text response."""
    _print(f"\n  {BOLD}Assistant:{RESET} {text}")


def streaming_start() -> None:
    """Print the assistant label before streaming begins."""
    sys.stdout.write(f"\n  {BOLD}Assistant:{RESET} ")
    sys.stdout.flush()


def streaming_token(token: str) -> None:
    """Print a single streaming token."""
    sys.stdout.write(token)
    sys.stdout.flush()


def streaming_end() -> None:
    """End the streaming line."""
    _print("")
