"""Utility functions for formatting and display"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import List, Dict, Any
import logging

console = Console()
logger = logging.getLogger(__name__)


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
