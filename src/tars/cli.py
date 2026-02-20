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
def health(namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Filter by namespace")):
    """Check cluster health"""
    try:
        cmd = MonitoringCommands()
        cmd.health_check(namespace)
    except Exception as e:
        print_error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def pods(namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Filter by namespace")):
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
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace")
):
    """Diagnose pod issues and get AI-powered recommendations"""
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
def rollback(
    resource_type: str = typer.Argument(..., help="Resource type (deployment, statefulset)"),
    resource_name: str = typer.Argument(..., help="Resource name"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Namespace")
):
    """Rollback a deployment or statefulset"""
    try:
        cmd = MonitoringCommands()
        cmd.rollback_resource(resource_type, resource_name, namespace)
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
