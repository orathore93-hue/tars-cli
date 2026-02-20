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

TARS_ROBOT = """[bold cyan]
        ╔═══════════════════════════════════╗
        ║   ┌─────────────────────────┐     ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │     ║
        ║   │  ▓ [/bold cyan][bold yellow]◉[/bold yellow][bold cyan] T.A.R.S [/bold cyan][bold yellow]◉[/bold yellow][bold cyan] ▓  │           ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │     ║
        ║   │  ▓  [/bold cyan][bold green]═══════════[/bold green][bold cyan]  ▓  │         ║
        ║   │  ▓  [/bold cyan][bold green]═══════════[/bold green][bold cyan]  ▓  │         ║
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
def health(namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Filter by namespace")):
    """Check cluster health"""
    try:
        cmd = MonitoringCommands()
        cmd.health_check(namespace)
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
    if config.settings.gemini_api_key:
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
    if config.settings.prometheus_url:
        print_success(f"Prometheus configured: {config.settings.prometheus_url}")
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
    """Set TARS humor level"""
    console.print(f"[bold cyan]Humor level set to {level}%[/bold cyan]")
    console.print(f"[italic]{'Sarcasm mode engaged' if level > 75 else 'Professional mode'}[/italic]")


@app.command()
def quote():
    """Get a random TARS quote"""
    import random
    quotes = [
        "Humor setting at 90%. Let's do this.",
        "I'm ready to monitor your cluster.",
        "TARS online. Let's see what's broken today.",
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
    """Show TARS creator info"""
    console.print("\n[bold cyan]TARS CLI[/bold cyan]")
    console.print("[bold]Technical Assistance & Reliability System[/bold]")
    console.print("\n[bold yellow]Created by:[/bold yellow]")
    console.print("  [cyan]Omer Rathore[/cyan]")
    console.print("  [dim]orathore93@gmail.com[/dim]")
    console.print("\n[dim]Built for Kubernetes SREs and DevOps Engineers[/dim]\n")


@app.command()
def welcome():
    """Show TARS welcome screen"""
    import random
    from rich.panel import Panel
    
    quotes = [
        "Humor setting at 90%. Let's do this.",
        "I'm ready to monitor your cluster.",
        "TARS online. Let's see what's broken today.",
        "Ready to analyze your Kubernetes cluster.",
        "Cluster monitoring active. Try not to break anything.",
    ]
    
    console.clear()
    console.print(TARS_BANNER)
    console.print(TARS_ROBOT)
    console.print(f"\n[bold green]TARS:[/bold green] [italic]{random.choice(quotes)}[/italic]")
    console.print("[dim italic]Your companion while you Kubersnaut.[/dim italic]\n")
    
    info_panel = """[bold yellow]What I Do:[/bold yellow]
• Monitor Kubernetes clusters (GKE/EKS) in real-time
• Detect issues: CrashLoops, OOM kills, pending pods, resource spikes
• AI-powered analysis with Gemini for troubleshooting
• On-call engineer toolkit for incident response
• Prevent downtime with proactive monitoring

[bold yellow]Quick Start:[/bold yellow]
  [cyan]tars setup[/cyan]      - Verify installation and configuration
  [cyan]tars health[/cyan]     - Check cluster health
  [cyan]tars triage[/cyan]     - Quick incident overview
  [cyan]tars watch[/cyan]      - Real-time pod monitoring
  [cyan]tars spike[/cyan]      - Monitor resource spikes
"""
    
    console.print(Panel(info_panel, border_style="cyan", padding=(0, 2)))
    console.print("\n[dim]Created by Omer Rathore | Type 'tars --help' for all commands[/dim]\n")


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
        # Show welcome screen when no arguments (just 'tars')
        if len(sys.argv) == 1:
            welcome()
            return
        
        # Show banner with help
        if len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']:
            console.print(TARS_BANNER)
        
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
