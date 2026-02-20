"""TARS CLI - Main entry point"""
import typer
import logging
import sys
from typing import Optional
from rich.console import Console

from .commands import MonitoringCommands
from .config import config, LOG_FILE
from .utils import print_error, print_success, print_info

TARS_BANNER = """[bold cyan]
╔════════════════════════════════════════════════════════════╗
║  ████████╗ █████╗ ██████╗ ███████╗                         ║
║  ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝                         ║
║     ██║   ███████║██████╔╝███████╗                         ║
║     ██║   ██╔══██║██╔══██╗╚════██║                         ║
║     ██║   ██║  ██║██║  ██║███████║                         ║
║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝                         ║
║                                                            ║
║  [bold yellow]Technical Assistance & Reliability System[/bold yellow]             ║
╚════════════════════════════════════════════════════════════╝
[/bold cyan]"""

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
    ]
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="tars",
    help="AI-Powered Kubernetes Monitoring CLI",
    add_completion=False,
    no_args_is_help=True
)
console = Console()


@app.command()
def health(namespace: Optional[str] = None):
    """Check cluster health"""
    try:
        cmd = MonitoringCommands()
        cmd.health_check(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def pods(namespace: Optional[str] = None):
    """List pods"""
    try:
        cmd = MonitoringCommands()
        cmd.list_pods(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def diagnose(
    pod_name: str = typer.Argument(..., help="Pod name to diagnose"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Diagnose pod issues with AI"""
    try:
        cmd = MonitoringCommands()
        cmd.diagnose_pod(pod_name, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def setup():
    """Setup and validate TARS configuration"""
    console.print("[bold]TARS CLI Setup[/bold]\n")
    
    # Check Gemini API key
    if config.gemini_api_key:
        print_success("GEMINI_API_KEY configured")
    else:
        print_error("GEMINI_API_KEY not set")
        console.print("  Get API key: https://makersuite.google.com")
        console.print("  Set with: export GEMINI_API_KEY='your-key'\n")
    
    # Check Kubernetes
    try:
        cmd = MonitoringCommands()
        print_success("Kubernetes connection established")
    except Exception as e:
        print_error(f"Kubernetes connection failed: {e}")
    
    # Check Prometheus
    if config.prometheus_url:
        print_success(f"Prometheus configured: {config.prometheus_url}")
    else:
        print_info("Prometheus not configured (optional)")
        console.print("  Set with: export PROMETHEUS_URL='http://prometheus:9090'\n")
    
    console.print("\n[green]Setup validation complete[/green]")
    console.print("Run: tars health")


@app.command()
def version():
    """Show version"""
    from . import __version__
    console.print(f"TARS CLI v{__version__}")


def main():
    """Main entry point"""
    try:
        # Show banner when showing help (no command or --help)
        if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']):
            console.print(TARS_BANNER)
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print_error(f"Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
