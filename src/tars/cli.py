"""TARS CLI - Main entry point"""
import typer
import logging
import random
from typing import Optional
from rich.console import Console

from .commands import MonitoringCommands
from .config import config, LOG_FILE
from .utils import print_error, print_success, print_info

TARS_ASCII = """[bold cyan]
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║  ████████╗ .  █████╗ .  ██████╗ .  ███████╗                ║
    ║  ╚══██╔══╝ . ██╔══██╗.  ██╔══██╗.  ██╔════╝                ║
    ║     ██║    . ███████║.  ██████╔╝.  ███████╗                ║
    ║     ██║    . ██╔══██║.  ██╔══██╗.  ╚════██║                ║
    ║     ██║    . ██║  ██║.  ██║  ██║.  ███████║                ║
    ║     ╚═╝    . ╚═╝  ╚═╝.  ╚═╝  ╚═╝.  ╚══════╝                ║
    ║                                                            ║
    ║    [/bold cyan][bold yellow]Technical Assistance & Reliability System[/bold yellow][bold cyan]               ║
    ║                                                            ║
    ║         [/bold cyan][dim]"Humor setting: 90%. Let's do this."[/dim][bold cyan]               ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
[/bold cyan]"""

WELCOME_MESSAGES = [
    "I'm ready to monitor your cluster.",
    "Humor setting at 90%. Cluster monitoring initiated.",
    "TARS online. Let's see what's broken today.",
    "Ready to analyze your Kubernetes cluster.",
    "Cluster monitoring active. Try not to break anything.",
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="tars",
    help="🤖 TARS - AI-Powered Kubernetes Monitoring for SREs",
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
    """Setup TARS CLI"""
    console.print("[bold cyan]🤖 TARS CLI Setup[/bold cyan]\n")
    
    # Check Gemini API key
    if config.gemini_api_key:
        print_success("GEMINI_API_KEY is set")
    else:
        print_error("GEMINI_API_KEY not set")
        console.print("Get your free API key at: https://makersuite.google.com")
        console.print("Then run: export GEMINI_API_KEY='your-key'\n")
    
    # Check Kubernetes
    try:
        cmd = MonitoringCommands()
        print_success("Kubernetes connection successful")
    except Exception as e:
        print_error(f"Kubernetes connection failed: {e}")
    
    # Check Prometheus
    if config.prometheus_url:
        print_success(f"Prometheus URL: {config.prometheus_url}")
    else:
        print_info("Prometheus URL not set (optional)")
        console.print("Set with: export PROMETHEUS_URL='http://prometheus:9090'\n")
    
    console.print("\n[bold green]✓ Setup complete![/bold green]")
    console.print("Try: tars health")


@app.command()
def version():
    """Show version"""
    from . import __version__
    console.print(f"TARS CLI v{__version__}")


def main():
    """Main entry point"""
    try:
        console.print(TARS_ASCII)
        console.print(f"[bold green]TARS:[/bold green] [italic]{random.choice(WELCOME_MESSAGES)}[/italic]\n")
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print_error(f"Unexpected error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
