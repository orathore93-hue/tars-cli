"""SSTARS CLI - Main entry point"""
import typer
import logging
import sys
from typing import Optional
from rich.console import Console

from .commands import MonitoringCommands
from .config import config, LOG_FILE
from .utils import print_error, print_success, print_info

STARS_BANNER = """[bold cyan]
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║  ███████╗.████████╗.  █████╗ .  ██████╗ .  ███████╗        ║
    ║  ██╔════╝.╚══██╔══╝. ██╔══██╗.  ██╔══██╗.  ██╔════╝        ║
    ║  ███████╗.   ██║   . ███████║.  ██████╔╝.  ███████╗        ║
    ║  ╚════██║.   ██║   . ██╔══██║.  ██╔══██╗.  ╚════██║        ║
    ║  ███████║.   ██║   . ██║  ██║.  ██║  ██║.  ███████║        ║
    ║  ╚══════╝.   ╚═╝   . ╚═╝  ╚═╝.  ╚═╝  ╚═╝.  ╚══════╝        ║
    ║                                                            ║
    ║    [/bold cyan][bold yellow]Site Technical Assistance & Reliability System[/bold yellow][bold cyan]          ║
    ║                                                            ║
    ║         [/bold cyan][dim]"Humor setting: 90%. Let's do this."[/dim][bold cyan]               ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
[/bold cyan]"""

