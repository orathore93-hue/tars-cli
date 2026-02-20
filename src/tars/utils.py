"""Utility functions for formatting and display"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from typing import List, Dict, Any
import logging
import re

console = Console()
logger = logging.getLogger(__name__)

# Sensitive data patterns for redaction
SENSITIVE_PATTERNS = [
    (re.compile(r'password["\s:=]+[^\s"]+', re.IGNORECASE), 'password=<REDACTED>'),
    (re.compile(r'token["\s:=]+[^\s"]+', re.IGNORECASE), 'token=<REDACTED>'),
    (re.compile(r'api[_-]?key["\s:=]+[^\s"]+', re.IGNORECASE), 'api_key=<REDACTED>'),
    (re.compile(r'secret["\s:=]+[^\s"]+', re.IGNORECASE), 'secret=<REDACTED>'),
    (re.compile(r'bearer\s+[^\s]+', re.IGNORECASE), 'bearer <REDACTED>'),
    (re.compile(r'authorization:\s*[^\s]+', re.IGNORECASE), 'authorization: <REDACTED>'),
    # AWS keys
    (re.compile(r'AKIA[0-9A-Z]{16}'), '<REDACTED_AWS_KEY>'),
    # Private keys
    (re.compile(r'-----BEGIN.*PRIVATE KEY-----.*?-----END.*PRIVATE KEY-----', re.DOTALL), '<REDACTED_PRIVATE_KEY>'),
]


def redact_sensitive_data(text: str) -> str:
    """
    Redact sensitive information from text before sending to AI or logging.
    
    Args:
        text: Text that may contain sensitive data
        
    Returns:
        Text with sensitive data redacted
    """
    if not text:
        return text
    
    redacted = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    
    return redacted


def create_table(title: str, columns: List[str]) -> Table:
    """Create a formatted table"""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)
    return table


def print_error(message: str):
    """Print error message"""
    console.print(f"[bold red]✗[/bold red] {message}")
    logger.error(message)


def print_success(message: str):
    """Print success message"""
    console.print(f"[bold green]✓[/bold green] {message}")
    logger.info(message)


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")
    logger.warning(message)


def print_info(message: str):
    """Print info message"""
    console.print(f"{message}")
    logger.info(message)


def print_panel(content: str, title: str = ""):
    """Print content in a panel"""
    console.print(Panel(content, title=title, border_style="cyan"))


def format_pod_status(status: str) -> str:
    """Format pod status with color"""
    status_colors = {
        "Running": "green",
        "Pending": "yellow",
        "Failed": "red",
        "Unknown": "dim",
        "Succeeded": "green",
        "CrashLoopBackOff": "red",
    }
    color = status_colors.get(status, "white")
    return f"[{color}]{status}[/{color}]"


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f}PB"


def truncate_string(s: str, max_length: int = 50) -> str:
    """Truncate string with ellipsis"""
    return s if len(s) <= max_length else s[:max_length-3] + "..."