STARS_ROBOT = """[bold cyan]
        ╔═══════════════════════════════════╗
        ║   ┌─────────────────────────┐     ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │     ║
        ║   │  ▓ [/bold cyan][bold yellow]◉[/bold yellow][bold cyan] S.T.A.R.S [/bold cyan][bold yellow]◉[/bold yellow][bold cyan] ▓      │     ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │     ║
        ║   │  ▓  [/bold cyan][bold green]═══════════[/bold green][bold cyan]  ▓      │     ║
        ║   │  ▓  [/bold cyan][bold green]═══════════[/bold green][bold cyan]  ▓      │     ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │     ║
        ║   └─────────────────────────┘     ║
        ║         ║           ║             ║
        ║      ┌──┴──┐     ┌──┴──┐          ║
        ║      │ ▓▓▓ │     │ ▓▓▓ │          ║
        ║      └─────┘     └─────┘          ║
        ╚═══════════════════════════════════╝
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
    no_args_is_help=False
)
console = Console()


@app.command()
def health(
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Filter by namespace"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Disable AI analysis (no data sent externally)")
):
    """Check cluster health"""
    try:
        cmd = MonitoringCommands()
        cmd.health_check(namespace, allow_ai=not no_ai)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def pods(namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Filter by namespace (default: all)")):
    """List pods with status and resource usage"""
    try:
        cmd = MonitoringCommands()
        cmd.list_pods(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def diagnose(
    pod_name: str = typer.Argument(..., help="Name of the pod to diagnose"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Disable AI analysis (no data sent externally)")
):
    """Diagnose pod issues and get AI-powered recommendations"""
    try:
        cmd = MonitoringCommands()
        cmd.diagnose_pod(pod_name, namespace, allow_ai=not no_ai)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def init():
    """Initialize STARS CLI - Show welcome screen and setup"""
    welcome()
    console.print("\n")
    setup()


@app.command()
def setup():
    """Setup and validate STARS configuration"""
    import getpass
    import keyring
    from pathlib import Path
    import os
    
    console.print("[bold]STARS CLI Setup[/bold]\n")
    
    # Check if API key already exists
    try:
        existing_key = keyring.get_password("stars-cli", "gemini_api_key")
        if not existing_key:
            # Check local credentials file
            creds_file = Path.home() / ".stars" / "credentials"
            if creds_file.exists():
                with open(creds_file, 'r') as f:
                    existing_key = f.read().strip()
    except Exception:
        existing_key = None
    
    if existing_key:
        print_success("Gemini API key already configured")
        console.print("  Run 'stars delete-api-key' to remove and reconfigure\n")
    else:
        console.print("[yellow]Gemini API key not found[/yellow]")
        console.print("  Get your API key: https://makersuite.google.com\n")
        
        if typer.confirm("Would you like to configure it now?"):
            api_key = getpass.getpass("Enter your Gemini API key (input hidden): ")
            
            if not api_key or not api_key.strip():
                print_error("No API key provided")
            else:
                # Try to save to keyring
                try:
                    keyring.set_password("stars-cli", "gemini_api_key", api_key.strip())
                    print_success("API key saved to OS keychain")
                except Exception as e:
                    # Fallback to local file
                    console.print(f"[yellow]⚠️  Keyring unavailable: {e}[/yellow]")
                    console.print("[yellow]Falling back to plaintext file (chmod 600)[/yellow]\n")
                    
                    creds_file = Path.home() / ".stars" / "credentials"
                    creds_file.parent.mkdir(exist_ok=True, mode=0o700)
                    
                    with open(creds_file, 'w') as f:
                        f.write(api_key.strip())
                    
                    os.chmod(creds_file, 0o600)
                    print_success(f"API key saved to {creds_file} (chmod 600)")
                    console.print("[yellow]⚠️  Warning: Using plaintext file storage (no OS keychain detected)[/yellow]")
                    console.print("[yellow]    For production, use environment variable: export GEMINI_API_KEY='your-key'[/yellow]\n")
    
    # Check Kubernetes
    try:
        cmd = MonitoringCommands()
        print_success("Kubernetes connection established")
    except Exception as e:
        print_error(f"Kubernetes connection failed: {e}")
    
    # Check Prometheus
    if config.settings.prometheus_url:
        print_success(f"Prometheus configured: {config.settings.prometheus_url}")
    else:
        print_info("Prometheus not configured (optional)")
        console.print("  Set with: export PROMETHEUS_URL='http://prometheus:9090'\n")
    
    console.print("\n[green]✅ Setup complete[/green]")
    console.print("Run: stars health")


@app.command()
def set_api_key():
    """Store Gemini API key securely in OS keychain"""
    import getpass
    import keyring
    from pathlib import Path
    import os
    
    console.print("[bold]Configure Gemini API Key[/bold]\n")
    console.print("Get your API key: https://makersuite.google.com\n")
    
    api_key = getpass.getpass("Enter your Gemini API key (input hidden): ")
    
    if not api_key or not api_key.strip():
        print_error("No API key provided")
        raise typer.Exit(1)
    
    # Try to save to keyring
    try:
        keyring.set_password("stars-cli", "gemini_api_key", api_key.strip())
        print_success("✅ API key saved to OS keychain")
        console.print("[dim]Your key is encrypted and stored securely[/dim]")
    except Exception as e:
        # Fallback to local file
        console.print(f"[yellow]⚠️  Keyring unavailable: {e}[/yellow]")
        console.print("[yellow]Falling back to local encrypted storage[/yellow]\n")
        
        creds_file = Path.home() / ".stars" / "credentials"
        creds_file.parent.mkdir(exist_ok=True, mode=0o700)
        
        with open(creds_file, 'w') as f:
            f.write(api_key.strip())
        
        os.chmod(creds_file, 0o600)
        print_success(f"✅ API key saved to {creds_file} (chmod 600)")
        console.print("[yellow]⚠️  Warning: Using local file storage (no OS keychain detected)[/yellow]")
        console.print("[yellow]    For production, use environment variable: export GEMINI_API_KEY='your-key'[/yellow]")


@app.command()
def delete_api_key():
    """Delete Gemini API key from secure storage"""
    import keyring
    from pathlib import Path
    
    console.print("[bold]Delete Gemini API Key[/bold]\n")
    
    deleted = False
    
    # Try to delete from keyring
    try:
        keyring.delete_password("stars-cli", "gemini_api_key")
        print_success("API key deleted from OS keychain")
        deleted = True
    except Exception:
        pass
    
    # Try to delete from local file
    creds_file = Path.home() / ".stars" / "credentials"
    if creds_file.exists():
        creds_file.unlink()
        print_success(f"API key deleted from {creds_file}")
        deleted = True
    
    if not deleted:
        print_info("No API key found in keychain or local storage")
    else:
        console.print("\n[green]✅ API key removed[/green]")
        console.print("Run 'stars set-api-key' to configure a new key")


@app.command()
def version():
    """Show version"""
    from . import __version__
    console.print(f"SSTARS CLI v{__version__}")


@app.command()
def logs(
    pod_name: str = typer.Argument(..., help="Name of the pod"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    tail: int = typer.Option(50, "--tail", "-t", help="Number of lines to show")
):
    """Get pod logs"""
    try:
        cmd = MonitoringCommands()
        cmd.get_pod_logs(pod_name, namespace, tail)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def events(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of events to show")
):
    """Show recent cluster events"""
    try:
        cmd = MonitoringCommands()
        cmd.list_events(namespace, limit)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def nodes():
    """List cluster nodes with status"""
    try:
        cmd = MonitoringCommands()
        cmd.list_nodes()
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def deployments(namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")):
    """List deployments"""
    try:
        cmd = MonitoringCommands()
        cmd.list_deployments(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def services(namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")):
    """List services"""
    try:
        cmd = MonitoringCommands()
        cmd.list_services(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def namespaces():
    """List all namespaces"""
    try:
        cmd = MonitoringCommands()
        cmd.list_namespaces()
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def configmaps(namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")):
    """List configmaps"""
    try:
        cmd = MonitoringCommands()
        cmd.list_configmaps(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def secrets(namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")):
    """List secrets"""
    try:
        cmd = MonitoringCommands()
        cmd.list_secrets(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def ingress(namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")):
    """List ingress resources"""
    try:
        cmd = MonitoringCommands()
        cmd.list_ingress(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def volumes(namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")):
    """List persistent volumes and claims"""
    try:
        cmd = MonitoringCommands()
        cmd.list_volumes(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def describe(
    resource_type: str = typer.Argument(..., help="Resource type (pod, deployment, service, etc)"),
    resource_name: str = typer.Argument(..., help="Resource name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")
):
    """Describe a Kubernetes resource"""
    try:
        cmd = MonitoringCommands()
        cmd.describe_resource(resource_type, resource_name, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def top(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of pods to show")
):
    """Show top resource-consuming pods"""
    try:
        cmd = MonitoringCommands()
        cmd.top_pods(namespace, limit)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def restart(
    resource_type: str = typer.Argument(..., help="Resource type (deployment, statefulset)"),
    resource_name: str = typer.Argument(..., help="Resource name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")
):
    """Restart a deployment or statefulset"""
    try:
        cmd = MonitoringCommands()
        cmd.restart_resource(resource_type, resource_name, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def scale(
    resource_type: str = typer.Argument(..., help="Resource type (deployment, statefulset)"),
    resource_name: str = typer.Argument(..., help="Resource name"),
    replicas: int = typer.Argument(..., help="Number of replicas"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")
):
    """Scale a deployment or statefulset"""
    try:
        cmd = MonitoringCommands()
        cmd.scale_resource(resource_type, resource_name, replicas, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def exec(
    pod_name: str = typer.Argument(..., help="Pod name"),
    command: str = typer.Argument(..., help="Command to execute"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    container: str = typer.Option(None, "--container", "-c", help="Container name")
):
    """Execute command in a pod"""
    from .sre_tools import validate_resource_name, validate_namespace
    from rich.prompt import Confirm
    
    # Validate inputs
    if not validate_resource_name(pod_name):
        print_error(f"Invalid pod name: {pod_name}")
        raise typer.Exit(1)
    
    if not validate_namespace(namespace):
        print_error(f"Invalid namespace: {namespace}")
        raise typer.Exit(1)
    
    # Confirm dangerous operation
    console.print(f"[yellow]⚠️  About to execute command in pod:[/yellow]")
    console.print(f"  Pod: {pod_name}")
    console.print(f"  Namespace: {namespace}")
    console.print(f"  Command: {command}")
    
    if not Confirm.ask("Continue?", default=False):
        print_info("Cancelled")
        raise typer.Exit(0)
    
    try:
        cmd = MonitoringCommands()
        cmd.exec_pod(pod_name, command, namespace, container)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def port_forward(
    pod_name: str = typer.Argument(..., help="Pod name"),
    port: str = typer.Argument(..., help="Port mapping (local:remote)"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")
):
    """Forward local port to pod"""
    import re
    from .sre_tools import validate_resource_name, validate_namespace
    
    # Validate port format
    if not re.match(r'^\d{1,5}:\d{1,5}$', port):
        print_error(f"Invalid port format: {port}. Expected format: local:remote (e.g., 8080:80)")
        raise typer.Exit(1)
    
    # Validate inputs
    if not validate_resource_name(pod_name):
        print_error(f"Invalid pod name: {pod_name}")
        raise typer.Exit(1)
    
    if not validate_namespace(namespace):
        print_error(f"Invalid namespace: {namespace}")
        raise typer.Exit(1)
    
    try:
        cmd = MonitoringCommands()
        cmd.port_forward(pod_name, port, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def context():
    """Show current Kubernetes context"""
    try:
        cmd = MonitoringCommands()
        cmd.show_context()
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def resources(namespace: str = typer.Argument(..., help="Namespace to analyze")):
    """Show resource usage and quotas for namespace"""
    try:
        cmd = MonitoringCommands()
        cmd.show_resources(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def watch(
    namespace: str = typer.Option(None, "--namespace", "-n", help="Namespace to watch"),
    interval: int = typer.Option(5, "--interval", "-i", help="Refresh interval in seconds")
):
    """Real-time pod monitoring dashboard"""
    try:
        cmd = MonitoringCommands()
        cmd.watch_pods(namespace, interval)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def analyze(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace to analyze")):
    """Analyze cluster with AI insights"""
    try:
        cmd = MonitoringCommands()
        cmd.analyze_cluster(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def errors(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of errors to show")
):
    """Show pods with errors and failures"""
    try:
        cmd = MonitoringCommands()
        cmd.show_errors(namespace, limit)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def crashloop(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Find pods in CrashLoopBackOff"""
    try:
        cmd = MonitoringCommands()
        cmd.find_crashloop(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def pending(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Find pending pods"""
    try:
        cmd = MonitoringCommands()
        cmd.find_pending(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def oom(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Find OOMKilled pods"""
    try:
        cmd = MonitoringCommands()
        cmd.find_oom(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def cordon(node_name: str = typer.Argument(..., help="Node name")):
    """Cordon a node (mark unschedulable)"""
    try:
        cmd = MonitoringCommands()
        cmd.cordon_node(node_name)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def uncordon(node_name: str = typer.Argument(..., help="Node name")):
    """Uncordon a node (mark schedulable)"""
    try:
        cmd = MonitoringCommands()
        cmd.uncordon_node(node_name)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def drain(
    node_name: str = typer.Argument(..., help="Node name"),
    force: bool = typer.Option(False, "--force", help="Force drain")
):
    """Drain a node"""
    try:
        cmd = MonitoringCommands()
        cmd.drain_node(node_name, force)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def quota(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Show resource quotas"""
    try:
        cmd = MonitoringCommands()
        cmd.show_quota(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def crds():
    """List Custom Resource Definitions"""
    try:
        cmd = MonitoringCommands()
        cmd.list_crds()
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def network(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Show network policies and connectivity"""
    try:
        cmd = MonitoringCommands()
        cmd.show_network(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def cost(namespace: str = typer.Option(None, "--namespace", "-n", help="Namespace")):
    """Estimate resource costs"""
    try:
        cmd = MonitoringCommands()
        cmd.estimate_cost(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def audit(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    hours: int = typer.Option(24, "--hours", help="Hours to look back")
):
    """Show audit logs"""
    try:
        cmd = MonitoringCommands()
        cmd.show_audit(namespace, hours)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def security_scan(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Scan for security issues"""
    try:
        cmd = MonitoringCommands()
        cmd.security_scan(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def compliance(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Check compliance with best practices"""
    try:
        cmd = MonitoringCommands()
        cmd.check_compliance(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def export(
    output_file: str = typer.Argument(..., help="Output file path"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml, json)")
):
    """Export cluster resources"""
    try:
        cmd = MonitoringCommands()
        cmd.export_resources(output_file, namespace, format)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def diff(
    resource_type: str = typer.Argument(..., help="Resource type"),
    resource_name: str = typer.Argument(..., help="Resource name"),
    file_path: str = typer.Argument(..., help="File to compare"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Show diff between live and file"""
    try:
        cmd = MonitoringCommands()
        cmd.show_diff(resource_type, resource_name, file_path, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def apply(
    file_path: str = typer.Argument(..., help="YAML file to apply"),
    namespace: str = typer.Option(None, "--namespace", "-n", help="Override namespace"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without applying")
):
    """Apply YAML file to cluster"""
    try:
        cmd = MonitoringCommands()
        cmd.apply_yaml_file(file_path, namespace, dry_run)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def create(
    file_path: str = typer.Argument(..., help="YAML file to create from"),
    namespace: str = typer.Option(None, "--namespace", "-n", help="Override namespace")
):
    """Create resources from YAML file"""
    try:
        cmd = MonitoringCommands()
        cmd.apply_yaml_file(file_path, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def delete(
    resource: str = typer.Argument(None, help="Resource to delete (e.g., pod/name)"),
    file: str = typer.Option(None, "--file", "-f", help="Delete from YAML file"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Delete resources"""
    try:
        cmd = MonitoringCommands()
        if file:
            cmd.delete_from_yaml_file(file, namespace)
        elif resource:
            print_error("Direct resource deletion not yet implemented. Use --file/-f")
            raise typer.Exit(1)
        else:
            print_error("Specify resource or use --file/-f")
            raise typer.Exit(1)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def history(
    resource_type: str = typer.Argument(..., help="Resource type"),
    resource_name: str = typer.Argument(..., help="Resource name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Show rollout history"""
    try:
        cmd = MonitoringCommands()
        cmd.show_history(resource_type, resource_name, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def triage(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """AI-powered issue triage"""
    try:
        cmd = MonitoringCommands()
        cmd.triage_issues(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def metrics(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    resource: str = typer.Option("pods", "--resource", "-r", help="Resource type")
):
    """Show resource metrics"""
    try:
        cmd = MonitoringCommands()
        cmd.show_metrics(namespace, resource)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def check():
    """Quick cluster health check"""
    try:
        cmd = MonitoringCommands()
        cmd.quick_check()
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def humor(level: int = typer.Argument(90, help="Humor level (0-100)")):
    """Set STARS humor level"""
    console.print(f"[bold cyan]Humor level set to {level}%[/bold cyan]")
    console.print(f"[italic]{'Sarcasm mode engaged' if level > 75 else 'Professional mode'}[/italic]")


@app.command()
def quote():
    """Get a random STARS quote"""
    import random
    quotes = [
        "Humor setting at 90%. Let's do this.",
        "I'm ready to monitor your cluster.",
        "STARS online. Let's see what's broken today.",
        "Cluster monitoring active. Try not to break anything.",
        "Ready to analyze your Kubernetes cluster.",
    ]
    console.print(f"[bold cyan]TARS:[/bold cyan] [italic]{random.choice(quotes)}[/italic]")


@app.command()
def aggregate_logs(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    pattern: str = typer.Option(None, "--pattern", "-p", help="Search pattern")
):
    """Aggregate logs from multiple pods"""
    try:
        cmd = MonitoringCommands()
        cmd.aggregate_logs(namespace, pattern)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def alert(
    name: str = typer.Argument(..., help="Alert name"),
    condition: str = typer.Argument(..., help="Alert condition"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Create an alert rule"""
    try:
        cmd = MonitoringCommands()
        cmd.create_alert(name, condition, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def alert_history(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Show alert history"""
    try:
        cmd = MonitoringCommands()
        cmd.show_alert_history(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def alert_webhook(url: str = typer.Argument(..., help="Webhook URL")):
    """Configure alert webhook"""
    try:
        cmd = MonitoringCommands()
        cmd.configure_webhook(url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def autofix(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Auto-fix common issues"""
    try:
        cmd = MonitoringCommands()
        cmd.autofix_issues(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def benchmark(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Run performance benchmarks"""
    try:
        cmd = MonitoringCommands()
        cmd.run_benchmark(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def privacy(
    action: str = typer.Argument(..., help="Action: status, revoke, or grant")
):
    """Manage AI data sharing consent"""
    from .config import check_ai_consent, grant_ai_consent, revoke_ai_consent
    
    try:
        if action == "status":
            if check_ai_consent():
                print_success("AI consent: GRANTED")
                print_info("Cluster data may be sent to Google Gemini API for analysis")
                print_info("Use 'tars privacy revoke' to disable")
            else:
                print_info("AI consent: NOT GRANTED")
                print_info("AI features will prompt for consent on first use")
                print_info("Use 'tars privacy grant' to enable without prompts")
        
        elif action == "revoke":
            revoke_ai_consent()
            print_success("AI consent revoked")
            print_info("No data will be sent to external AI services")
            print_info("Use --no-ai flag or 'tars privacy grant' to re-enable")
        
        elif action == "grant":
            grant_ai_consent()
            print_success("AI consent granted")
            print_info("AI features enabled for all commands")
            print_info("See docs/PRIVACY.md for details on data handling")
        
        else:
            print_error(f"Unknown action: {action}")
            print_info("Valid actions: status, revoke, grant")
            raise typer.Exit(1)
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def blast(
    target: str = typer.Argument(..., help="Target service"),
    requests: int = typer.Option(100, "--requests", "-r", help="Number of requests"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Load test a service"""
    try:
        cmd = MonitoringCommands()
        cmd.load_test(target, requests, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def bottleneck(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Find performance bottlenecks"""
    try:
        cmd = MonitoringCommands()
        cmd.find_bottlenecks(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def chaos(
    action: str = typer.Argument(..., help="Chaos action (kill-pod, network-delay)"),
    target: str = typer.Argument(..., help="Target resource"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Chaos engineering experiments"""
    try:
        cmd = MonitoringCommands()
        cmd.chaos_experiment(action, target, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def compare(
    resource1: str = typer.Argument(..., help="First resource"),
    resource2: str = typer.Argument(..., help="Second resource"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Compare two resources"""
    try:
        cmd = MonitoringCommands()
        cmd.compare_resources(resource1, resource2, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def creator():
    """Show STARS creator info"""
    console.print("\n[bold cyan]SSTARS CLI[/bold cyan]")
    console.print("[bold]Site Technical Assistance &  Reliability System[/bold]")
    console.print("\n[bold yellow]Created by:[/bold yellow]")
    console.print("  [cyan]Omer Rathore[/cyan]")
    console.print("  [dim]orathore93@gmail.com[/dim]")
    console.print("\n[dim]Built for Kubernetes SREs and DevOps Engineers[/dim]\n")


@app.command()
def welcome():
    """Show STARS welcome screen"""
    import random
    from rich.panel import Panel
    
    quotes = [
        "Humor setting at 90%. Let's do this.",
        "I'm ready to monitor your cluster.",
        "STARS online. Let's see what's broken today.",
        "Ready to analyze your Kubernetes cluster.",
        "Cluster monitoring active. Try not to break anything.",
    ]
    
    console.clear()
    console.print(STARS_BANNER)
    console.print(STARS_ROBOT)
    console.print(f"\n[bold green]STARS:[/bold green] [italic]{random.choice(quotes)}[/italic]")
    console.print("[dim italic]Your companion while you Kubersnaut.[/dim italic]\n")
    
    info_panel = """[bold yellow]What I Do:[/bold yellow]
• Monitor Kubernetes clusters (GKE/EKS) in real-time
• Detect issues: CrashLoops, OOM kills, pending pods, resource spikes
• AI-powered analysis with Gemini for troubleshooting
• On-call engineer toolkit for incident response
• Prevent downtime with proactive monitoring

[bold yellow]Quick Start:[/bold yellow]
  [cyan]stars init[/cyan]      - Initialize and setup STARS
  [cyan]stars health[/cyan]    - Check cluster health
  [cyan]stars triage[/cyan]    - Quick incident overview
  [cyan]stars watch[/cyan]     - Real-time pod monitoring
  [cyan]stars spike[/cyan]     - Monitor resource spikes

[bold yellow]🔒 Security & Privacy:[/bold yellow]
  • All operations require RBAC permissions
  • Destructive actions need explicit confirmation
  • AI features require user consent (use --no-ai to opt-out)
  • Secrets automatically redacted before external calls
  • Complete audit trail in ~/.stars/audit.log
  • Privacy policy: [cyan]docs/PRIVACY.md[/cyan]
"""
    
    console.print(Panel(info_panel, border_style="cyan", padding=(0, 2)))
    console.print("\n[dim]Created by Omer Rathore | Type 'stars --help' for all commands[/dim]\n")


@app.command()
def dashboard(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Launch interactive dashboard"""
    try:
        cmd = MonitoringCommands()
        cmd.launch_dashboard(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def forecast(
    resource: str = typer.Argument(..., help="Resource to forecast"),
    days: int = typer.Option(7, "--days", "-d", help="Days to forecast"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Forecast resource usage"""
    try:
        cmd = MonitoringCommands()
        cmd.forecast_usage(resource, days, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def god():
    """God mode - show everything"""
    try:
        cmd = MonitoringCommands()
        cmd.god_mode()
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def heatmap(
    metric: str = typer.Argument(..., help="Metric to visualize"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Generate resource heatmap"""
    try:
        cmd = MonitoringCommands()
        cmd.generate_heatmap(metric, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def incident_report(
    incident_id: str = typer.Argument(..., help="Incident ID"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Generate incident report"""
    try:
        cmd = MonitoringCommands()
        cmd.generate_incident_report(incident_id, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def multi_cluster(action: str = typer.Argument(..., help="Action (list, switch, compare)")):
    """Multi-cluster operations"""
    try:
        cmd = MonitoringCommands()
        cmd.multi_cluster_ops(action)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def oncall():
    """Show on-call information"""
    try:
        cmd = MonitoringCommands()
        cmd.show_oncall()
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def profile(
    pod_name: str = typer.Argument(..., help="Pod name"),
    duration: int = typer.Option(30, "--duration", "-d", help="Profile duration in seconds"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Profile pod performance"""
    try:
        cmd = MonitoringCommands()
        cmd.profile_pod(pod_name, duration, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_check(url: str = typer.Option(None, "--url", help="Prometheus URL")):
    """Check Prometheus connection"""
    try:
        cmd = MonitoringCommands()
        cmd.check_prometheus(url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_metrics(url: str = typer.Option(None, "--url", help="Prometheus URL")):
    """List Prometheus metrics"""
    try:
        cmd = MonitoringCommands()
        cmd.list_prom_metrics(url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_query(
    query: str = typer.Argument(..., help="PromQL query"),
    url: str = typer.Option(None, "--url", help="Prometheus URL")
):
    """Execute Prometheus query"""
    try:
        cmd = MonitoringCommands()
        cmd.execute_prom_query(query, url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_alerts(url: str = typer.Option(None, "--url", help="Prometheus URL")):
    """Show Prometheus alerts"""
    try:
        cmd = MonitoringCommands()
        cmd.show_prom_alerts(url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_dashboard(url: str = typer.Option(None, "--url", help="Prometheus URL")):
    """Open Prometheus dashboard"""
    try:
        cmd = MonitoringCommands()
        cmd.open_prom_dashboard(url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_export(
    output: str = typer.Argument(..., help="Output file"),
    url: str = typer.Option(None, "--url", help="Prometheus URL")
):
    """Export Prometheus data"""
    try:
        cmd = MonitoringCommands()
        cmd.export_prom_data(output, url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_compare(
    metric1: str = typer.Argument(..., help="First metric"),
    metric2: str = typer.Argument(..., help="Second metric"),
    url: str = typer.Option(None, "--url", help="Prometheus URL")
):
    """Compare Prometheus metrics"""
    try:
        cmd = MonitoringCommands()
        cmd.compare_prom_metrics(metric1, metric2, url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def prom_record(
    name: str = typer.Argument(..., help="Recording rule name"),
    query: str = typer.Argument(..., help="PromQL query"),
    url: str = typer.Option(None, "--url", help="Prometheus URL")
):
    """Create Prometheus recording rule"""
    try:
        cmd = MonitoringCommands()
        cmd.create_prom_recording(name, query, url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def pulse(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Show cluster pulse (quick overview)"""
    try:
        cmd = MonitoringCommands()
        cmd.show_pulse(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def replay(
    incident_id: str = typer.Argument(..., help="Incident ID to replay"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Replay past incident"""
    try:
        cmd = MonitoringCommands()
        cmd.replay_incident(incident_id, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def runbook(
    issue: str = typer.Argument(..., help="Issue type"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Show runbook for issue"""
    try:
        cmd = MonitoringCommands()
        cmd.show_runbook(issue, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def sli(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Show Service Level Indicators"""
    try:
        cmd = MonitoringCommands()
        cmd.show_sli(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def slo(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Show Service Level Objectives"""
    try:
        cmd = MonitoringCommands()
        cmd.show_slo(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def smart_scale(
    resource: str = typer.Argument(..., help="Resource to scale"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """AI-powered smart scaling"""
    try:
        cmd = MonitoringCommands()
        cmd.smart_scale(resource, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def snapshot(
    name: str = typer.Argument(..., help="Snapshot name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Create cluster snapshot"""
    try:
        cmd = MonitoringCommands()
        cmd.create_snapshot(name, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def spike(
    metric: str = typer.Argument(..., help="Metric to monitor"),
    threshold: float = typer.Option(80.0, "--threshold", "-t", help="Spike threshold"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Monitor for metric spikes"""
    try:
        cmd = MonitoringCommands()
        cmd.monitor_spikes(metric, threshold, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def story(namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")):
    """Generate cluster story (timeline)"""
    try:
        cmd = MonitoringCommands()
        cmd.generate_story(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def timeline(
    resource: str = typer.Argument(..., help="Resource name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Show resource timeline"""
    try:
        cmd = MonitoringCommands()
        cmd.show_timeline(resource, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def trace(
    service: str = typer.Argument(..., help="Service name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Trace service requests"""
    try:
        cmd = MonitoringCommands()
        cmd.trace_service(service, namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def cardinality(url: str = typer.Option(None, "--url", help="Prometheus URL")):
    """Show metric cardinality"""
    try:
        cmd = MonitoringCommands()
        cmd.show_cardinality(url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def cardinality_labels(
    metric: str = typer.Argument(..., help="Metric name"),
    url: str = typer.Option(None, "--url", help="Prometheus URL")
):
    """Show label cardinality for metric"""
    try:
        cmd = MonitoringCommands()
        cmd.show_label_cardinality(metric, url)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


def main():
    """Main entry point"""
    try:
        # Show welcome screen when no arguments (just 'stars')
        if len(sys.argv) == 1:
            welcome()
            return
        
        # Show banner with help
        if len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']:
            console.print(STARS_BANNER)
        
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        raise typer.Exit(0)
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print_error(f"Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()


# ============================================================================
# SRE-FOCUSED COMMANDS
# ============================================================================

@app.command()
def incident(
    action: str = typer.Argument(..., help="Action: start, log, close, list"),
    message: str = typer.Argument(None, help="Message for log action"),
    title: str = typer.Option(None, "--title", "-t", help="Incident title (for start)"),
    severity: str = typer.Option("medium", "--severity", "-s", help="Severity: low, medium, high, critical"),
    resource: str = typer.Option(None, "--resource", "-r", help="Affected resource")
):
    """Incident management for on-call engineers"""
    from .incident import IncidentManager
    
    try:
        manager = IncidentManager()
        
        if action == "start":
            if not title:
                print_error("Title required for starting incident. Use --title")
                raise typer.Exit(1)
            manager.start_incident(title, severity)
        
        elif action == "log":
            if not message:
                print_error("Message required for logging. Usage: stars incident log 'your message'")
                raise typer.Exit(1)
            manager.log_action(message, resource)
        
        elif action == "close":
            if not message:
                print_error("Resolution message required. Usage: stars incident close 'resolution'")
                raise typer.Exit(1)
            manager.close_incident(message)
        
        elif action == "list":
            manager.list_incidents()
        
        else:
            print_error(f"Unknown action: {action}. Use: start, log, close, list")
            raise typer.Exit(1)
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def blast_radius(
    deployment: str = typer.Argument(..., help="Deployment name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Analyze blast radius of deployment changes"""
    from .sre_tools import BlastRadiusAnalyzer
    from .k8s_client import K8sClient
    
    try:
        k8s = K8sClient()
        analyzer = BlastRadiusAnalyzer(k8s)
        
        blast_radius = analyzer.analyze_deployment(deployment, namespace)
        analyzer.display_blast_radius(blast_radius)
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def fix_crashloop(
    pod: str = typer.Argument(..., help="Pod name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Dry run mode")
):
    """Analyze and suggest fixes for crashloop backoff"""
    from .sre_tools import QuickFixer
    from .k8s_client import K8sClient
    
    try:
        k8s = K8sClient()
        fixer = QuickFixer(k8s)
        
        console.print(f"\n[bold]Analyzing crashloop for pod: {pod}[/bold]\n")
        fixes = fixer.fix_crashloop(pod, namespace, dry_run)
        
        if fixes:
            console.print("[bold yellow]Suggested Fixes:[/bold yellow]")
            for i, fix in enumerate(fixes, 1):
                console.print(f"  {i}. {fix}")
            console.print()
        else:
            console.print("[green]No issues detected[/green]")
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def clear_evicted(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Dry run mode"),
    all_namespaces: bool = typer.Option(False, "--all-namespaces", "-A", help="All namespaces")
):
    """Remove all evicted pods"""
    from .sre_tools import QuickFixer
    from .k8s_client import K8sClient
    from rich.prompt import Confirm
    
    try:
        k8s = K8sClient()
        fixer = QuickFixer(k8s)
        
        if all_namespaces:
            console.print("[yellow]Scanning all namespaces...[/yellow]")
            # TODO: Implement all namespaces
            console.print("[red]All namespaces not yet implemented[/red]")
            return
        
        count = fixer.clear_evicted_pods(namespace, dry_run)
        
        if dry_run and count > 0:
            console.print(f"\n[yellow]Run with --apply to actually delete {count} pods[/yellow]")
            console.print("[dim]Example: stars clear-evicted --apply[/dim]\n")
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def rollback(
    deployment: str = typer.Argument(..., help="Deployment name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    revision: int = typer.Option(0, "--revision", "-r", help="Revision number (0 = previous)"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Dry run mode")
):
    """Rollback deployment to previous version"""
    from .k8s_client import K8sClient
    from .sre_tools import BlastRadiusAnalyzer, validate_resource_name, validate_namespace
    from rich.prompt import Confirm
    
    if not validate_resource_name(deployment) or not validate_namespace(namespace):
        print_error("Invalid deployment name or namespace")
        raise typer.Exit(1)
    
    try:
        k8s = K8sClient()
        
        # Show blast radius first
        console.print("\n[bold yellow]⚠️  Analyzing blast radius...[/bold yellow]")
        analyzer = BlastRadiusAnalyzer(k8s)
        blast_radius = analyzer.analyze_deployment(deployment, namespace)
        analyzer.display_blast_radius(blast_radius)
        
        if dry_run:
            console.print(f"\n[yellow]DRY RUN: Would rollback {deployment} to revision {revision or 'previous'}[/yellow]")
            console.print("[dim]Run with --apply to execute rollback[/dim]\n")
            return
        
        # Confirm
        if not Confirm.ask(f"\n[bold red]Rollback {deployment}?[/bold red]", default=False):
            console.print("[yellow]Cancelled[/yellow]")
            return
        
        # Execute rollback
        console.print(f"\n[bold]Rolling back {deployment}...[/bold]")
        
        # Use kubectl rollback
        import subprocess
        cmd = ['kubectl', 'rollout', 'undo', f'deployment/{deployment}', '-n', namespace]
        if revision > 0:
            cmd.extend(['--to-revision', str(revision)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[green]✓ Rollback initiated[/green]")
            console.print(f"\n[dim]Monitor with: stars watch -n {namespace}[/dim]\n")
        else:
            console.print(f"[red]✗ Rollback failed: {result.stderr}[/red]")
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def oncall_report(
    hours: int = typer.Option(8, "--hours", "-h", help="Hours to report on"),
    namespace: str = typer.Option(None, "--namespace", "-n", help="Filter by namespace")
):
    """Generate on-call shift report"""
    from .incident import IncidentManager
    from datetime import datetime, timedelta
    
    try:
        console.print(f"\n[bold]On-Call Shift Report[/bold]")
        console.print(f"[dim]Last {hours} hours[/dim]\n")
        
        # Get incidents
        manager = IncidentManager()
        manager.list_incidents(limit=20)
        
        # TODO: Add more metrics
        # - Pod restarts
        # - Failed deployments
        # - Resource alerts
        # - Error rate spikes
        
        console.print("\n[dim]Full report generation coming soon...[/dim]\n")
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def security_scan(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace"),
    quick: bool = typer.Option(False, "--quick", "-q", help="Quick scan only")
):
    """Quick security audit of cluster resources"""
    from .k8s_client import K8sClient
    from rich.panel import Panel
    
    try:
        k8s = K8sClient()
        console.print("\n[bold]Security Scan[/bold]\n")
        
        issues = []
        
        # Check for privileged containers
        console.print("[cyan]Checking for privileged containers...[/cyan]")
        pods = k8s.list_pods(namespace)
        for pod in pods:
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if container.security_context and container.security_context.privileged:
                        issues.append(f"Privileged container: {pod.metadata.name}/{container.name}")
        
        # Check for host network
        console.print("[cyan]Checking for host network usage...[/cyan]")
        for pod in pods:
            if pod.spec.host_network:
                issues.append(f"Host network enabled: {pod.metadata.name}")
        
        # Check for missing resource limits
        console.print("[cyan]Checking for missing resource limits...[/cyan]")
        for pod in pods:
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if not container.resources or not container.resources.limits:
                        issues.append(f"No resource limits: {pod.metadata.name}/{container.name}")
        
        # Display results
        if issues:
            console.print(f"\n[bold red]Found {len(issues)} security issues:[/bold red]\n")
            for issue in issues[:10]:
                console.print(f"  • {issue}")
            if len(issues) > 10:
                console.print(f"\n[dim]... and {len(issues) - 10} more issues[/dim]")
        else:
            console.print("\n[bold green]✓ No security issues found[/bold green]")
        
        console.print()
    
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)

