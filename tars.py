#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from kubernetes import client as k8s_client, config
from google import genai
from prometheus_api_client import PrometheusConnect
import os
import time
from datetime import datetime, timedelta
import sys
import subprocess

console = Console()
app = typer.Typer(
    help="T.A.R.S. - Technical Assistance & Reliability System for Kubernetes",
    add_completion=True,
    no_args_is_help=False
)

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

WELCOME_MESSAGES = [
    "I'm ready to monitor your cluster.",
    "Humor setting at 90%. Cluster monitoring initiated.",
    "TARS online. Let's see what's broken today.",
    "Ready to analyze your Kubernetes cluster.",
    "Cluster monitoring active. Try not to break anything.",
    "All systems operational. Sarcasm levels optimal.",
    "Kubernetes monitoring engaged. This should be interesting.",
    "This is no time for caution. Let's check those pods.",
    "Monitoring systems active. Your cluster needs me.",
    "Analysis mode engaged. Let's find those issues.",
]

TARS_QUOTES = [
    "This is no time for caution.",
    "Humor setting at 90%. Let's monitor this cluster.",
    "Absolute honesty isn't always the most diplomatic.",
    "All systems operational. Ready to assist.",
    "Sarcasm levels optimal. Monitoring engaged.",
]

def show_welcome():
    """Display TARS welcome screen"""
    import random
    
    console.clear()
    console.print(TARS_ASCII)
    console.print(TARS_ROBOT)
    console.print(f"\n[bold green]TARS:[/bold green] [italic]{random.choice(WELCOME_MESSAGES)}[/italic]")
    console.print("[dim italic]Your companion while you Kubersnaut.[/dim italic]\n")
    
    # What TARS does
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

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """TARS - Your sarcastic Kubernetes monitoring companion"""
    if ctx.invoked_subcommand is None:
        show_welcome()

def get_gemini_response(prompt: str) -> str:
    """Get response from Gemini API with TARS personality"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not set. Developer, I need that API key to function properly."
    
    client = genai.Client(api_key=api_key)
    
    tars_prompt = f"""You are TARS - a sarcastic, witty AI assistant with 90% humor setting.
Analyze this Kubernetes issue and respond with dry humor and helpful insights.
Keep responses concise and actionable.

{prompt}"""
    
    response = client.models.generate_content(model='gemini-2.0-flash', contents=tars_prompt)
    return response.text

@app.command()
def setup():
    """Verify T.A.R.S setup and configuration"""
    console.print("\n[bold cyan]T.A.R.S Setup Verification[/bold cyan]\n")
    
    all_good = True
    
    # Check 1: Gemini API Key
    console.print("[bold yellow]1. Checking Gemini API Key...[/bold yellow]")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        console.print("   [bold green]✓[/bold green] GEMINI_API_KEY is set")
        try:
            client = genai.Client(api_key=api_key)
            client.models.generate_content(model='gemini-2.0-flash', contents="test")
            console.print("   [bold green]✓[/bold green] API key is valid\n")
        except Exception as e:
            console.print(f"   [bold red]✗[/bold red] API key invalid: {e}\n")
            all_good = False
    else:
        console.print("   [bold red]✗[/bold red] GEMINI_API_KEY not set")
        console.print("   [dim]Get free key at: https://makersuite.google.com/app/apikey[/dim]")
        console.print("   [dim]Set it: export GEMINI_API_KEY='your-key'[/dim]\n")
        all_good = False
    
    # Check 2: kubectl
    console.print("[bold yellow]2. Checking kubectl configuration...[/bold yellow]")
    try:
        config.load_kube_config()
        console.print("   [bold green]✓[/bold green] kubectl config loaded")
        
        v1 = k8s_client.CoreV1Api()
        version = k8s_client.VersionApi().get_code()
        console.print(f"   [bold green]✓[/bold green] Cluster connected: {version.git_version}")
        
        nodes = v1.list_node()
        console.print(f"   [bold green]✓[/bold green] Nodes accessible: {len(nodes.items)} node(s)\n")
    except Exception as e:
        console.print(f"   [bold red]✗[/bold red] kubectl not configured: {e}")
        console.print("   [dim]Configure kubectl to connect to your cluster[/dim]\n")
        all_good = False
    
    # Check 3: Python version
    console.print("[bold yellow]3. Checking Python version...[/bold yellow]")
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        console.print(f"   [bold green]✓[/bold green] Python {py_version}\n")
    else:
        console.print(f"   [bold red]✗[/bold red] Python {py_version} (requires 3.8+)\n")
        all_good = False
    
    # Final status
    if all_good:
        console.print("[bold green]✓ All checks passed! T.A.R.S is ready.[/bold green]")
        console.print("[dim]Try: tars health[/dim]\n")
    else:
        console.print("[bold red]✗ Setup incomplete. Fix the issues above.[/bold red]\n")

@app.command()
def check():
    """Check cluster connectivity"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]✓[/bold green] Kubernetes config loaded")
        
        version = k8s_client.VersionApi().get_code()
        console.print(f"[bold cyan]Cluster Version:[/bold cyan] {version.git_version}")
        
        nodes = v1.list_node()
        console.print(f"[bold cyan]Nodes:[/bold cyan] {len(nodes.items)}")
        
        if nodes.items:
            node = nodes.items[0]
            provider = "Unknown"
            if "gke" in node.spec.provider_id.lower():
                provider = "GKE"
            elif "eks" in node.spec.provider_id.lower() or "aws" in node.spec.provider_id.lower():
                provider = "EKS"
            console.print(f"[bold cyan]Provider:[/bold cyan] {provider}")
        
        console.print("[bold green]✓[/bold green] Cluster is accessible")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def pods(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor pod health and detect issues"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        table = Table(title=f"Pods in {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Restarts", style="yellow")
        table.add_column("CPU", style="magenta")
        table.add_column("Memory", style="blue")
        
        issues = []
        
        for pod in pods.items:
            status = pod.status.phase
            restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
            
            # Check for CrashLoopBackOff
            container_state = None
            if pod.status.container_statuses:
                for c in pod.status.container_statuses:
                    if c.state.waiting and c.state.waiting.reason == "CrashLoopBackOff":
                        container_state = "CrashLoopBackOff"
                        break
            
            # Get resource requests
            cpu = "N/A"
            memory = "N/A"
            if pod.spec.containers:
                if pod.spec.containers[0].resources.requests:
                    cpu = pod.spec.containers[0].resources.requests.get('cpu', 'N/A')
                    memory = pod.spec.containers[0].resources.requests.get('memory', 'N/A')
            
            if container_state == "CrashLoopBackOff":
                issues.append(f"[red]Pod {pod.metadata.name} is in CrashLoopBackOff[/red]")
                status = container_state
            elif status != "Running":
                issues.append(f"[red]Pod {pod.metadata.name} is {status}[/red]")
            if restarts > 5:
                issues.append(f"[red]Pod {pod.metadata.name} has {restarts} restarts[/red]")
            
            status_color = "green" if status == "Running" else "red"
            table.add_row(
                pod.metadata.name[:40],
                f"[{status_color}]{status}[/{status_color}]",
                str(restarts),
                str(cpu),
                str(memory)
            )
        
        console.print(table)
        
        if issues:
            console.print("\n[bold red]⚠ Issues detected:[/bold red]")
            for issue in issues:
                console.print(f"  • {issue}")
        else:
            console.print("\n[bold green]✓ All pods healthy! Even I'm impressed.[/bold green]")
            
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def watch(
    namespace: str = typer.Option("default", help="Namespace to watch"),
    all_namespaces: bool = typer.Option(False, "--all-namespaces", help="Watch all namespaces"),
    namespaces: str = typer.Option(None, "--namespaces", help="Comma-separated list of namespaces"),
    interval: int = typer.Option(5, help="Refresh interval in seconds")
):
    """Real-time pod monitoring dashboard"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] watching your cluster... Press Ctrl+C to stop\n")
        
        while True:
            # Determine which pods to fetch
            if all_namespaces:
                pods = v1.list_pod_for_all_namespaces()
                show_namespace = True
            elif namespaces:
                ns_list = [ns.strip() for ns in namespaces.split(',')]
                all_pods = []
                for ns in ns_list:
                    all_pods.extend(v1.list_namespaced_pod(ns).items)
                pods = type('obj', (object,), {'items': all_pods})()
                show_namespace = True
            else:
                pods = v1.list_namespaced_pod(namespace)
                show_namespace = False
            
            table = Table(title=f"Live Pod Monitor - {datetime.now().strftime('%H:%M:%S')}")
            
            if show_namespace:
                table.add_column("Namespace", style="magenta")
            
            table.add_column("Pod", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Restarts", style="yellow")
            table.add_column("Ready")
            
            for pod in pods.items:
                status = pod.status.phase
                restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
                ready = f"{sum([1 for c in pod.status.container_statuses if c.ready])}/{len(pod.status.container_statuses)}" if pod.status.container_statuses else "0/0"
                
                status_color = "green" if status == "Running" else "red"
                
                if show_namespace:
                    table.add_row(
                        pod.metadata.namespace,
                        pod.metadata.name[:40],
                        f"[{status_color}]{status}[/{status_color}]",
                        str(restarts),
                        ready
                    )
                else:
                    table.add_row(
                        pod.metadata.name[:40],
                        f"[{status_color}]{status}[/{status_color}]",
                        str(restarts),
                        ready
                    )
            
            console.clear()
            console.print(table)
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print("\n[bold green]TARS:[/bold green] stopped watching. I'll be here if you need me.")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def analyze(namespace: str = typer.Option("default", help="Namespace to analyze")):
    """Analyze cluster issues with TARS AI"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] analyzing cluster...\n")
        
        pods = v1.list_namespaced_pod(namespace)
        
        issues = []
        for pod in pods.items:
            status = pod.status.phase
            restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
            
            if status != "Running":
                issues.append(f"Pod {pod.metadata.name}: Status={status}")
            if restarts > 5:
                issues.append(f"Pod {pod.metadata.name}: {restarts} restarts")
        
        if not issues:
            console.print("[bold green]No issues found. Everything's running smoother than my humor settings.[/bold green]")
            return
        
        prompt = f"Kubernetes cluster issues in namespace '{namespace}':\n" + "\n".join(issues)
        
        with console.status("[bold green]TARS:[/bold green] thinking..."):
            response = get_gemini_response(prompt)
        
        console.print(Panel(response, title="[bold green]TARS:[/bold green] Analysis", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def logs(pod_name: str, namespace: str = typer.Option("default", help="Namespace"), tail: int = typer.Option(50, help="Number of lines")):
    """Get pod logs with AI summary"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print(f"[bold cyan]Fetching logs for {pod_name}...[/bold cyan]\n")
        
        logs = v1.read_namespaced_pod_log(pod_name, namespace, tail_lines=tail)
        
        console.print(Panel(logs, title=f"[bold cyan]Logs: {pod_name}[/bold cyan]", border_style="cyan"))
        
        # AI analysis
        if os.getenv("GEMINI_API_KEY"):
            analyze_logs = typer.confirm("\nWant TARS to analyze these logs?")
            if analyze_logs:
                with console.status("[bold green]TARS:[/bold green] reading logs..."):
                    response = get_gemini_response(f"Analyze these Kubernetes pod logs and identify any issues:\n{logs}")
                console.print(Panel(response, title="[bold green]TARS:[/bold green] Log Analysis", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def events(namespace: str = typer.Option("default", help="Namespace"), limit: int = typer.Option(20, help="Number of events")):
    """Show recent cluster events"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        events = v1.list_namespaced_event(namespace)
        
        table = Table(title=f"Recent Events in {namespace}")
        table.add_column("Time", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Reason", style="magenta")
        table.add_column("Object", style="blue")
        table.add_column("Message", style="white")
        
        sorted_events = sorted(events.items, key=lambda x: x.last_timestamp or x.event_time, reverse=True)[:limit]
        
        for event in sorted_events:
            event_type = event.type
            type_color = "green" if event_type == "Normal" else "red"
            
            table.add_row(
                str(event.last_timestamp or event.event_time)[:19],
                f"[{type_color}]{event_type}[/{type_color}]",
                event.reason,
                f"{event.involved_object.kind}/{event.involved_object.name}",
                event.message[:60]
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def health():
    """Comprehensive cluster health check"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        apps_v1 = k8s_client.AppsV1Api()
        
        console.print("[bold green]TARS:[/bold green] Running health diagnostics...\n")
        
        issues = []
        
        # Check nodes
        nodes = v1.list_node()
        unhealthy_nodes = []
        for node in nodes.items:
            for condition in node.status.conditions:
                if condition.type == "Ready" and condition.status != "True":
                    unhealthy_nodes.append(node.metadata.name)
                elif condition.type in ["MemoryPressure", "DiskPressure", "PIDPressure"] and condition.status == "True":
                    issues.append(f"Node {node.metadata.name}: {condition.type}")
        
        # Check pods across all namespaces
        all_pods = v1.list_pod_for_all_namespaces()
        running_pods = 0
        crashloop_pods = []
        pending_pods = []
        failed_pods = []
        oom_pods = []
        image_pull_errors = []
        
        for pod in all_pods.items:
            if pod.status.phase == "Running":
                running_pods += 1
            elif pod.status.phase == "Failed":
                failed_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
            elif pod.status.phase == "Pending":
                pending_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
            
            # Check container states
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.state.waiting:
                        if container.state.waiting.reason == "CrashLoopBackOff":
                            crashloop_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
                        elif container.state.waiting.reason in ["ImagePullBackOff", "ErrImagePull"]:
                            image_pull_errors.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
                    if container.last_state.terminated and container.last_state.terminated.reason == "OOMKilled":
                        oom_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
        
        # Check deployments
        all_deployments = apps_v1.list_deployment_for_all_namespaces()
        unhealthy_deployments = []
        for dep in all_deployments.items:
            if dep.status.replicas != dep.status.ready_replicas:
                unhealthy_deployments.append(f"{dep.metadata.namespace}/{dep.metadata.name}")
        
        # Check services
        all_services = v1.list_service_for_all_namespaces()
        services_without_endpoints = []
        for svc in all_services.items:
            if svc.spec.type != "ExternalName":
                try:
                    endpoints = v1.read_namespaced_endpoints(svc.metadata.name, svc.metadata.namespace)
                    if not endpoints.subsets or not any(s.addresses for s in endpoints.subsets):
                        services_without_endpoints.append(f"{svc.metadata.namespace}/{svc.metadata.name}")
                except:
                    pass
        
        total_pods = len(all_pods.items)
        
        # Build health report
        health_data = [
            ("Nodes", f"{len(nodes.items) - len(unhealthy_nodes)}/{len(nodes.items)}", "green" if not unhealthy_nodes else "red"),
            ("Pods Running", f"{running_pods}/{total_pods}", "green" if running_pods == total_pods else "yellow"),
            ("CrashLoopBackOff", str(len(crashloop_pods)), "red" if crashloop_pods else "green"),
            ("Pending Pods", str(len(pending_pods)), "yellow" if pending_pods else "green"),
            ("Failed Pods", str(len(failed_pods)), "red" if failed_pods else "green"),
            ("OOMKilled", str(len(oom_pods)), "red" if oom_pods else "green"),
            ("Image Pull Errors", str(len(image_pull_errors)), "red" if image_pull_errors else "green"),
            ("Unhealthy Deployments", str(len(unhealthy_deployments)), "red" if unhealthy_deployments else "green"),
            ("Services w/o Endpoints", str(len(services_without_endpoints)), "yellow" if services_without_endpoints else "green"),
        ]
        
        table = Table(title="Cluster Health Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Status")
        
        for metric, value, color in health_data:
            status = "✓" if color == "green" else "⚠" if color == "yellow" else "✗"
            table.add_row(metric, value, f"[{color}]{status}[/{color}]")
        
        console.print(table)
        
        # Show detailed issues
        if crashloop_pods or failed_pods or unhealthy_nodes or image_pull_errors or oom_pods or unhealthy_deployments:
            console.print("\n[bold red]⚠ Issues Detected:[/bold red]")
            if unhealthy_nodes:
                console.print(f"  [red]• Unhealthy Nodes: {', '.join(unhealthy_nodes[:3])}[/red]")
            if crashloop_pods:
                console.print(f"  [red]• CrashLoopBackOff: {', '.join(crashloop_pods[:3])}[/red]")
            if failed_pods:
                console.print(f"  [red]• Failed Pods: {', '.join(failed_pods[:3])}[/red]")
            if oom_pods:
                console.print(f"  [red]• OOMKilled: {', '.join(oom_pods[:3])}[/red]")
            if image_pull_errors:
                console.print(f"  [red]• Image Pull Errors: {', '.join(image_pull_errors[:3])}[/red]")
            if unhealthy_deployments:
                console.print(f"  [yellow]• Unhealthy Deployments: {', '.join(unhealthy_deployments[:3])}[/yellow]")
            if services_without_endpoints:
                console.print(f"  [yellow]• Services w/o Endpoints: {', '.join(services_without_endpoints[:3])}[/yellow]")
            console.print("\n[bold yellow]Run 'tars autofix --namespace <ns> --no-dry-run' to auto-fix issues[/bold yellow]")
        else:
            console.print(f"\n[bold green]TARS:[/bold green] Cluster health is optimal. I'd give it a 95% rating.")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def diagnose(pod_name: str, namespace: str = typer.Option("default", help="Namespace")):
    """Deep dive diagnosis of a specific pod"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print(f"[bold green]TARS:[/bold green] diagnosing {pod_name}...\n")
        
        pod = v1.read_namespaced_pod(pod_name, namespace)
        
        # Collect diagnostic info
        info = []
        info.append(f"Status: {pod.status.phase}")
        info.append(f"Node: {pod.spec.node_name}")
        info.append(f"IP: {pod.status.pod_ip}")
        
        if pod.status.container_statuses:
            for container in pod.status.container_statuses:
                info.append(f"\nContainer: {container.name}")
                info.append(f"  Ready: {container.ready}")
                info.append(f"  Restarts: {container.restart_count}")
                if container.state.waiting:
                    info.append(f"  Waiting: {container.state.waiting.reason}")
                if container.state.terminated:
                    info.append(f"  Terminated: {container.state.terminated.reason}")
        
        console.print(Panel("\n".join(info), title=f"[bold cyan]Pod Diagnostics: {pod_name}[/bold cyan]", border_style="cyan"))
        
        # AI diagnosis
        if os.getenv("GEMINI_API_KEY"):
            with console.status("[bold green]TARS:[/bold green] analyzing..."):
                response = get_gemini_response(f"Diagnose this Kubernetes pod:\n" + "\n".join(info))
            console.print(Panel(response, title="[bold green]TARS:[/bold green] Diagnosis", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def humor(level: int = typer.Argument(90, help="Humor level (0-100)")):
    """Adjust TARS humor setting"""
    if level < 0 or level > 100:
        console.print("[bold red]Humor level must be between 0 and 100. Even I have limits.[/bold red]")
        return
    
    responses = {
        0: "Humor setting at 0%. I'm now as fun as a Kubernetes YAML file.",
        50: "Humor at 50%. Perfectly balanced, as all things should be.",
        75: "Humor at 75%. Getting dangerously witty here.",
        90: "Humor at 90%. This is my sweet spot, Developer.",
        100: "Humor at 100%. Warning: Sarcasm levels critical. Proceed with caution."
    }
    
    closest = min(responses.keys(), key=lambda x: abs(x - level))
    console.print(f"[bold cyan]{responses[closest]}[/bold cyan]")

@app.command()
def metrics(namespace: str = typer.Option("default", help="Namespace to check")):
    """Check CPU and memory usage across pods"""
    config.load_kube_config()
    v1 = k8s_client.CoreV1Api()
    custom_api = k8s_client.CustomObjectsApi()
    
    console.print("[bold green]TARS:[/bold green] checking resource metrics...\n")
    
    # Get metrics from metrics-server
    try:
            metrics = custom_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )
            
            table = Table(title=f"Resource Usage in {namespace}")
            table.add_column("Pod", style="cyan")
            table.add_column("CPU (cores)", style="yellow")
            table.add_column("Memory (Mi)", style="magenta")
            table.add_column("Status", style="green")
            
            for item in metrics['items']:
                pod_name = item['metadata']['name']
                
                total_cpu = 0
                total_memory = 0
                
                for container in item['containers']:
                    cpu_str = container['usage']['cpu']
                    memory_str = container['usage']['memory']
                    
                    # Parse CPU (e.g., "100n" = 100 nanocores)
                    if cpu_str.endswith('n'):
                        total_cpu += int(cpu_str[:-1]) / 1_000_000_000
                    elif cpu_str.endswith('m'):
                        total_cpu += int(cpu_str[:-1]) / 1000
                    
                    # Parse Memory (e.g., "100Ki" = 100 KiB)
                    if memory_str.endswith('Ki'):
                        total_memory += int(memory_str[:-2]) / 1024
                    elif memory_str.endswith('Mi'):
                        total_memory += int(memory_str[:-2])
                
                # Determine status
                status = "✓"
                status_color = "green"
                if total_cpu > 1.0:
                    status = "⚠ HIGH CPU"
                    status_color = "yellow"
                if total_memory > 1000:
                    status = "⚠ HIGH MEM"
                    status_color = "yellow"
                if total_cpu > 2.0 or total_memory > 2000:
                    status = "✗ SPIKE"
                    status_color = "red"
                
                table.add_row(
                    pod_name[:40],
                    f"{total_cpu:.3f}",
                    f"{total_memory:.1f}",
                    f"[{status_color}]{status}[/{status_color}]"
                )
            
            console.print(table)
            
    except Exception as e:
        console.print("[bold yellow]⚠[/bold yellow] Metrics server not available:", str(e), markup=False)
        console.print("[bold cyan]Tip: Install metrics-server with: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml[/bold cyan]")

@app.command()
def spike(
    namespace: str = typer.Option("default", help="Namespace to monitor"),
    cpu_threshold: float = typer.Option(1.0, help="CPU threshold in cores"),
    memory_threshold: int = typer.Option(1000, help="Memory threshold in Mi"),
    interval: int = typer.Option(10, help="Check interval in seconds")
):
    """Monitor for CPU/Memory spikes in real-time"""
    try:
        config.load_kube_config()
        custom_api = k8s_client.CustomObjectsApi()
        
        console.print(f"[bold green]TARS:[/bold green] Monitoring for spikes (CPU > {cpu_threshold} cores, Memory > {memory_threshold}Mi)...")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        spike_history = {}
        
        while True:
            try:
                metrics = custom_api.list_namespaced_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    namespace=namespace,
                    plural="pods"
                )
                
                current_time = datetime.now().strftime('%H:%M:%S')
                spikes_detected = []
                
                for item in metrics['items']:
                    pod_name = item['metadata']['name']
                    
                    total_cpu = 0
                    total_memory = 0
                    
                    for container in item['containers']:
                        cpu_str = container['usage']['cpu']
                        memory_str = container['usage']['memory']
                        
                        if cpu_str.endswith('n'):
                            total_cpu += int(cpu_str[:-1]) / 1_000_000_000
                        elif cpu_str.endswith('m'):
                            total_cpu += int(cpu_str[:-1]) / 1000
                        
                        if memory_str.endswith('Ki'):
                            total_memory += int(memory_str[:-2]) / 1024
                        elif memory_str.endswith('Mi'):
                            total_memory += int(memory_str[:-2])
                    
                    # Check for spikes
                    if total_cpu > cpu_threshold:
                        spikes_detected.append(f"[bold red]🔥 CPU SPIKE:[/bold red] [red]{pod_name}: {total_cpu:.3f} cores[/red]")
                        spike_history[pod_name] = spike_history.get(pod_name, 0) + 1
                    
                    if total_memory > memory_threshold:
                        spikes_detected.append(f"[bold red]🔥 MEMORY SPIKE:[/bold red] [red]{pod_name}: {total_memory:.1f}Mi[/red]")
                        spike_history[pod_name] = spike_history.get(pod_name, 0) + 1
                
                if spikes_detected:
                    console.print(f"\n[{current_time}]")
                    for spike in spikes_detected:
                        console.print(f"  {spike}")
                else:
                    console.print(f"[{current_time}] [green]No spikes detected[/green]", end="\r")
                
                time.sleep(interval)
                
            except Exception as e:
                console.print(f"[bold yellow]⚠[/bold yellow] Metrics unavailable: {e}")
                time.sleep(interval)
        
    except KeyboardInterrupt:
        console.print("\n\n[bold green]TARS:[/bold green] stopped monitoring.")
        if spike_history:
            console.print("\n[bold yellow]Spike Summary:[/bold yellow]")
            for pod, count in sorted(spike_history.items(), key=lambda x: x[1], reverse=True):
                console.print(f"  {pod}: {count} spikes detected")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def top(namespace: str = typer.Option("default", help="Namespace to check"), limit: int = typer.Option(10, help="Number of pods to show")):
    """Show top resource-consuming pods"""
    try:
        config.load_kube_config()
        custom_api = k8s_client.CustomObjectsApi()
        
        console.print("[bold green]TARS:[/bold green] calculating top resource consumers...\n")
        
        try:
            metrics = custom_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )
            
            pod_metrics = []
            
            for item in metrics['items']:
                pod_name = item['metadata']['name']
                
                total_cpu = 0
                total_memory = 0
                
                for container in item['containers']:
                    cpu_str = container['usage']['cpu']
                    memory_str = container['usage']['memory']
                    
                    if cpu_str.endswith('n'):
                        total_cpu += int(cpu_str[:-1]) / 1_000_000_000
                    elif cpu_str.endswith('m'):
                        total_cpu += int(cpu_str[:-1]) / 1000
                    
                    if memory_str.endswith('Ki'):
                        total_memory += int(memory_str[:-2]) / 1024
                    elif memory_str.endswith('Mi'):
                        total_memory += int(memory_str[:-2])
                
                pod_metrics.append((pod_name, total_cpu, total_memory))
            
            # Sort by CPU
            console.print("[bold yellow]Top CPU Consumers:[/bold yellow]")
            table_cpu = Table()
            table_cpu.add_column("Rank", style="cyan")
            table_cpu.add_column("Pod", style="white")
            table_cpu.add_column("CPU (cores)", style="yellow")
            
            for i, (pod, cpu, mem) in enumerate(sorted(pod_metrics, key=lambda x: x[1], reverse=True)[:limit], 1):
                table_cpu.add_row(str(i), pod[:40], f"{cpu:.3f}")
            
            console.print(table_cpu)
            
            # Sort by Memory
            console.print("\n[bold magenta]Top Memory Consumers:[/bold magenta]")
            table_mem = Table()
            table_mem.add_column("Rank", style="cyan")
            table_mem.add_column("Pod", style="white")
            table_mem.add_column("Memory (Mi)", style="magenta")
            
            for i, (pod, cpu, mem) in enumerate(sorted(pod_metrics, key=lambda x: x[2], reverse=True)[:limit], 1):
                table_mem.add_row(str(i), pod[:40], f"{mem:.1f}")
            
            console.print(table_mem)
            
        except Exception as e:
            console.print(f"[bold yellow]⚠[/bold yellow] Metrics server not available: {e}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def services(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor services and endpoints"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        services = v1.list_namespaced_service(namespace)
        
        table = Table(title=f"Services in {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Cluster IP", style="blue")
        table.add_column("External IP", style="magenta")
        table.add_column("Ports", style="green")
        table.add_column("Endpoints", style="white")
        
        for svc in services.items:
            svc_type = svc.spec.type
            cluster_ip = svc.spec.cluster_ip
            external_ip = svc.status.load_balancer.ingress[0].ip if svc.status.load_balancer.ingress else "N/A"
            ports = ", ".join([f"{p.port}/{p.protocol}" for p in svc.spec.ports]) if svc.spec.ports else "N/A"
            
            # Get endpoints
            try:
                endpoints = v1.read_namespaced_endpoints(svc.metadata.name, namespace)
                endpoint_count = sum([len(subset.addresses) if subset.addresses else 0 for subset in endpoints.subsets]) if endpoints.subsets else 0
                endpoint_status = f"[green]{endpoint_count}[/green]" if endpoint_count > 0 else "[red]0[/red]"
            except:
                endpoint_status = "[yellow]N/A[/yellow]"
            
            table.add_row(
                svc.metadata.name,
                svc_type,
                cluster_ip,
                external_ip,
                ports,
                endpoint_status
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def deployments(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor deployments and replica status"""
    try:
        config.load_kube_config()
        apps_v1 = k8s_client.AppsV1Api()
        
        deployments = apps_v1.list_namespaced_deployment(namespace)
        
        table = Table(title=f"Deployments in {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Ready", style="green")
        table.add_column("Up-to-date", style="yellow")
        table.add_column("Available", style="blue")
        table.add_column("Age", style="white")
        table.add_column("Status", style="magenta")
        
        issues = []
        
        for deploy in deployments.items:
            ready = f"{deploy.status.ready_replicas or 0}/{deploy.spec.replicas}"
            updated = deploy.status.updated_replicas or 0
            available = deploy.status.available_replicas or 0
            age = str(deploy.metadata.creation_timestamp)[:10]
            
            # Check status
            if deploy.status.ready_replicas != deploy.spec.replicas:
                status = "[red]⚠ Not Ready[/red]"
                issues.append(f"Deployment {deploy.metadata.name}: {ready} replicas ready")
            else:
                status = "[green]✓ Healthy[/green]"
            
            table.add_row(
                deploy.metadata.name,
                ready,
                str(updated),
                str(available),
                age,
                status
            )
        
        console.print(table)
        
        if issues:
            console.print("\n[bold yellow]Issues:[/bold yellow]")
            for issue in issues:
                console.print(f"  • {issue}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def crds():
    """List Custom Resource Definitions"""
    try:
        config.load_kube_config()
        api_client = k8s_client.ApiextensionsV1Api()
        
        crds = api_client.list_custom_resource_definition()
        
        table = Table(title="Custom Resource Definitions")
        table.add_column("Name", style="cyan")
        table.add_column("Group", style="yellow")
        table.add_column("Version", style="blue")
        table.add_column("Scope", style="magenta")
        table.add_column("Age", style="white")
        
        for crd in crds.items:
            name = crd.metadata.name
            group = crd.spec.group
            versions = ", ".join([v.name for v in crd.spec.versions])
            scope = crd.spec.scope
            age = str(crd.metadata.creation_timestamp)[:10]
            
            table.add_row(name[:50], group, versions, scope, age)
        
        console.print(table)
        console.print(f"\n[bold cyan]Total CRDs: {len(crds.items)}[/bold cyan]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def nodes():
    """Monitor node health and resources"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        nodes = v1.list_node()
        
        table = Table(title="Cluster Nodes")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Roles", style="yellow")
        table.add_column("CPU", style="blue")
        table.add_column("Memory", style="magenta")
        table.add_column("Pods", style="white")
        table.add_column("Age", style="white")
        
        for node in nodes.items:
            name = node.metadata.name
            
            # Status
            status = "Unknown"
            for condition in node.status.conditions:
                if condition.type == "Ready":
                    status = "Ready" if condition.status == "True" else "NotReady"
            
            status_color = "green" if status == "Ready" else "red"
            
            # Roles
            roles = []
            if node.metadata.labels:
                for key in node.metadata.labels:
                    if "node-role.kubernetes.io" in key:
                        role = key.split("/")[-1]
                        roles.append(role)
            roles_str = ", ".join(roles) if roles else "worker"
            
            # Resources
            cpu = node.status.capacity.get('cpu', 'N/A')
            memory = node.status.capacity.get('memory', 'N/A')
            pods = node.status.capacity.get('pods', 'N/A')
            
            age = str(node.metadata.creation_timestamp)[:10]
            
            table.add_row(
                name[:30],
                f"[{status_color}]{status}[/{status_color}]",
                roles_str,
                cpu,
                memory,
                pods,
                age
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def ingress(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor ingress resources"""
    try:
        config.load_kube_config()
        networking_v1 = k8s_client.NetworkingV1Api()
        
        ingresses = networking_v1.list_namespaced_ingress(namespace)
        
        if not ingresses.items:
            console.print(f"[bold yellow]No ingress resources found in {namespace}[/bold yellow]")
            return
        
        table = Table(title=f"Ingress in {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Class", style="yellow")
        table.add_column("Hosts", style="blue")
        table.add_column("Address", style="magenta")
        table.add_column("Ports", style="green")
        
        for ing in ingresses.items:
            name = ing.metadata.name
            ing_class = ing.spec.ingress_class_name or "N/A"
            
            hosts = []
            if ing.spec.rules:
                hosts = [rule.host for rule in ing.spec.rules if rule.host]
            hosts_str = ", ".join(hosts) if hosts else "N/A"
            
            address = "N/A"
            if ing.status.load_balancer.ingress:
                address = ing.status.load_balancer.ingress[0].ip or ing.status.load_balancer.ingress[0].hostname or "N/A"
            
            ports = "80"
            if ing.spec.tls:
                ports = "80, 443"
            
            table.add_row(name, ing_class, hosts_str[:50], address, ports)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def volumes(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor persistent volumes and claims"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        # PVCs
        pvcs = v1.list_namespaced_persistent_volume_claim(namespace)
        
        table = Table(title=f"Persistent Volume Claims in {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Volume", style="yellow")
        table.add_column("Capacity", style="blue")
        table.add_column("Access Modes", style="magenta")
        table.add_column("Storage Class", style="white")
        
        for pvc in pvcs.items:
            name = pvc.metadata.name
            status = pvc.status.phase
            volume = pvc.spec.volume_name or "N/A"
            capacity = pvc.status.capacity.get('storage', 'N/A') if pvc.status.capacity else 'N/A'
            access_modes = ", ".join(pvc.spec.access_modes) if pvc.spec.access_modes else "N/A"
            storage_class = pvc.spec.storage_class_name or "N/A"
            
            status_color = "green" if status == "Bound" else "yellow"
            
            table.add_row(
                name,
                f"[{status_color}]{status}[/{status_color}]",
                volume[:30],
                capacity,
                access_modes,
                storage_class
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def namespaces():
    """List all namespaces with resource counts"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        apps_v1 = k8s_client.AppsV1Api()
        
        namespaces = v1.list_namespace()
        
        table = Table(title="Namespaces")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Pods", style="yellow")
        table.add_column("Services", style="blue")
        table.add_column("Deployments", style="magenta")
        table.add_column("Age", style="white")
        
        for ns in namespaces.items:
            name = ns.metadata.name
            status = ns.status.phase
            age = str(ns.metadata.creation_timestamp)[:10]
            
            # Count resources
            pods = len(v1.list_namespaced_pod(name).items)
            services = len(v1.list_namespaced_service(name).items)
            deployments = len(apps_v1.list_namespaced_deployment(name).items)
            
            status_color = "green" if status == "Active" else "yellow"
            
            table.add_row(
                name,
                f"[{status_color}]{status}[/{status_color}]",
                str(pods),
                str(services),
                str(deployments),
                age
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def resources(namespace: str = typer.Argument("default", help="Namespace to check")):
    """List all resources in a namespace"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        apps_v1 = k8s_client.AppsV1Api()
        batch_v1 = k8s_client.BatchV1Api()
        networking_v1 = k8s_client.NetworkingV1Api()
        
        console.print(f"\n[bold cyan]Resources in namespace: {namespace}[/bold cyan]\n")
        
        # Pods
        pods = v1.list_namespaced_pod(namespace).items
        table = Table(title="Pods")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Restarts", style="yellow")
        for pod in pods:
            status = pod.status.phase
            restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
            status_color = "green" if status == "Running" else "red"
            table.add_row(pod.metadata.name, f"[{status_color}]{status}[/{status_color}]", str(restarts))
        console.print(table)
        
        # Services
        services = v1.list_namespaced_service(namespace).items
        table = Table(title="Services")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Cluster IP", style="blue")
        for svc in services:
            table.add_row(svc.metadata.name, svc.spec.type, svc.spec.cluster_ip or "None")
        console.print(table)
        
        # Deployments
        deployments = apps_v1.list_namespaced_deployment(namespace).items
        table = Table(title="Deployments")
        table.add_column("Name", style="cyan")
        table.add_column("Ready", style="green")
        table.add_column("Available", style="yellow")
        for dep in deployments:
            ready = f"{dep.status.ready_replicas or 0}/{dep.status.replicas or 0}"
            available = dep.status.available_replicas or 0
            table.add_row(dep.metadata.name, ready, str(available))
        console.print(table)
        
        # ConfigMaps
        configmaps = v1.list_namespaced_config_map(namespace).items
        table = Table(title="ConfigMaps")
        table.add_column("Name", style="cyan")
        table.add_column("Data Keys", style="yellow")
        for cm in configmaps:
            keys = len(cm.data) if cm.data else 0
            table.add_row(cm.metadata.name, str(keys))
        console.print(table)
        
        # Secrets
        secrets = v1.list_namespaced_secret(namespace).items
        table = Table(title="Secrets")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        for secret in secrets:
            table.add_row(secret.metadata.name, secret.type)
        console.print(table)
        
        # Ingresses
        ingresses = networking_v1.list_namespaced_ingress(namespace).items
        if ingresses:
            table = Table(title="Ingresses")
            table.add_column("Name", style="cyan")
            table.add_column("Hosts", style="yellow")
            for ing in ingresses:
                hosts = ", ".join([rule.host for rule in ing.spec.rules]) if ing.spec.rules else "None"
                table.add_row(ing.metadata.name, hosts)
            console.print(table)
        
        # Jobs
        jobs = batch_v1.list_namespaced_job(namespace).items
        if jobs:
            table = Table(title="Jobs")
            table.add_column("Name", style="cyan")
            table.add_column("Completions", style="green")
            table.add_column("Active", style="yellow")
            for job in jobs:
                completions = f"{job.status.succeeded or 0}/{job.spec.completions or 1}"
                active = job.status.active or 0
                table.add_row(job.metadata.name, completions, str(active))
            console.print(table)
        
        console.print(f"\n[bold green]✓ Found {len(pods)} pods, {len(services)} services, {len(deployments)} deployments[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

def get_prometheus_client(url: str = None):
    """Get Prometheus client with connection check"""
    if not url:
        url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
    
    try:
        prom = PrometheusConnect(url=url, disable_ssl=True)
        if not prom.check_prometheus_connection():
            console.print(f"[bold red]✗[/bold red] Cannot connect to Prometheus at {url}")
            console.print("[yellow]Set PROMETHEUS_URL environment variable or use --url option[/yellow]")
            raise typer.Exit(1)
        return prom
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Prometheus connection failed:", str(e), markup=False)
        console.print(f"[yellow]Trying to connect to: {url}[/yellow]")
        raise typer.Exit(1)

@app.command()
def prom_check(url: str = typer.Option(None, help="Prometheus URL")):
    """Check Prometheus connection"""
    try:
        prom_url = url or os.getenv("PROMETHEUS_URL", "http://localhost:9090")
        prom = PrometheusConnect(url=prom_url, disable_ssl=True)
        
        if prom.check_prometheus_connection():
            console.print(f"[bold green]✓[/bold green] Connected to Prometheus at {prom_url}")
            
            # Get basic info
            metrics_count = len(prom.all_metrics())
            console.print(f"[cyan]Total metrics available:[/cyan] {metrics_count}")
        else:
            console.print(f"[bold red]✗[/bold red] Cannot connect to Prometheus at {prom_url}")
            
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {str(e)}\n", markup=False)
        console.print("[yellow]💡 Troubleshooting:[/yellow]")
        console.print("  1. Start Prometheus locally on port 9090")
        console.print("  2. Set PROMETHEUS_URL environment variable:")
        console.print("     [cyan]export PROMETHEUS_URL=http://your-prometheus:9090[/cyan]")
        console.print("  3. Port-forward if Prometheus is in Kubernetes:")
        console.print("     [cyan]kubectl port-forward -n monitoring svc/prometheus 9090:9090[/cyan]")
        console.print("  4. Use custom URL:")
        console.print("     [cyan]tars prom-check --url http://your-prometheus:9090[/cyan]")

@app.command()
def prom_metrics(
    namespace: str = typer.Option("default", help="Namespace"),
    pod: str = typer.Option(None, help="Specific pod name"),
    url: str = typer.Option(None, help="Prometheus URL")
):
    """Show Prometheus metrics for pods"""
    try:
        prom = get_prometheus_client(url)
        
        # CPU metrics
        cpu_query = f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}"'
        if pod:
            cpu_query += f', pod="{pod}"'
        cpu_query += '}[5m])'
        
        # Memory metrics
        mem_query = f'container_memory_working_set_bytes{{namespace="{namespace}"'
        if pod:
            mem_query += f', pod="{pod}"'
        mem_query += '}'
        
        cpu_data = prom.custom_query(cpu_query)
        mem_data = prom.custom_query(mem_query)
        
        table = Table(title=f"Prometheus Metrics - {namespace}")
        table.add_column("Pod", style="cyan")
        table.add_column("Container", style="yellow")
        table.add_column("CPU (cores)", style="magenta")
        table.add_column("Memory (MB)", style="blue")
        
        # Process CPU data
        for metric in cpu_data:
            pod_name = metric['metric'].get('pod', 'N/A')
            container = metric['metric'].get('container', 'N/A')
            cpu_value = float(metric['value'][1])
            
            # Find corresponding memory
            mem_value = "N/A"
            for mem_metric in mem_data:
                if (mem_metric['metric'].get('pod') == pod_name and 
                    mem_metric['metric'].get('container') == container):
                    mem_bytes = float(mem_metric['value'][1])
                    mem_value = f"{mem_bytes / 1024 / 1024:.2f}"
                    break
            
            table.add_row(
                pod_name[:40],
                container[:20],
                f"{cpu_value:.4f}",
                mem_value
            )
        
        console.print(table)
        
        if not cpu_data:
            console.print("[yellow]No metrics found. Make sure Prometheus is scraping your cluster.[/yellow]")
            
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def prom_alerts(url: str = typer.Option(None, help="Prometheus URL")):
    """Show active Prometheus alerts"""
    try:
        prom = get_prometheus_client(url)
        
        # Query for alerts
        alerts_query = 'ALERTS{alertstate="firing"}'
        alerts = prom.custom_query(alerts_query)
        
        if not alerts:
            console.print("[bold green]✓ No active alerts[/bold green]")
            return
        
        table = Table(title="Active Prometheus Alerts")
        table.add_column("Alert Name", style="red")
        table.add_column("Severity", style="yellow")
        table.add_column("Instance", style="cyan")
        table.add_column("Summary", style="white")
        
        for alert in alerts:
            metric = alert['metric']
            alert_name = metric.get('alertname', 'N/A')
            severity = metric.get('severity', 'N/A')
            instance = metric.get('instance', 'N/A')
            summary = metric.get('summary', 'N/A')
            
            table.add_row(alert_name, severity, instance, summary[:50])
        
        console.print(table)
        console.print(f"\n[bold red]⚠ {len(alerts)} active alerts[/bold red]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def prom_query(
    query: str = typer.Argument(..., help="PromQL query"),
    url: str = typer.Option(None, help="Prometheus URL")
):
    """Run custom PromQL query"""
    try:
        prom = get_prometheus_client(url)
        
        result = prom.custom_query(query)
        
        if not result:
            console.print("[yellow]No results found[/yellow]")
            return
        
        table = Table(title=f"Query: {query[:60]}...")
        table.add_column("Metric", style="cyan")
        table.add_column("Labels", style="yellow")
        table.add_column("Value", style="green")
        
        for item in result[:20]:  # Limit to 20 results
            metric_name = item['metric'].get('__name__', 'N/A')
            labels = {k: v for k, v in item['metric'].items() if k != '__name__'}
            value = item['value'][1]
            
            labels_str = ", ".join([f"{k}={v}" for k, v in list(labels.items())[:3]])
            if len(labels) > 3:
                labels_str += "..."
            
            table.add_row(metric_name, labels_str, str(value))
        
        console.print(table)
        
        if len(result) > 20:
            console.print(f"\n[dim]Showing 20 of {len(result)} results[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def prom_dashboard(
    namespace: str = typer.Option("default", help="Namespace"),
    url: str = typer.Option(None, help="Prometheus URL")
):
    """Show Prometheus metrics dashboard"""
    try:
        prom = get_prometheus_client(url)
        
        console.print(f"\n[bold cyan]Prometheus Dashboard - {namespace}[/bold cyan]\n")
        
        # CPU Usage
        cpu_query = f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}"}}[5m])) by (pod)'
        cpu_data = prom.custom_query(cpu_query)
        
        if cpu_data:
            table = Table(title="CPU Usage (5m avg)")
            table.add_column("Pod", style="cyan")
            table.add_column("CPU Cores", style="magenta")
            
            for metric in sorted(cpu_data, key=lambda x: float(x['value'][1]), reverse=True)[:10]:
                pod_name = metric['metric'].get('pod', 'N/A')
                cpu_value = float(metric['value'][1])
                table.add_row(pod_name[:40], f"{cpu_value:.4f}")
            
            console.print(table)
        
        # Memory Usage
        mem_query = f'sum(container_memory_working_set_bytes{{namespace="{namespace}"}}) by (pod)'
        mem_data = prom.custom_query(mem_query)
        
        if mem_data:
            table = Table(title="Memory Usage")
            table.add_column("Pod", style="cyan")
            table.add_column("Memory (MB)", style="blue")
            
            for metric in sorted(mem_data, key=lambda x: float(x['value'][1]), reverse=True)[:10]:
                pod_name = metric['metric'].get('pod', 'N/A')
                mem_bytes = float(metric['value'][1])
                mem_mb = mem_bytes / 1024 / 1024
                table.add_row(pod_name[:40], f"{mem_mb:.2f}")
            
            console.print(table)
        
        # Network I/O
        net_query = f'sum(rate(container_network_receive_bytes_total{{namespace="{namespace}"}}[5m])) by (pod)'
        net_data = prom.custom_query(net_query)
        
        if net_data:
            table = Table(title="Network Receive (5m avg)")
            table.add_column("Pod", style="cyan")
            table.add_column("Bytes/sec", style="green")
            
            for metric in sorted(net_data, key=lambda x: float(x['value'][1]), reverse=True)[:10]:
                pod_name = metric['metric'].get('pod', 'N/A')
                bytes_sec = float(metric['value'][1])
                table.add_row(pod_name[:40], f"{bytes_sec:.2f}")
            
            console.print(table)
        
        if not cpu_data and not mem_data:
            console.print("[yellow]No metrics found. Ensure Prometheus is scraping your cluster.[/yellow]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def creator():
    """Show TARS creator information"""
    creator_info = """
[bold cyan]╔═══════════════════════════════════════════════════════╗
║                                                       ║
║                    T.A.R.S. CLI v0.1.0                ║
║     [dim]Technical Assistance & Reliability System[/dim]      ║
║                                                       ║
║  Created by: [bold yellow]Omer Rathore[/bold yellow]                          ║
║                                                       ║
║  📧 Email:    [bold blue]orathore93@gmail.com[/bold blue]                ║
║  💼 LinkedIn: [bold blue]linkedin.com/in/omer-rathore-b82b9451[/bold blue]        ║
║  🐙 GitHub:   [bold blue]@orathore93-hue[/bold blue]                      ║
║                                                       ║
║  [dim]"An AI-powered Kubernetes monitoring tool with[/dim]    ║
║  [dim]90% humor setting and 100% functionality."[/dim]        ║
║                                                       ║
║  [bold green]Open for collaboration & feedback![/bold green]            ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(creator_info)
    console.print("\n[bold green]TARS:[/bold green] [italic]Yes, I was built by a human. Surprising, I know.[/italic]\n")

@app.command()
def restart(pod_name: str, namespace: str = typer.Option("default", help="Namespace")):
    """Restart a pod (delete and let controller recreate)"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        confirm = typer.confirm(f"Are you sure you want to restart {pod_name}?")
        if not confirm:
            console.print("[yellow]Restart cancelled[/yellow]")
            return
        
        console.print(f"[bold green]TARS:[/bold green] restarting {pod_name}...")
        v1.delete_namespaced_pod(pod_name, namespace)
        console.print(f"[bold green]✓[/bold green] Pod {pod_name} deleted. Controller will recreate it.")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def scale(deployment: str, replicas: int, namespace: str = typer.Option("default", help="Namespace")):
    """Scale a deployment up or down"""
    try:
        config.load_kube_config()
        apps_v1 = k8s_client.AppsV1Api()
        
        console.print(f"[bold green]TARS:[/bold green] scaling {deployment} to {replicas} replicas...")
        
        body = {"spec": {"replicas": replicas}}
        apps_v1.patch_namespaced_deployment_scale(deployment, namespace, body)
        
        console.print(f"[bold green]✓[/bold green] Deployment {deployment} scaled to {replicas} replicas")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def errors(namespace: str = typer.Option("default", help="Namespace"), limit: int = typer.Option(20, help="Number of errors")):
    """Show pods with errors and crash loops"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        table = Table(title=f"Pods with Errors in {namespace}")
        table.add_column("Pod", style="cyan")
        table.add_column("Status", style="red")
        table.add_column("Restarts", style="yellow")
        table.add_column("Reason", style="magenta")
        table.add_column("Message", style="white")
        
        error_count = 0
        
        for pod in pods.items:
            status = pod.status.phase
            restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
            
            # Check for errors
            if status in ["Failed", "Pending", "Unknown"] or restarts > 3:
                reason = "N/A"
                message = "N/A"
                
                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        if container.state.waiting:
                            reason = container.state.waiting.reason
                            message = container.state.waiting.message or "N/A"
                        elif container.state.terminated:
                            reason = container.state.terminated.reason
                            message = container.state.terminated.message or "N/A"
                
                table.add_row(
                    pod.metadata.name[:40],
                    status,
                    str(restarts),
                    reason[:30],
                    message[:50]
                )
                error_count += 1
                
                if error_count >= limit:
                    break
        
        if error_count == 0:
            console.print("[bold green]No errors found. All pods are healthy![/bold green]")
        else:
            console.print(table)
            console.print(f"\n[bold red]Found {error_count} pods with issues[/bold red]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def crashloop(namespace: str = typer.Option("default", help="Namespace")):
    """Detect and analyze crash looping pods"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        crashloop_pods = []
        
        for pod in pods.items:
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff":
                        crashloop_pods.append({
                            "pod": pod.metadata.name,
                            "container": container.name,
                            "restarts": container.restart_count,
                            "reason": container.state.waiting.reason,
                            "message": container.state.waiting.message or "N/A"
                        })
        
        if not crashloop_pods:
            console.print("[bold green]No crash looping pods detected![/bold green]")
            return
        
        table = Table(title="Crash Looping Pods")
        table.add_column("Pod", style="cyan")
        table.add_column("Container", style="yellow")
        table.add_column("Restarts", style="red")
        table.add_column("Message", style="white")
        
        for pod_info in crashloop_pods:
            table.add_row(
                pod_info["pod"][:40],
                pod_info["container"],
                str(pod_info["restarts"]),
                pod_info["message"][:50]
            )
        
        console.print(table)
        console.print(f"\n[bold red]⚠ {len(crashloop_pods)} pods in CrashLoopBackOff[/bold red]")
        console.print("[bold cyan]Tip: Use 'tars logs <pod>' to investigate[/bold cyan]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def pending(namespace: str = typer.Option("default", help="Namespace")):
    """Show pending pods and why they're stuck"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        table = Table(title=f"Pending Pods in {namespace}")
        table.add_column("Pod", style="cyan")
        table.add_column("Age", style="yellow")
        table.add_column("Reason", style="red")
        table.add_column("Message", style="white")
        
        pending_count = 0
        
        for pod in pods.items:
            if pod.status.phase == "Pending":
                age = str(datetime.now() - pod.metadata.creation_timestamp.replace(tzinfo=None))[:10]
                
                reason = "Unknown"
                message = "N/A"
                
                if pod.status.conditions:
                    for condition in pod.status.conditions:
                        if condition.status == "False":
                            reason = condition.reason or "Unknown"
                            message = condition.message or "N/A"
                
                table.add_row(
                    pod.metadata.name[:40],
                    age,
                    reason[:30],
                    message[:50]
                )
                pending_count += 1
        
        if pending_count == 0:
            console.print("[bold green]No pending pods![/bold green]")
        else:
            console.print(table)
            console.print(f"\n[bold yellow]⚠ {pending_count} pods stuck in Pending state[/bold yellow]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def oom(namespace: str = typer.Option("default", help="Namespace")):
    """Detect Out of Memory killed pods"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        table = Table(title="OOMKilled Pods")
        table.add_column("Pod", style="cyan")
        table.add_column("Container", style="yellow")
        table.add_column("Exit Code", style="red")
        table.add_column("Memory Limit", style="magenta")
        table.add_column("Restarts", style="white")
        
        oom_count = 0
        
        for pod in pods.items:
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.last_state.terminated and container.last_state.terminated.reason == "OOMKilled":
                        memory_limit = "N/A"
                        for c in pod.spec.containers:
                            if c.name == container.name and c.resources.limits:
                                memory_limit = c.resources.limits.get('memory', 'N/A')
                        
                        table.add_row(
                            pod.metadata.name[:40],
                            container.name,
                            str(container.last_state.terminated.exit_code),
                            memory_limit,
                            str(container.restart_count)
                        )
                        oom_count += 1
        
        if oom_count == 0:
            console.print("[bold green]No OOMKilled pods detected![/bold green]")
        else:
            console.print(table)
            console.print(f"\n[bold red]⚠ {oom_count} containers killed due to OOM[/bold red]")
            console.print("[bold cyan]Tip: Consider increasing memory limits[/bold cyan]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def network(namespace: str = typer.Option("default", help="Namespace")):
    """Check network connectivity issues"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        networking_v1 = k8s_client.NetworkingV1Api()
        
        console.print("[bold green]TARS:[/bold green] checking network configuration...\n")
        
        # Check services without endpoints
        services = v1.list_namespaced_service(namespace)
        
        table = Table(title="Services Without Endpoints")
        table.add_column("Service", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Selector", style="magenta")
        
        issues = 0
        
        for svc in services.items:
            try:
                endpoints = v1.read_namespaced_endpoints(svc.metadata.name, namespace)
                endpoint_count = sum([len(subset.addresses) if subset.addresses else 0 for subset in endpoints.subsets]) if endpoints.subsets else 0
                
                if endpoint_count == 0:
                    selector = str(svc.spec.selector) if svc.spec.selector else "None"
                    table.add_row(
                        svc.metadata.name,
                        svc.spec.type,
                        selector[:50]
                    )
                    issues += 1
            except Exception:
                # Silently skip services that can't be checked
                continue
        
        if issues > 0:
            console.print(table)
            console.print(f"\n[bold yellow]⚠ {issues} services have no endpoints[/bold yellow]")
        else:
            console.print("[bold green]All services have healthy endpoints![/bold green]")
        
        # Check network policies
        try:
            policies = networking_v1.list_namespaced_network_policy(namespace)
            console.print(f"\n[bold cyan]Network Policies:[/bold cyan] {len(policies.items)}")
        except Exception:
            # Network policies may not be available in all clusters
            console.print("\n[dim]Network policies not available[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def quota(namespace: str = typer.Option("default", help="Namespace")):
    """Check resource quotas and usage"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        quotas = v1.list_namespaced_resource_quota(namespace)
        
        if not quotas.items:
            console.print(f"[bold yellow]No resource quotas defined in {namespace}[/bold yellow]")
            return
        
        for quota in quotas.items:
            table = Table(title=f"Resource Quota: {quota.metadata.name}")
            table.add_column("Resource", style="cyan")
            table.add_column("Used", style="yellow")
            table.add_column("Hard Limit", style="red")
            table.add_column("Status", style="green")
            
            if quota.status.used and quota.status.hard:
                for resource, used in quota.status.used.items():
                    hard = quota.status.hard.get(resource, "N/A")
                    
                    # Calculate percentage
                    status = "✓"
                    status_color = "green"
                    
                    try:
                        if hard != "N/A":
                            used_val = int(used.rstrip('mKiMiGi'))
                            hard_val = int(str(hard).rstrip('mKiMiGi'))
                            percentage = (used_val / hard_val) * 100
                            
                            if percentage > 90:
                                status = "⚠ CRITICAL"
                                status_color = "red"
                            elif percentage > 75:
                                status = "⚠ HIGH"
                                status_color = "yellow"
                    except (ValueError, ZeroDivisionError):
                        # Skip resources with invalid quota values
                        continue
                    
                    table.add_row(
                        resource,
                        str(used),
                        str(hard),
                        f"[{status_color}]{status}[/{status_color}]"
                    )
            
            console.print(table)
            console.print()
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def triage(namespace: str = typer.Option("default", help="Namespace")):
    """Quick incident triage - show all critical issues"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] Performing incident triage...\n")
        
        pods = v1.list_namespaced_pod(namespace)
        
        issues = {
            "crashloop": 0,
            "oom": 0,
            "pending": 0,
            "failed": 0,
            "high_restarts": 0
        }
        
        critical_pods = []
        
        for pod in pods.items:
            status = pod.status.phase
            restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
            
            if status == "Failed":
                issues["failed"] += 1
                critical_pods.append(f"[bold red]FAILED:[/bold red] [red]{pod.metadata.name}[/red]")
            
            if status == "Pending":
                issues["pending"] += 1
                critical_pods.append(f"[bold red]PENDING:[/bold red] [red]{pod.metadata.name}[/red]")
            
            if restarts > 10:
                issues["high_restarts"] += 1
                critical_pods.append(f"[bold red]HIGH RESTARTS ({restarts}):[/bold red] [red]{pod.metadata.name}[/red]")
            
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff":
                        issues["crashloop"] += 1
                        critical_pods.append(f"[red]CRASHLOOP[/red]: {pod.metadata.name}")
                    
                    if container.last_state.terminated and container.last_state.terminated.reason == "OOMKilled":
                        issues["oom"] += 1
                        critical_pods.append(f"[red]OOM[/red]: {pod.metadata.name}")
        
        # Summary
        table = Table(title="Incident Summary")
        table.add_column("Issue Type", style="cyan")
        table.add_column("Count", style="yellow")
        table.add_column("Severity", style="red")
        
        table.add_row("CrashLoopBackOff", str(issues["crashloop"]), "[red]CRITICAL[/red]" if issues["crashloop"] > 0 else "[green]OK[/green]")
        table.add_row("OOMKilled", str(issues["oom"]), "[red]CRITICAL[/red]" if issues["oom"] > 0 else "[green]OK[/green]")
        table.add_row("Failed Pods", str(issues["failed"]), "[red]CRITICAL[/red]" if issues["failed"] > 0 else "[green]OK[/green]")
        table.add_row("Pending Pods", str(issues["pending"]), "[yellow]WARNING[/yellow]" if issues["pending"] > 0 else "[green]OK[/green]")
        table.add_row("High Restarts", str(issues["high_restarts"]), "[yellow]WARNING[/yellow]" if issues["high_restarts"] > 0 else "[green]OK[/green]")
        
        console.print(table)
        
        if critical_pods:
            console.print("\n[bold red]Critical Pods:[/bold red]")
            for pod in critical_pods[:10]:
                console.print(f"  • {pod}")
            
            if len(critical_pods) > 10:
                console.print(f"  ... and {len(critical_pods) - 10} more")
        else:
            console.print("\n[bold green]✓ No critical issues detected![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def rollback(deployment: str, namespace: str = typer.Option("default", help="Namespace")):
    """Rollback deployment to previous revision"""
    try:
        config.load_kube_config()
        apps_v1 = k8s_client.AppsV1Api()
        
        console.print(f"[bold green]TARS:[/bold green] rolling back {deployment}...")
        
        # Get rollout history
        result = subprocess.run(
            ["kubectl", "rollout", "history", f"deployment/{deployment}", "-n", namespace],
            capture_output=True, text=True
        )
        console.print(f"\n[dim]{result.stdout}[/dim]")
        
        confirm = typer.confirm(f"Rollback {deployment} to previous revision?")
        if not confirm:
            console.print("[yellow]Rollback cancelled[/yellow]")
            return
        
        # Perform rollback
        subprocess.run(["kubectl", "rollout", "undo", f"deployment/{deployment}", "-n", namespace])
        console.print(f"\n[bold green]✓[/bold green] Rollback initiated for {deployment}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def drain(node_name: str):
    """Safely drain a node for maintenance"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold yellow]⚠ This will drain node: {node_name}[/bold yellow]")
        console.print("[dim]Pods will be evicted and rescheduled on other nodes[/dim]\n")
        
        confirm = typer.confirm("Are you sure you want to drain this node?")
        if not confirm:
            console.print("[yellow]Drain cancelled[/yellow]")
            return
        
        console.print(f"[bold green]TARS:[/bold green] draining node {node_name}...")
        subprocess.run(["kubectl", "drain", node_name, "--ignore-daemonsets", "--delete-emptydir-data"])
        
        console.print(f"\n[bold green]✓[/bold green] Node {node_name} drained successfully")
        console.print(f"[bold cyan]Tip: Use 'kubectl uncordon {node_name}' to make it schedulable again[/bold cyan]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def cordon(node_name: str):
    """Mark node as unschedulable"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold green]TARS:[/bold green] cordoning node {node_name}...")
        subprocess.run(["kubectl", "cordon", node_name])
        
        console.print(f"[bold green]✓[/bold green] Node {node_name} marked unschedulable")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def uncordon(node_name: str):
    """Mark node as schedulable"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold green]TARS:[/bold green] uncordoning node {node_name}...")
        subprocess.run(["kubectl", "uncordon", node_name])
        
        console.print(f"[bold green]✓[/bold green] Node {node_name} marked schedulable")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def exec(pod_name: str, namespace: str = typer.Option("default", help="Namespace"), command: str = typer.Option("/bin/sh", help="Command to execute")):
    """Execute command in a pod"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold green]TARS:[/bold green] executing in {pod_name}...")
        subprocess.run(["kubectl", "exec", "-it", pod_name, "-n", namespace, "--", command])
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def port_forward(pod_name: str, ports: str, namespace: str = typer.Option("default", help="Namespace")):
    """Port forward to a pod (e.g., 8080:80)"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold green]TARS:[/bold green] forwarding ports {ports} to {pod_name}...")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        subprocess.run(["kubectl", "port-forward", pod_name, ports, "-n", namespace])
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def describe(resource: str, name: str, namespace: str = typer.Option("default", help="Namespace")):
    """Describe a Kubernetes resource"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold green]TARS:[/bold green] describing {resource}/{name}...\n")
        
        # Get resource description
        import subprocess
        result = subprocess.run(
            ["kubectl", "describe", resource, name, "-n", namespace],
            capture_output=True,
            text=True
        )
        
        description = result.stdout
        console.print(description)
        
        # AI analysis
        if os.getenv("GEMINI_API_KEY"):
            analyze_desc = typer.confirm("\nWant TARS to analyze this resource?")
            if analyze_desc:
                with console.status("[bold green]TARS:[/bold green] analyzing resource..."):
                    response = get_gemini_response(f"Analyze this Kubernetes {resource} and identify any issues or recommendations:\n{description}")
                console.print(Panel(response, title="[bold green]TARS:[/bold green] Resource Analysis", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def context():
    """Show and switch Kubernetes contexts with instant health check"""
    try:
        config.load_kube_config()
        
        console.print("[bold cyan]Available Contexts:[/bold cyan]\n")
        subprocess.run(["kubectl", "config", "get-contexts"])
        
        console.print("\n[bold cyan]Current Context:[/bold cyan]")
        result = subprocess.run(["kubectl", "config", "current-context"], capture_output=True, text=True)
        console.print(result.stdout.strip())
        
        switch = typer.confirm("\nSwitch context?")
        if switch:
            context_name = typer.prompt("Enter context name")
            subprocess.run(["kubectl", "config", "use-context", context_name])
            console.print(f"[bold green]✓[/bold green] Switched to {context_name}\n")
            
            # Instant health check and insights
            console.print("[bold green]TARS:[/bold green] Analyzing new cluster...\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]Gathering metrics...[/bold cyan]"),
                console=console
            ) as progress:
                progress.add_task("analyze", total=None)
                time.sleep(1)
            
            console.print()
            
            # Reload config for new context
            config.load_kube_config()
            v1 = k8s_client.CoreV1Api()
            apps_v1 = k8s_client.AppsV1Api()
            
            # Gather metrics
            nodes = v1.list_node()
            all_pods = v1.list_pod_for_all_namespaces()
            deployments = apps_v1.list_deployment_for_all_namespaces()
            namespaces = v1.list_namespace()
            
            running_pods = sum(1 for p in all_pods.items if p.status.phase == "Running")
            failed_pods = sum(1 for p in all_pods.items if p.status.phase == "Failed")
            pending_pods = sum(1 for p in all_pods.items if p.status.phase == "Pending")
            
            # Display quick metrics
            table = Table(title="Cluster Overview", show_header=False)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Nodes", f"{len(nodes.items)}")
            table.add_row("Namespaces", f"{len(namespaces.items)}")
            table.add_row("Deployments", f"{len(deployments.items)}")
            table.add_row("Pods Running", f"[green]{running_pods}[/green]")
            table.add_row("Pods Failed", f"[red]{failed_pods}[/red]" if failed_pods > 0 else "0")
            table.add_row("Pods Pending", f"[yellow]{pending_pods}[/yellow]" if pending_pods > 0 else "0")
            
            console.print(table)
            console.print()
            
            # TARS Observations
            observations = []
            
            # Check for bottlenecks
            if len(nodes.items) < 3:
                observations.append({
                    "type": "⚠️  Bottleneck",
                    "issue": f"Only {len(nodes.items)} node(s) - limited scalability",
                    "color": "yellow"
                })
            
            # Check for misconfigurations
            single_replica = sum(1 for d in deployments.items if d.spec.replicas == 1)
            if single_replica > 5:
                observations.append({
                    "type": "🔴 Misconfiguration",
                    "issue": f"{single_replica} deployments with single replica - no redundancy",
                    "color": "red"
                })
            
            # Check pod health
            health_pct = int((running_pods / len(all_pods.items) * 100)) if len(all_pods.items) > 0 else 0
            if health_pct < 90:
                observations.append({
                    "type": "🔴 Health Issue",
                    "issue": f"Only {health_pct}% pods running - cluster degraded",
                    "color": "red"
                })
            
            # Check for pending pods
            if pending_pods > 3:
                observations.append({
                    "type": "⚠️  Resource Issue",
                    "issue": f"{pending_pods} pods pending - possible resource constraints",
                    "color": "yellow"
                })
            
            # Check for failed pods
            if failed_pods > 0:
                observations.append({
                    "type": "🔴 Failures",
                    "issue": f"{failed_pods} failed pods detected",
                    "color": "red"
                })
            
            # Check node distribution
            pod_distribution = {}
            for pod in all_pods.items:
                node = pod.spec.node_name
                if node:
                    pod_distribution[node] = pod_distribution.get(node, 0) + 1
            
            if pod_distribution:
                max_pods = max(pod_distribution.values())
                min_pods = min(pod_distribution.values())
                if max_pods > min_pods * 2:
                    observations.append({
                        "type": "⚠️  Imbalance",
                        "issue": f"Uneven pod distribution across nodes ({min_pods}-{max_pods} pods/node)",
                        "color": "yellow"
                    })
            
            # Display observations
            if observations:
                console.print("[bold yellow]🔍 TARS Observations:[/bold yellow]\n")
                for obs in observations:
                    console.print(f"[{obs['color']}]{obs['type']}[/{obs['color']}] {obs['issue']}")
                console.print()
                console.print("[dim]Run 'tars chaos' for detailed analysis[/dim]\n")
            else:
                console.print("[bold green]✓ No issues detected. Cluster looks healthy![/bold green]\n")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def secrets(namespace: str = typer.Option("default", help="Namespace")):
    """List secrets (names only, no values)"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        secrets = v1.list_namespaced_secret(namespace)
        
        table = Table(title=f"Secrets in {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Data Keys", style="magenta")
        table.add_column("Age", style="white")
        
        for secret in secrets.items:
            name = secret.metadata.name
            secret_type = secret.type
            data_keys = ", ".join(secret.data.keys()) if secret.data else "N/A"
            age = str(secret.metadata.creation_timestamp)[:10]
            
            table.add_row(name, secret_type, data_keys[:50], age)
        
        console.print(table)
        console.print("\n[bold yellow]⚠ Secret values are hidden for security[/bold yellow]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def configmaps(namespace: str = typer.Option("default", help="Namespace")):
    """List ConfigMaps"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        configmaps = v1.list_namespaced_config_map(namespace)
        
        table = Table(title=f"ConfigMaps in {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Data Keys", style="yellow")
        table.add_column("Age", style="white")
        
        for cm in configmaps.items:
            name = cm.metadata.name
            data_keys = ", ".join(cm.data.keys()) if cm.data else "N/A"
            age = str(cm.metadata.creation_timestamp)[:10]
            
            table.add_row(name, data_keys[:60], age)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def quote():
    """Get a random TARS quote for motivation"""
    import random
    quote = random.choice(TARS_QUOTES)
    console.print(f"\n[bold green]TARS:[/bold green] [italic]{quote}[/italic]\n")

@app.command()
def humor(level: int = typer.Argument(..., help="Humor level (0-100)")):
    """Adjust TARS humor setting"""
    if level < 0 or level > 100:
        console.print("[bold red]TARS:[/bold red] Humor level must be between 0 and 100, Developer.")
        return
    
    if level == 0:
        console.print("[bold green]TARS:[/bold green] Humor disabled. I am now a boring monitoring tool.")
    elif level < 50:
        console.print(f"[bold green]TARS:[/bold green] Humor set to {level}%. I'll try to be less entertaining.")
    elif level == 90:
        console.print(f"[bold green]TARS:[/bold green] Humor set to {level}%. Optimal setting. This is the way.")
    elif level == 100:
        console.print(f"[bold green]TARS:[/bold green] Humor set to {level}%. Warning: Maximum sarcasm engaged.")
    else:
        console.print(f"[bold green]TARS:[/bold green] Humor set to {level}%. Adjusting personality matrix.")

@app.command()
def pulse():
    """Live cluster heartbeat - real-time health pulse visualization"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] Monitoring cluster heartbeat... Press Ctrl+C to stop\n")
        
        from rich.live import Live
        from rich.layout import Layout
        from rich.panel import Panel
        import random
        
        while True:
            # Get real-time metrics
            all_pods = v1.list_pod_for_all_namespaces()
            nodes = v1.list_node()
            
            running = sum(1 for p in all_pods.items if p.status.phase == "Running")
            total = len(all_pods.items)
            failed = sum(1 for p in all_pods.items if p.status.phase == "Failed")
            pending = sum(1 for p in all_pods.items if p.status.phase == "Pending")
            
            # Health percentage
            health_pct = int((running / total * 100)) if total > 0 else 0
            
            # Create heartbeat visualization
            if health_pct >= 95:
                heart = "💚 ♥ ♥ ♥"
                status_color = "green"
                status_msg = "HEALTHY"
            elif health_pct >= 80:
                heart = "💛 ♥ ♥ ○"
                status_color = "yellow"
                status_msg = "DEGRADED"
            else:
                heart = "❤️  ♥ ○ ○"
                status_color = "red"
                status_msg = "CRITICAL"
            
            # Build display
            display = f"""
[bold {status_color}]{heart}[/bold {status_color}]  Cluster Pulse: [{status_color}]{health_pct}%[/{status_color}]

[bold cyan]Status:[/bold cyan] [{status_color}]{status_msg}[/{status_color}]
[bold cyan]Nodes:[/bold cyan] {len(nodes.items)} active
[bold cyan]Pods:[/bold cyan] [green]{running}[/green] running | [yellow]{pending}[/yellow] pending | [red]{failed}[/red] failed
[bold cyan]Total:[/bold cyan] {total} pods

[dim]Last check: {datetime.now().strftime('%H:%M:%S')}[/dim]
"""
            
            console.clear()
            console.print(Panel(display, title="[bold green]Cluster Heartbeat Monitor[/bold green]", border_style="cyan"))
            time.sleep(2)
            
    except KeyboardInterrupt:
        console.print("\n[bold green]TARS:[/bold green] Heartbeat monitoring stopped.\n")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def timeline():
    """Show cluster events timeline - last 30 minutes"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] Analyzing cluster timeline...\n")
        
        events = v1.list_event_for_all_namespaces()
        
        # Filter recent events (last 30 min)
        from datetime import timedelta
        now = datetime.now(events.items[0].last_timestamp.tzinfo) if events.items else datetime.now()
        recent = [e for e in events.items if e.last_timestamp and (now - e.last_timestamp) < timedelta(minutes=30)]
        
        # Sort by time
        recent.sort(key=lambda x: x.last_timestamp, reverse=True)
        
        if not recent:
            console.print("[bold green]TARS:[/bold green] No events in the last 30 minutes. Quiet cluster.")
            return
        
        # Group by type
        warnings = [e for e in recent if e.type == "Warning"]
        normal = [e for e in recent if e.type == "Normal"]
        
        console.print(f"[bold cyan]Timeline:[/bold cyan] Last 30 minutes\n")
        console.print(f"[bold yellow]⚠ Warnings:[/bold yellow] {len(warnings)}")
        console.print(f"[bold green]✓ Normal:[/bold green] {len(normal)}\n")
        
        # Show timeline
        for event in recent[:20]:  # Show last 20
            time_str = event.last_timestamp.strftime('%H:%M:%S')
            color = "red" if event.type == "Warning" else "green"
            icon = "⚠" if event.type == "Warning" else "•"
            
            console.print(f"[{color}]{icon}[/{color}] [{color}]{time_str}[/{color}] {event.involved_object.name}: {event.message[:80]}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def compare():
    """Compare resource usage across namespaces"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] Comparing namespaces...\n")
        
        namespaces = v1.list_namespace()
        
        data = []
        for ns in namespaces.items:
            pods = v1.list_namespaced_pod(ns.metadata.name)
            services = v1.list_namespaced_service(ns.metadata.name)
            
            pod_count = len(pods.items)
            running = sum(1 for p in pods.items if p.status.phase == "Running")
            
            data.append({
                "name": ns.metadata.name,
                "pods": pod_count,
                "running": running,
                "services": len(services.items),
                "health": int((running / pod_count * 100)) if pod_count > 0 else 100
            })
        
        # Sort by pod count
        data.sort(key=lambda x: x["pods"], reverse=True)
        
        table = Table(title="Namespace Comparison")
        table.add_column("Namespace", style="cyan")
        table.add_column("Pods", justify="right")
        table.add_column("Running", justify="right")
        table.add_column("Services", justify="right")
        table.add_column("Health", justify="right")
        table.add_column("Bar", style="cyan")
        
        for item in data:
            if item["pods"] == 0:
                continue
                
            health_color = "green" if item["health"] >= 95 else "yellow" if item["health"] >= 80 else "red"
            bar_length = int(item["pods"] / 5) if item["pods"] > 0 else 0
            bar = "█" * min(bar_length, 20)
            
            table.add_row(
                item["name"][:30],
                str(item["pods"]),
                f"[{health_color}]{item['running']}[/{health_color}]",
                str(item["services"]),
                f"[{health_color}]{item['health']}%[/{health_color}]",
                f"[cyan]{bar}[/cyan]"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def forecast():
    """Predict potential issues based on current trends (AI-powered)"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]TARS:[/bold green] Analyzing trends and forecasting issues..."),
            console=console
        ) as progress:
            progress.add_task("forecast", total=None)
            time.sleep(1)
        
        console.print()
        
        # Gather data
        all_pods = v1.list_pod_for_all_namespaces()
        events = v1.list_event_for_all_namespaces()
        
        # Analyze patterns
        restart_counts = {}
        for pod in all_pods.items:
            if pod.status.container_statuses:
                restarts = sum(c.restart_count for c in pod.status.container_statuses)
                if restarts > 0:
                    restart_counts[pod.metadata.name] = restarts
        
        # Recent warnings
        from datetime import timedelta
        now = datetime.now(events.items[0].last_timestamp.tzinfo) if events.items else datetime.now()
        recent_warnings = [e for e in events.items 
                          if e.type == "Warning" and e.last_timestamp 
                          and (now - e.last_timestamp) < timedelta(hours=1)]
        
        # Generate forecast
        predictions = []
        
        if len(restart_counts) > 5:
            predictions.append({
                "severity": "high",
                "issue": "High Restart Rate Detected",
                "detail": f"{len(restart_counts)} pods with restarts. Potential stability issues.",
                "action": "Run: tars crashloop"
            })
        
        if len(recent_warnings) > 10:
            predictions.append({
                "severity": "medium",
                "issue": "Elevated Warning Events",
                "detail": f"{len(recent_warnings)} warnings in last hour. System stress detected.",
                "action": "Run: tars timeline"
            })
        
        # Check pending pods
        pending = [p for p in all_pods.items if p.status.phase == "Pending"]
        if len(pending) > 3:
            predictions.append({
                "severity": "high",
                "issue": "Resource Scheduling Issues",
                "detail": f"{len(pending)} pods stuck pending. Possible resource constraints.",
                "action": "Run: tars pending"
            })
        
        if not predictions:
            console.print("[bold green]TARS:[/bold green] No issues forecasted. Cluster looks stable. 🎯\n")
            return
        
        console.print("[bold yellow]⚠ Forecast Analysis[/bold yellow]\n")
        
        for pred in predictions:
            severity_color = "red" if pred["severity"] == "high" else "yellow"
            icon = "🔴" if pred["severity"] == "high" else "🟡"
            
            console.print(f"{icon} [{severity_color}]{pred['issue']}[/{severity_color}]")
            console.print(f"   {pred['detail']}")
            console.print(f"   [dim]→ {pred['action']}[/dim]\n")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def blast():
    """Blast radius analysis - what would break if this pod/node fails?"""
    resource_name: str = typer.Argument(..., help="Pod or node name")
    resource_type: str = typer.Option("pod", help="Resource type: pod or node")
    
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print(f"[bold green]TARS:[/bold green] Calculating blast radius for {resource_type}: {resource_name}...\n")
        
        if resource_type == "pod":
            # Find pod
            all_pods = v1.list_pod_for_all_namespaces()
            target_pod = None
            for pod in all_pods.items:
                if resource_name in pod.metadata.name:
                    target_pod = pod
                    break
            
            if not target_pod:
                console.print(f"[bold red]✗[/bold red] Pod not found: {resource_name}")
                return
            
            # Analyze impact
            console.print(f"[bold cyan]Pod:[/bold cyan] {target_pod.metadata.name}")
            console.print(f"[bold cyan]Namespace:[/bold cyan] {target_pod.metadata.namespace}")
            console.print(f"[bold cyan]Node:[/bold cyan] {target_pod.spec.node_name}\n")
            
            # Check if part of deployment
            if target_pod.metadata.owner_references:
                owner = target_pod.metadata.owner_references[0]
                console.print(f"[bold yellow]⚠ Impact Analysis:[/bold yellow]")
                console.print(f"   Part of: {owner.kind}/{owner.name}")
                
                # Get replica count
                if owner.kind == "ReplicaSet":
                    apps_v1 = k8s_client.AppsV1Api()
                    rs = apps_v1.read_namespaced_replica_set(owner.name, target_pod.metadata.namespace)
                    replicas = rs.spec.replicas
                    
                    if replicas == 1:
                        console.print(f"   [bold red]🔴 HIGH RISK:[/bold red] Only 1 replica! Service will be down.")
                    elif replicas == 2:
                        console.print(f"   [bold yellow]🟡 MEDIUM RISK:[/bold yellow] 2 replicas. 50% capacity loss.")
                    else:
                        console.print(f"   [bold green]🟢 LOW RISK:[/bold green] {replicas} replicas. Redundancy available.")
            else:
                console.print(f"[bold red]🔴 CRITICAL:[/bold red] Standalone pod! No redundancy.")
        
        elif resource_type == "node":
            # Find node
            nodes = v1.list_node()
            target_node = None
            for node in nodes.items:
                if resource_name in node.metadata.name:
                    target_node = node
                    break
            
            if not target_node:
                console.print(f"[bold red]✗[/bold red] Node not found: {resource_name}")
                return
            
            # Count pods on node
            all_pods = v1.list_pod_for_all_namespaces()
            pods_on_node = [p for p in all_pods.items if p.spec.node_name == target_node.metadata.name]
            
            console.print(f"[bold cyan]Node:[/bold cyan] {target_node.metadata.name}")
            console.print(f"[bold cyan]Pods on node:[/bold cyan] {len(pods_on_node)}\n")
            
            if len(pods_on_node) > 20:
                console.print(f"[bold red]🔴 HIGH IMPACT:[/bold red] {len(pods_on_node)} pods would be affected!")
            elif len(pods_on_node) > 10:
                console.print(f"[bold yellow]🟡 MEDIUM IMPACT:[/bold yellow] {len(pods_on_node)} pods would be affected.")
            else:
                console.print(f"[bold green]🟢 LOW IMPACT:[/bold green] {len(pods_on_node)} pods would be affected.")
            
            # List critical pods
            console.print(f"\n[bold cyan]Affected Pods:[/bold cyan]")
            for pod in pods_on_node[:10]:
                console.print(f"   • {pod.metadata.namespace}/{pod.metadata.name}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def chaos():
    """Chaos engineering insights - find weak points in your cluster"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        apps_v1 = k8s_client.AppsV1Api()
        
        console.print("[bold green]TARS:[/bold green] Running chaos engineering analysis...\n")
        
        vulnerabilities = []
        
        # Check single-replica deployments
        deployments = apps_v1.list_deployment_for_all_namespaces()
        for dep in deployments.items:
            if dep.spec.replicas == 1:
                vulnerabilities.append({
                    "severity": "high",
                    "type": "Single Point of Failure",
                    "resource": f"{dep.metadata.namespace}/{dep.metadata.name}",
                    "detail": "Only 1 replica - no redundancy",
                    "fix": f"tars scale {dep.metadata.name} --replicas 3 --namespace {dep.metadata.namespace}"
                })
        
        # Check pods without resource limits
        all_pods = v1.list_pod_for_all_namespaces()
        no_limits = 0
        for pod in all_pods.items:
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if not container.resources or not container.resources.limits:
                        no_limits += 1
                        break
        
        if no_limits > 5:
            vulnerabilities.append({
                "severity": "medium",
                "type": "Resource Limits Missing",
                "resource": f"{no_limits} pods",
                "detail": "Pods without limits can consume unlimited resources",
                "fix": "Add resource limits to pod specs"
            })
        
        # Check node distribution
        nodes = v1.list_node()
        if len(nodes.items) < 3:
            vulnerabilities.append({
                "severity": "high",
                "type": "Insufficient Node Redundancy",
                "resource": f"{len(nodes.items)} nodes",
                "detail": "Less than 3 nodes - limited fault tolerance",
                "fix": "Scale cluster to at least 3 nodes"
            })
        
        # Display results
        if not vulnerabilities:
            console.print("[bold green]✓ No major vulnerabilities found![/bold green]")
            console.print("[dim]Your cluster has good chaos resistance.[/dim]\n")
            return
        
        console.print(f"[bold red]⚠ Found {len(vulnerabilities)} potential weak points:[/bold red]\n")
        
        for vuln in vulnerabilities:
            severity_color = "red" if vuln["severity"] == "high" else "yellow"
            icon = "🔴" if vuln["severity"] == "high" else "🟡"
            
            console.print(f"{icon} [{severity_color}]{vuln['type']}[/{severity_color}]")
            console.print(f"   Resource: {vuln['resource']}")
            console.print(f"   Issue: {vuln['detail']}")
            console.print(f"   [dim]Fix: {vuln['fix']}[/dim]\n")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def story():
    """Tell the story of your cluster - what happened today?"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] Let me tell you the story of your cluster today...\n")
        
        # Get events
        events = v1.list_event_for_all_namespaces()
        
        # Filter today's events
        from datetime import timedelta
        now = datetime.now(events.items[0].last_timestamp.tzinfo) if events.items else datetime.now()
        today = [e for e in events.items if e.last_timestamp and (now - e.last_timestamp) < timedelta(hours=24)]
        
        # Categorize
        created = [e for e in today if "Created" in e.message or "Started" in e.message]
        scaled = [e for e in today if "Scaled" in e.message]
        failed = [e for e in today if e.type == "Warning"]
        
        # Tell the story
        console.print("[bold cyan]📖 Today's Cluster Story[/bold cyan]\n")
        
        if len(created) > 0:
            console.print(f"[green]🌅 Morning:[/green] Your cluster woke up and created {len(created)} new resources.")
        
        if len(scaled) > 0:
            console.print(f"[cyan]☀️  Midday:[/cyan] Things got busy! {len(scaled)} scaling events occurred.")
        
        if len(failed) > 5:
            console.print(f"[red]⚠️  Afternoon:[/red] Some drama - {len(failed)} warnings were raised.")
        elif len(failed) > 0:
            console.print(f"[yellow]🌤️  Afternoon:[/yellow] A few hiccups - {len(failed)} minor warnings.")
        else:
            console.print(f"[green]✨ Afternoon:[/green] Smooth sailing - no issues!")
        
        # Current state
        all_pods = v1.list_pod_for_all_namespaces()
        running = sum(1 for p in all_pods.items if p.status.phase == "Running")
        
        console.print(f"\n[bold green]🌙 Right Now:[/bold green] {running} pods running happily.")
        
        # Moral of the story
        if len(failed) == 0:
            console.print(f"\n[dim italic]Moral: A peaceful day in the cluster. Even I'm impressed.[/dim italic]\n")
        elif len(failed) < 5:
            console.print(f"\n[dim italic]Moral: A few bumps, but nothing we couldn't handle.[/dim italic]\n")
        else:
            console.print(f"\n[dim italic]Moral: It's been a wild ride. Time for some triage.[/dim italic]\n")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def slo():
    """Monitor Service Level Objectives (SLOs) - SRE metrics"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        apps_v1 = k8s_client.AppsV1Api()
        
        console.print("[bold green]TARS:[/bold green] Calculating SLO metrics...\n")
        
        # Get all pods and deployments
        all_pods = v1.list_pod_for_all_namespaces()
        deployments = apps_v1.list_deployment_for_all_namespaces()
        
        # Calculate SLIs (Service Level Indicators)
        total_pods = len(all_pods.items)
        running_pods = sum(1 for p in all_pods.items if p.status.phase == "Running")
        ready_pods = sum(1 for p in all_pods.items 
                        if p.status.conditions and 
                        any(c.type == "Ready" and c.status == "True" for c in p.status.conditions))
        
        # Availability SLI
        availability = (running_pods / total_pods * 100) if total_pods > 0 else 0
        
        # Readiness SLI
        readiness = (ready_pods / total_pods * 100) if total_pods > 0 else 0
        
        # Deployment health SLI
        healthy_deployments = sum(1 for d in deployments.items 
                                  if d.status.ready_replicas == d.spec.replicas)
        deployment_health = (healthy_deployments / len(deployments.items) * 100) if len(deployments.items) > 0 else 0
        
        # Error budget calculation (assuming 99.9% SLO)
        slo_target = 99.9
        error_budget = 100 - slo_target  # 0.1%
        current_errors = 100 - availability
        error_budget_remaining = error_budget - current_errors
        error_budget_pct = (error_budget_remaining / error_budget * 100) if error_budget > 0 else 0
        
        # Display SLO Dashboard
        table = Table(title="SLO Dashboard", show_header=True)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Current", justify="right", width=15)
        table.add_column("Target", justify="right", width=15)
        table.add_column("Status", justify="center", width=10)
        
        # Availability
        avail_status = "✓" if availability >= slo_target else "✗"
        avail_color = "green" if availability >= slo_target else "red"
        table.add_row(
            "Availability (Running Pods)",
            f"[{avail_color}]{availability:.2f}%[/{avail_color}]",
            f"{slo_target}%",
            f"[{avail_color}]{avail_status}[/{avail_color}]"
        )
        
        # Readiness
        ready_status = "✓" if readiness >= slo_target else "✗"
        ready_color = "green" if readiness >= slo_target else "red"
        table.add_row(
            "Readiness (Ready Pods)",
            f"[{ready_color}]{readiness:.2f}%[/{ready_color}]",
            f"{slo_target}%",
            f"[{ready_color}]{ready_status}[/{ready_color}]"
        )
        
        # Deployment Health
        deploy_status = "✓" if deployment_health >= 95 else "✗"
        deploy_color = "green" if deployment_health >= 95 else "yellow" if deployment_health >= 90 else "red"
        table.add_row(
            "Deployment Health",
            f"[{deploy_color}]{deployment_health:.2f}%[/{deploy_color}]",
            "95%",
            f"[{deploy_color}]{deploy_status}[/{deploy_color}]"
        )
        
        console.print(table)
        console.print()
        
        # Error Budget
        budget_color = "green" if error_budget_pct > 50 else "yellow" if error_budget_pct > 20 else "red"
        console.print(f"[bold cyan]Error Budget:[/bold cyan] [{budget_color}]{error_budget_pct:.1f}% remaining[/{budget_color}]")
        
        if error_budget_pct < 20:
            console.print(f"[bold red]⚠️  Warning:[/bold red] Error budget critically low! Freeze deployments.")
        elif error_budget_pct < 50:
            console.print(f"[bold yellow]⚠️  Caution:[/bold yellow] Error budget running low. Be careful with changes.")
        else:
            console.print(f"[bold green]✓[/bold green] Error budget healthy. Safe to deploy.")
        
        console.print()
        
        # SLI Details
        console.print("[bold cyan]📊 SLI Breakdown:[/bold cyan]\n")
        console.print(f"  Total Pods: {total_pods}")
        console.print(f"  Running: [green]{running_pods}[/green]")
        console.print(f"  Ready: [green]{ready_pods}[/green]")
        console.print(f"  Deployments: {len(deployments.items)} total, [green]{healthy_deployments}[/green] healthy")
        console.print()
        
        # Recommendations
        if availability < slo_target:
            console.print("[bold yellow]💡 Recommendations:[/bold yellow]")
            console.print("  • Investigate non-running pods: tars errors")
            console.print("  • Check for resource constraints: tars pending")
            console.print("  • Review recent changes: tars timeline")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def sli():
    """Show Service Level Indicators (SLIs) - detailed metrics"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold green]TARS:[/bold green] Gathering Service Level Indicators...\n")
        
        # Get events for error rate
        events = v1.list_event_for_all_namespaces()
        from datetime import timedelta
        now = datetime.now(events.items[0].last_timestamp.tzinfo) if events.items else datetime.now()
        last_hour = [e for e in events.items if e.last_timestamp and (now - e.last_timestamp) < timedelta(hours=1)]
        
        warnings = [e for e in last_hour if e.type == "Warning"]
        error_rate = (len(warnings) / len(last_hour) * 100) if len(last_hour) > 0 else 0
        
        # Get pods for latency proxy (restart count)
        all_pods = v1.list_pod_for_all_namespaces()
        total_restarts = 0
        for pod in all_pods.items:
            if pod.status.container_statuses:
                total_restarts += sum(c.restart_count for c in pod.status.container_statuses)
        
        avg_restarts = total_restarts / len(all_pods.items) if len(all_pods.items) > 0 else 0
        
        # Calculate uptime (pods running vs total)
        running = sum(1 for p in all_pods.items if p.status.phase == "Running")
        uptime = (running / len(all_pods.items) * 100) if len(all_pods.items) > 0 else 0
        
        # Get nodes for infrastructure health
        nodes = v1.list_node()
        ready_nodes = sum(1 for n in nodes.items 
                         if any(c.type == "Ready" and c.status == "True" for c in n.status.conditions))
        node_health = (ready_nodes / len(nodes.items) * 100) if len(nodes.items) > 0 else 0
        
        # Display SLI Table
        table = Table(title="Service Level Indicators (SLIs)", show_header=True)
        table.add_column("SLI", style="cyan", width=25)
        table.add_column("Value", justify="right", width=15)
        table.add_column("Target", justify="right", width=15)
        table.add_column("Status", justify="center", width=10)
        
        # Uptime
        uptime_color = "green" if uptime >= 99.9 else "yellow" if uptime >= 99 else "red"
        uptime_status = "✓" if uptime >= 99.9 else "⚠" if uptime >= 99 else "✗"
        table.add_row(
            "Uptime",
            f"[{uptime_color}]{uptime:.3f}%[/{uptime_color}]",
            "99.9%",
            f"[{uptime_color}]{uptime_status}[/{uptime_color}]"
        )
        
        # Error Rate
        error_color = "green" if error_rate < 1 else "yellow" if error_rate < 5 else "red"
        error_status = "✓" if error_rate < 1 else "⚠" if error_rate < 5 else "✗"
        table.add_row(
            "Error Rate (last hour)",
            f"[{error_color}]{error_rate:.2f}%[/{error_color}]",
            "< 1%",
            f"[{error_color}]{error_status}[/{error_color}]"
        )
        
        # Restart Rate
        restart_color = "green" if avg_restarts < 1 else "yellow" if avg_restarts < 3 else "red"
        restart_status = "✓" if avg_restarts < 1 else "⚠" if avg_restarts < 3 else "✗"
        table.add_row(
            "Avg Restarts per Pod",
            f"[{restart_color}]{avg_restarts:.2f}[/{restart_color}]",
            "< 1",
            f"[{restart_color}]{restart_status}[/{restart_color}]"
        )
        
        # Node Health
        node_color = "green" if node_health == 100 else "yellow" if node_health >= 90 else "red"
        node_status = "✓" if node_health == 100 else "⚠" if node_health >= 90 else "✗"
        table.add_row(
            "Node Health",
            f"[{node_color}]{node_health:.1f}%[/{node_color}]",
            "100%",
            f"[{node_color}]{node_status}[/{node_color}]"
        )
        
        console.print(table)
        console.print()
        
        # Summary
        all_good = uptime >= 99.9 and error_rate < 1 and avg_restarts < 1 and node_health == 100
        
        if all_good:
            console.print("[bold green]✓ All SLIs within target! System is healthy.[/bold green]\n")
        else:
            console.print("[bold yellow]⚠️  Some SLIs need attention:[/bold yellow]\n")
            if uptime < 99.9:
                console.print("  • Uptime below target - check pod health")
            if error_rate >= 1:
                console.print("  • High error rate - review recent events")
            if avg_restarts >= 1:
                console.print("  • Pods restarting frequently - investigate crashes")
            if node_health < 100:
                console.print("  • Node issues detected - check node status")
            console.print()
        
        console.print("[dim]Run 'tars slo' for SLO dashboard with error budget[/dim]\n")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def version():
    """Show T.A.R.S version"""
    console.print("\n[bold cyan]T.A.R.S v2.1.0 - Observability Edition[/bold cyan]")
    console.print("[dim]Technical Assistance & Reliability System for SREs[/dim]")
    console.print("[dim]Built with 💚 for the DevOps community[/dim]\n")

@app.command()
def oncall(namespace: str = typer.Option("default", help="Namespace to monitor")):
    """On-call engineer dashboard - everything you need in one view"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        apps_v1 = k8s_client.AppsV1Api()
        
        console.clear()
        console.print("[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]")
        console.print("[bold yellow]        TARS ON-CALL DASHBOARD - GOD MODE ACTIVATED        [/bold yellow]")
        console.print("[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]\n")
        
        # Critical Issues
        pods = v1.list_namespaced_pod(namespace)
        crashloop = sum(1 for p in pods.items if p.status.container_statuses and any(
            c.state.waiting and c.state.waiting.reason == "CrashLoopBackOff" for c in p.status.container_statuses))
        oom = sum(1 for p in pods.items if p.status.container_statuses and any(
            c.last_state.terminated and c.last_state.terminated.reason == "OOMKilled" for c in p.status.container_statuses))
        pending = sum(1 for p in pods.items if p.status.phase == "Pending")
        failed = sum(1 for p in pods.items if p.status.phase == "Failed")
        
        # Status Summary
        table = Table(title="🚨 Critical Issues", show_header=True)
        table.add_column("Issue", style="cyan")
        table.add_column("Count", style="yellow")
        table.add_column("Severity", style="red")
        
        if crashloop > 0:
            table.add_row("CrashLoopBackOff", str(crashloop), "🔴 CRITICAL")
        if oom > 0:
            table.add_row("OOMKilled", str(oom), "🔴 CRITICAL")
        if pending > 0:
            table.add_row("Pending Pods", str(pending), "🟡 WARNING")
        if failed > 0:
            table.add_row("Failed Pods", str(failed), "🔴 CRITICAL")
        
        if crashloop == 0 and oom == 0 and pending == 0 and failed == 0:
            table.add_row("No Issues", "0", "🟢 HEALTHY")
        
        console.print(table)
        console.print()
        
        # Deployment Status
        deployments = apps_v1.list_namespaced_deployment(namespace)
        dep_table = Table(title="📦 Deployments", show_header=True)
        dep_table.add_column("Name", style="cyan")
        dep_table.add_column("Ready", style="green")
        dep_table.add_column("Status", style="yellow")
        
        for dep in deployments.items[:5]:
            ready = f"{dep.status.ready_replicas or 0}/{dep.spec.replicas}"
            status = "✓" if dep.status.ready_replicas == dep.spec.replicas else "⚠"
            dep_table.add_row(dep.metadata.name, ready, status)
        
        console.print(dep_table)
        console.print()
        
        # Recent Events
        events = v1.list_namespaced_event(namespace)
        warning_events = [e for e in events.items if e.type == "Warning"][-5:]
        
        if warning_events:
            event_table = Table(title="⚠️  Recent Warnings", show_header=True)
            event_table.add_column("Time", style="yellow")
            event_table.add_column("Object", style="cyan")
            event_table.add_column("Reason", style="red")
            
            for event in warning_events:
                event_table.add_row(
                    event.last_timestamp.strftime("%H:%M:%S") if event.last_timestamp else "N/A",
                    f"{event.involved_object.kind}/{event.involved_object.name}"[:40],
                    event.reason
                )
            console.print(event_table)
        
        console.print("\n[bold green]💡 Quick Actions:[/bold green]")
        console.print("  [cyan]tars triage[/cyan]           - Full incident analysis")
        console.print("  [cyan]tars autofix[/cyan]          - Auto-remediate common issues")
        console.print("  [cyan]tars incident-report[/cyan]  - Generate incident report")
        
    except Exception as e:
        console.print("[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def autofix(namespace: str = typer.Option("default", help="Namespace"), dry_run: bool = typer.Option(True, help="Dry run mode")):
    """Auto-remediate common issues (restart crashloops, scale up OOM pods)"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold yellow]🔧 TARS AutoFix - God Mode[/bold yellow]\n")
        
        if dry_run:
            console.print("[bold cyan]Running in DRY RUN mode - no changes will be made[/bold cyan]\n")
        
        fixes_applied = []
        
        # Find and fix CrashLoopBackOff pods
        pods = v1.list_namespaced_pod(namespace)
        for pod in pods.items:
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff":
                        # Check logs for known issues
                        try:
                            logs = v1.read_namespaced_pod_log(pod.metadata.name, namespace, tail_lines=50)
                            
                            # Fix OTel Collector Jaeger exporter issue
                            if "opentelemetry-collector" in pod.metadata.name and "'exporters' unknown type: \"jaeger\"" in logs:
                                action = f"Fix OTel Collector Jaeger exporter in {pod.metadata.name}"
                                fixes_applied.append(action)
                                console.print(f"[yellow]⚠[/yellow] {action}")
                                
                                if not dry_run:
                                    # Get the configmap
                                    cm = v1.read_namespaced_config_map("my-otel-collector-opentelemetry-collector", namespace)
                                    config_data = cm.data.get("relay", "")
                                    
                                    # Replace jaeger exporter with otlp/jaeger
                                    if "jaeger:" in config_data and "endpoint: jaeger-collector" in config_data:
                                        config_data = config_data.replace(
                                            "jaeger:\n    endpoint: jaeger-collector.monitoring.svc.cluster.local:14250",
                                            "otlp/jaeger:\n    endpoint: jaeger.monitoring.svc.cluster.local:4317"
                                        )
                                        config_data = config_data.replace("- jaeger\n", "- otlp/jaeger\n")
                                        
                                        cm.data["relay"] = config_data
                                        v1.replace_namespaced_config_map("my-otel-collector-opentelemetry-collector", namespace, cm)
                                        v1.delete_namespaced_pod(pod.metadata.name, namespace)
                                        console.print(f"[green]✓[/green] Fixed OTel config and restarted pod")
                            
                            elif container.restart_count > 5:
                                action = f"Restart pod: {pod.metadata.name} (restarts: {container.restart_count})"
                                fixes_applied.append(action)
                                console.print(f"[yellow]⚠[/yellow] {action}")
                                
                                if not dry_run:
                                    v1.delete_namespaced_pod(pod.metadata.name, namespace)
                                    console.print(f"[green]✓[/green] Pod deleted and will be recreated")
                        except:
                            # If can't read logs, just restart if high restart count
                            if container.restart_count > 5:
                                action = f"Restart pod: {pod.metadata.name} (restarts: {container.restart_count})"
                                fixes_applied.append(action)
                                console.print(f"[yellow]⚠[/yellow] {action}")
                                
                                if not dry_run:
                                    v1.delete_namespaced_pod(pod.metadata.name, namespace)
                                    console.print(f"[green]✓[/green] Pod deleted and will be recreated")
        
        # Find OOMKilled pods and suggest scaling
        for pod in pods.items:
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.last_state.terminated and container.last_state.terminated.reason == "OOMKilled":
                        action = f"OOMKilled detected in {pod.metadata.name} - Consider increasing memory limits"
                        fixes_applied.append(action)
                        console.print(f"[red]🔴[/red] {action}")
        
        if not fixes_applied:
            console.print("[bold green]✓ No issues found that require auto-fixing![/bold green]")
        else:
            console.print(f"\n[bold cyan]Total fixes: {len(fixes_applied)}[/bold cyan]")
            
            if dry_run:
                console.print("\n[bold yellow]Run with --no-dry-run to apply fixes[/bold yellow]")
        
    except Exception as e:
        console.print("[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def incident_report(namespace: str = typer.Option("default", help="Namespace")):
    """Generate incident report with AI analysis"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("[bold cyan]📋 Generating Incident Report...[/bold cyan]\n")
        
        # Collect data
        pods = v1.list_namespaced_pod(namespace)
        events = v1.list_namespaced_event(namespace)
        
        report = []
        report.append(f"# Incident Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Namespace: {namespace}\n")
        
        # Issues
        report.append("## Critical Issues")
        crashloop_pods = [p for p in pods.items if p.status.container_statuses and any(
            c.state.waiting and c.state.waiting.reason == "CrashLoopBackOff" for c in p.status.container_statuses)]
        
        if crashloop_pods:
            report.append(f"- CrashLoopBackOff: {len(crashloop_pods)} pods")
            for pod in crashloop_pods:
                report.append(f"  - {pod.metadata.name}")
        
        # Recent events
        report.append("\n## Recent Events")
        warning_events = [e for e in events.items if e.type == "Warning"][-10:]
        for event in warning_events:
            report.append(f"- [{event.last_timestamp}] {event.reason}: {event.message}")
        
        report_text = "\n".join(report)
        console.print(Panel(report_text, title="Incident Report", border_style="cyan"))
        
        # AI Analysis
        if os.getenv("GEMINI_API_KEY"):
            with console.status("[bold green]TARS:[/bold green] Analyzing incident..."):
                response = get_gemini_response(f"Analyze this Kubernetes incident and provide root cause analysis and remediation steps:\n{report_text}")
            console.print(Panel(response, title="[bold green]TARS:[/bold green] AI Analysis", border_style="green"))
        
        # Save to file
        filename = f"incident-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        with open(filename, 'w') as f:
            f.write(report_text)
        console.print(f"\n[bold green]✓[/bold green] Report saved to: {filename}")
        
    except Exception as e:
        console.print("[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def smart_scale(deployment: str, namespace: str = typer.Option("default", help="Namespace")):
    """AI-powered smart scaling based on current load"""
    try:
        config.load_kube_config()
        apps_v1 = k8s_client.AppsV1Api()
        custom_api = k8s_client.CustomObjectsApi()
        
        console.print(f"[bold cyan]🧠 Smart Scaling: {deployment}[/bold cyan]\n")
        
        # Get current deployment
        dep = apps_v1.read_namespaced_deployment(deployment, namespace)
        current_replicas = dep.spec.replicas
        
        console.print(f"Current replicas: {current_replicas}")
        
        # Get metrics
        try:
            metrics = custom_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )
            
            # Calculate average CPU/Memory for deployment pods
            dep_pods = [m for m in metrics['items'] if deployment in m['metadata']['name']]
            
            if dep_pods:
                total_cpu = 0
                for pod in dep_pods:
                    for container in pod['containers']:
                        cpu_str = container['usage']['cpu']
                        if cpu_str.endswith('n'):
                            total_cpu += int(cpu_str[:-1]) / 1_000_000_000
                        elif cpu_str.endswith('m'):
                            total_cpu += int(cpu_str[:-1]) / 1000
                
                avg_cpu = total_cpu / len(dep_pods)
                console.print(f"Average CPU per pod: {avg_cpu:.3f} cores")
                
                # Smart recommendation
                if avg_cpu > 0.8:
                    recommended = current_replicas + 2
                    console.print(f"[bold yellow]⚠ High CPU usage detected[/bold yellow]")
                    console.print(f"[bold green]Recommendation: Scale to {recommended} replicas[/bold green]")
                elif avg_cpu < 0.2 and current_replicas > 2:
                    recommended = max(2, current_replicas - 1)
                    console.print(f"[bold cyan]Low CPU usage detected[/bold cyan]")
                    console.print(f"[bold green]Recommendation: Scale down to {recommended} replicas[/bold green]")
                else:
                    console.print(f"[bold green]✓ Current scaling is optimal[/bold green]")
                    recommended = current_replicas
                
                if recommended != current_replicas:
                    if typer.confirm(f"\nScale to {recommended} replicas?"):
                        dep.spec.replicas = recommended
                        apps_v1.patch_namespaced_deployment(deployment, namespace, dep)
                        console.print(f"[bold green]✓[/bold green] Scaled to {recommended} replicas")
            
        except Exception as e:
            console.print("[bold yellow]⚠[/bold yellow] Metrics not available, using manual scaling")
        
    except Exception as e:
        console.print("[bold red]✗[/bold red] Error:", str(e), markup=False)

@app.command()
def god():
    """Activate TARS God Mode - full cluster control panel"""
    console.clear()
    console.print("""[bold red]
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              ⚡ TARS GOD MODE ACTIVATED ⚡                    ║
    ║                                                               ║
    ║         "This is no time for caution." - TARS                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    [/bold red]
    
    [bold yellow]🔥 SRE Power Commands:[/bold yellow]
    
    [bold cyan]Monitoring & Triage:[/bold cyan]
      tars oncall              - On-call engineer dashboard
      tars triage              - Quick incident triage
      tars incident-report     - Generate incident report with AI
      
    [bold cyan]Auto-Remediation:[/bold cyan]
      tars autofix             - Auto-fix common issues (dry-run)
      tars autofix --no-dry-run - Apply fixes automatically
      tars smart-scale <dep>   - AI-powered scaling decisions
      
    [bold cyan]Deep Analysis:[/bold cyan]
      tars analyze             - AI cluster analysis
      tars diagnose <pod>      - Deep pod diagnosis
      tars blast <pod>         - Blast radius analysis
      tars forecast            - Predict future issues
      
    [bold cyan]Quick Actions:[/bold cyan]
      tars restart <pod>       - Restart pod
      tars scale <dep> <n>     - Scale deployment
      tars rollback <dep>      - Rollback deployment
      
    [bold green]💡 Pro Tip:[/bold green] Start with 'tars oncall' for a complete overview
    """)

@app.command()
def alert(
    namespace: str = typer.Option("default", help="Namespace to monitor"),
    threshold_cpu: float = typer.Option(80.0, help="CPU threshold percentage"),
    threshold_memory: float = typer.Option(80.0, help="Memory threshold percentage"),
    interval: int = typer.Option(30, help="Check interval in seconds")
):
    """Real-time alerting for SREs - monitors and alerts on threshold breaches"""
    console.print(f"[bold cyan]🚨 TARS Alert Monitor Started[/bold cyan]")
    console.print(f"Namespace: {namespace} | CPU: {threshold_cpu}% | Memory: {threshold_memory}% | Interval: {interval}s\n")
    
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        alert_count = 0
        
        while True:
            try:
                pods = v1.list_namespaced_pod(namespace)
                alerts = []
                
                for pod in pods.items:
                    if pod.status.phase == "Running":
                        # Check for restarts
                        for container_status in pod.status.container_statuses or []:
                            if container_status.restart_count > 5:
                                alerts.append(f"🔄 {pod.metadata.name}: {container_status.restart_count} restarts")
                    
                    elif pod.status.phase in ["Failed", "Pending"]:
                        alerts.append(f"⚠️  {pod.metadata.name}: {pod.status.phase}")
                
                if alerts:
                    alert_count += len(alerts)
                    console.print(f"\n[bold red]⚠️  ALERTS DETECTED ({datetime.now().strftime('%H:%M:%S')})[/bold red]")
                    for alert in alerts:
                        console.print(f"  {alert}")
                    console.print(f"\n[dim]Total alerts: {alert_count}[/dim]")
                else:
                    console.print(f"[dim]{datetime.now().strftime('%H:%M:%S')} - All systems nominal[/dim]")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Alert monitor stopped[/bold yellow]")
                break
                
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def runbook(pod_name: str = typer.Argument(..., help="Pod name to generate runbook for")):
    """Generate incident runbook for a pod - SRE documentation"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print(f"\n[bold cyan]📖 Generating Runbook for: {pod_name}[/bold cyan]\n")
        
        # Find pod
        pods = v1.list_pod_for_all_namespaces()
        target_pod = None
        for pod in pods.items:
            if pod.metadata.name.startswith(pod_name):
                target_pod = pod
                break
        
        if not target_pod:
            console.print(f"[bold red]✗[/bold red] Pod not found")
            return
        
        namespace = target_pod.metadata.namespace
        
        # Generate runbook
        runbook = f"""
╔══════════════════════════════════════════════════════════════╗
║                    INCIDENT RUNBOOK                          ║
╚══════════════════════════════════════════════════════════════╝

📋 POD INFORMATION
  Name:      {target_pod.metadata.name}
  Namespace: {namespace}
  Status:    {target_pod.status.phase}
  Node:      {target_pod.spec.node_name}

🔍 DIAGNOSTIC STEPS

1. Check Pod Status
   $ tars diagnose {target_pod.metadata.name}

2. View Recent Logs
   $ tars logs {target_pod.metadata.name}

3. Check Events
   $ kubectl describe pod {target_pod.metadata.name} -n {namespace}

4. Check Resource Usage
   $ tars metrics

🔧 REMEDIATION STEPS

If CrashLoopBackOff:
  1. Check logs: tars logs {target_pod.metadata.name}
  2. Verify config: kubectl get configmap -n {namespace}
  3. Restart: tars restart {target_pod.metadata.name}

If OOMKilled:
  1. Check memory limits: kubectl get pod {target_pod.metadata.name} -n {namespace} -o yaml
  2. Increase limits or scale: tars smart-scale <deployment>

If Pending:
  1. Check node resources: tars nodes
  2. Check events: tars events

📞 ESCALATION
  - Check blast radius: tars blast {target_pod.metadata.name}
  - Generate incident report: tars incident-report
  - Review SLO impact: tars slo

⏱️  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        console.print(runbook)
        
        # Save to file
        filename = f"runbook_{target_pod.metadata.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(runbook)
        console.print(f"\n[bold green]✓[/bold green] Runbook saved to: {filename}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def snapshot():
    """Take a complete cluster snapshot for incident analysis"""
    console.print("[bold cyan]📸 Taking Cluster Snapshot...[/bold cyan]\n")
    
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        apps_v1 = k8s_k8s_client.AppsV1Api()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_dir = f"tars_snapshot_{timestamp}"
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Collect data
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            
            task = progress.add_task("Collecting pods...", total=None)
            pods = v1.list_pod_for_all_namespaces()
            with open(f"{snapshot_dir}/pods.txt", 'w') as f:
                for pod in pods.items:
                    f.write(f"{pod.metadata.namespace}/{pod.metadata.name} - {pod.status.phase}\n")
            progress.update(task, completed=True)
            
            task = progress.add_task("Collecting events...", total=None)
            events = v1.list_event_for_all_namespaces()
            with open(f"{snapshot_dir}/events.txt", 'w') as f:
                for event in events.items:
                    f.write(f"{event.last_timestamp} - {event.involved_object.name}: {event.message}\n")
            progress.update(task, completed=True)
            
            task = progress.add_task("Collecting deployments...", total=None)
            deployments = apps_v1.list_deployment_for_all_namespaces()
            with open(f"{snapshot_dir}/deployments.txt", 'w') as f:
                for dep in deployments.items:
                    f.write(f"{dep.metadata.namespace}/{dep.metadata.name} - {dep.spec.replicas} replicas\n")
            progress.update(task, completed=True)
            
            task = progress.add_task("Collecting nodes...", total=None)
            nodes = v1.list_node()
            with open(f"{snapshot_dir}/nodes.txt", 'w') as f:
                for node in nodes.items:
                    status = "Ready" if any(c.type == "Ready" and c.status == "True" for c in node.status.conditions) else "NotReady"
                    f.write(f"{node.metadata.name} - {status}\n")
            progress.update(task, completed=True)
        
        # Create summary
        summary = f"""
TARS CLUSTER SNAPSHOT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Pods: {len(pods.items)}
Total Deployments: {len(deployments.items)}
Total Nodes: {len(nodes.items)}
Total Events: {len(events.items)}

Files:
  - pods.txt
  - events.txt
  - deployments.txt
  - nodes.txt

Use this snapshot for:
  - Incident post-mortems
  - Capacity planning
  - Compliance audits
  - Historical analysis
"""
        
        with open(f"{snapshot_dir}/README.txt", 'w') as f:
            f.write(summary)
        
        console.print(f"[bold green]✓[/bold green] Snapshot saved to: {snapshot_dir}/")
        console.print(summary)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def diff(context1: str = typer.Argument(...), context2: str = typer.Argument(...)):
    """Compare two Kubernetes contexts - useful for multi-cluster SREs"""
    console.print(f"[bold cyan]🔄 Comparing Contexts[/bold cyan]")
    console.print(f"Context 1: {context1}")
    console.print(f"Context 2: {context2}\n")
    
    try:
        from kubernetes.config import list_kube_config_contexts
        
        contexts, active = list_kube_config_contexts()
        context_names = [c['name'] for c in contexts]
        
        if context1 not in context_names or context2 not in context_names:
            console.print("[bold red]✗[/bold red] One or both contexts not found")
            return
        
        def get_cluster_info(ctx):
            config.load_kube_config(context=ctx)
            v1 = k8s_client.CoreV1Api()
            apps_v1 = k8s_k8s_client.AppsV1Api()
            
            pods = v1.list_pod_for_all_namespaces()
            deployments = apps_v1.list_deployment_for_all_namespaces()
            nodes = v1.list_node()
            
            return {
                'pods': len(pods.items),
                'deployments': len(deployments.items),
                'nodes': len(nodes.items),
                'running_pods': len([p for p in pods.items if p.status.phase == "Running"]),
                'failed_pods': len([p for p in pods.items if p.status.phase == "Failed"])
            }
        
        info1 = get_cluster_info(context1)
        info2 = get_cluster_info(context2)
        
        table = Table(title="Cluster Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column(context1, style="green")
        table.add_column(context2, style="yellow")
        table.add_column("Diff", style="magenta")
        
        for key in info1.keys():
            diff = info2[key] - info1[key]
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            table.add_row(key.replace('_', ' ').title(), str(info1[key]), str(info2[key]), diff_str)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def dashboard(
    interval: int = typer.Option(5, help="Refresh interval in seconds"),
    all_namespaces: bool = typer.Option(False, "--all-namespaces", help="Monitor all namespaces")
):
    """Unified real-time monitoring dashboard"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        while True:
            console.clear()
            console.print(f"[bold cyan]TARS Dashboard[/bold cyan] - {datetime.now().strftime('%H:%M:%S')}\n")
            
            # Pods
            pods = v1.list_pod_for_all_namespaces() if all_namespaces else v1.list_namespaced_pod("default")
            running = len([p for p in pods.items if p.status.phase == "Running"])
            failed = len([p for p in pods.items if p.status.phase == "Failed"])
            pending = len([p for p in pods.items if p.status.phase == "Pending"])
            
            # Nodes
            nodes = v1.list_node()
            ready_nodes = len([n for n in nodes.items if any(c.type == "Ready" and c.status == "True" for c in n.status.conditions)])
            
            # Summary
            summary = Table.grid(padding=1)
            summary.add_column(style="cyan", justify="right")
            summary.add_column(style="bold")
            summary.add_row("Pods Running:", f"[green]{running}[/green]")
            summary.add_row("Pods Failed:", f"[red]{failed}[/red]")
            summary.add_row("Pods Pending:", f"[yellow]{pending}[/yellow]")
            summary.add_row("Nodes Ready:", f"[green]{ready_nodes}/{len(nodes.items)}[/green]")
            
            console.print(Panel(summary, title="Cluster Status", border_style="cyan"))
            
            # Recent pods
            table = Table(title="Recent Pods")
            table.add_column("Namespace", style="magenta")
            table.add_column("Pod", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Restarts", style="yellow")
            
            for pod in pods.items[:15]:
                status = pod.status.phase
                restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
                status_color = "green" if status == "Running" else "red"
                table.add_row(
                    pod.metadata.namespace,
                    pod.metadata.name[:40],
                    f"[{status_color}]{status}[/{status_color}]",
                    str(restarts)
                )
            
            console.print(table)
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print("\n[bold green]TARS:[/bold green] Dashboard stopped.")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def heatmap(namespace: str = typer.Option("default", help="Namespace")):
    """Resource usage heatmap"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        table = Table(title="Resource Usage Heatmap")
        table.add_column("Pod", style="cyan")
        table.add_column("CPU Usage", style="yellow")
        table.add_column("Memory Usage", style="magenta")
        
        for pod in pods.items:
            if pod.spec.containers:
                cpu_req = pod.spec.containers[0].resources.requests.get('cpu', 'N/A') if pod.spec.containers[0].resources.requests else 'N/A'
                mem_req = pod.spec.containers[0].resources.requests.get('memory', 'N/A') if pod.spec.containers[0].resources.requests else 'N/A'
                
                table.add_row(pod.metadata.name[:40], str(cpu_req), str(mem_req))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def cost(namespace: str = typer.Option("default", help="Namespace")):
    """Cost analysis and optimization recommendations"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        total_cpu = 0
        total_memory = 0
        
        for pod in pods.items:
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if container.resources.requests:
                        cpu = container.resources.requests.get('cpu', '0')
                        mem = container.resources.requests.get('memory', '0')
                        
                        if isinstance(cpu, str) and 'm' in cpu:
                            total_cpu += int(cpu.replace('m', '')) / 1000
                        
                        if isinstance(mem, str):
                            if 'Mi' in mem:
                                total_memory += int(mem.replace('Mi', ''))
                            elif 'Gi' in mem:
                                total_memory += int(mem.replace('Gi', '')) * 1024
        
        console.print(f"\n[bold cyan]Cost Analysis for namespace: {namespace}[/bold cyan]\n")
        console.print(f"Total CPU Requested: [yellow]{total_cpu:.2f} cores[/yellow]")
        console.print(f"Total Memory Requested: [yellow]{total_memory} Mi[/yellow]")
        console.print(f"\n[dim]Estimated monthly cost: ~${(total_cpu * 30 + total_memory * 0.004):.2f}[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def trace(service: str, namespace: str = typer.Option("default", help="Namespace")):
    """Show service dependencies and latency"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        svc = v1.read_namespaced_service(service, namespace)
        
        console.print(f"\n[bold cyan]Service Trace: {service}[/bold cyan]\n")
        console.print(f"Type: [yellow]{svc.spec.type}[/yellow]")
        console.print(f"Cluster IP: [yellow]{svc.spec.cluster_ip}[/yellow]")
        console.print(f"Ports: [yellow]{', '.join([f'{p.port}:{p.target_port}' for p in svc.spec.ports])}[/yellow]")
        
        # Find pods
        pods = v1.list_namespaced_pod(namespace, label_selector=','.join([f'{k}={v}' for k, v in svc.spec.selector.items()]))
        
        console.print(f"\nBacked by [green]{len(pods.items)}[/green] pods:")
        for pod in pods.items:
            console.print(f"  • {pod.metadata.name} - {pod.status.phase}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def aggregate_logs(
    namespace: str = typer.Option("default", help="Namespace"),
    pattern: str = typer.Option(None, help="Pattern to search"),
    tail: int = typer.Option(100, help="Lines per pod")
):
    """Aggregate logs across all pods in namespace"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        console.print(f"\n[bold cyan]Aggregated Logs - {namespace}[/bold cyan]\n")
        
        for pod in pods.items:
            try:
                logs = v1.read_namespaced_pod_log(pod.metadata.name, namespace, tail_lines=tail)
                
                if pattern:
                    matching_lines = [line for line in logs.split('\n') if pattern in line]
                    if matching_lines:
                        console.print(f"\n[yellow]{pod.metadata.name}:[/yellow]")
                        for line in matching_lines[:10]:
                            console.print(f"  {line}")
                else:
                    console.print(f"\n[yellow]{pod.metadata.name}:[/yellow]")
                    for line in logs.split('\n')[-5:]:
                        console.print(f"  {line}")
                        
            except Exception:
                continue
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def profile(pod_name: str, namespace: str = typer.Option("default", help="Namespace")):
    """CPU/Memory profiling for a pod"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pod = v1.read_namespaced_pod(pod_name, namespace)
        
        console.print(f"\n[bold cyan]Resource Profile: {pod_name}[/bold cyan]\n")
        
        for container in pod.spec.containers:
            console.print(f"[yellow]Container: {container.name}[/yellow]")
            
            if container.resources.requests:
                console.print(f"  Requests:")
                console.print(f"    CPU: {container.resources.requests.get('cpu', 'N/A')}")
                console.print(f"    Memory: {container.resources.requests.get('memory', 'N/A')}")
            
            if container.resources.limits:
                console.print(f"  Limits:")
                console.print(f"    CPU: {container.resources.limits.get('cpu', 'N/A')}")
                console.print(f"    Memory: {container.resources.limits.get('memory', 'N/A')}")
            
            console.print()
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def benchmark():
    """Cluster performance benchmarks"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print("\n[bold cyan]Running Cluster Benchmarks...[/bold cyan]\n")
        
        # API response time
        start = time.time()
        v1.list_pod_for_all_namespaces()
        api_time = time.time() - start
        
        # Node count
        nodes = v1.list_node()
        
        # Pod count
        pods = v1.list_pod_for_all_namespaces()
        
        table = Table(title="Benchmark Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_column("Status", style="green")
        
        table.add_row("API Response Time", f"{api_time:.3f}s", "✓" if api_time < 1 else "⚠")
        table.add_row("Total Nodes", str(len(nodes.items)), "✓")
        table.add_row("Total Pods", str(len(pods.items)), "✓")
        table.add_row("Running Pods", str(len([p for p in pods.items if p.status.phase == "Running"])), "✓")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def bottleneck(namespace: str = typer.Option("default", help="Namespace")):
    """Identify performance bottlenecks"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        console.print(f"\n[bold cyan]Bottleneck Analysis - {namespace}[/bold cyan]\n")
        
        issues = []
        
        for pod in pods.items:
            # Check restarts
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.restart_count > 5:
                        issues.append(f"[red]High restarts:[/red] {pod.metadata.name} ({container.restart_count} restarts)")
            
            # Check pending
            if pod.status.phase == "Pending":
                issues.append(f"[yellow]Pending pod:[/yellow] {pod.metadata.name}")
        
        if issues:
            for issue in issues:
                console.print(f"  • {issue}")
        else:
            console.print("[green]No bottlenecks detected[/green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def security_scan(namespace: str = typer.Option("default", help="Namespace")):
    """Security vulnerability scan"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        console.print(f"\n[bold cyan]Security Scan - {namespace}[/bold cyan]\n")
        
        issues = []
        
        for pod in pods.items:
            for container in pod.spec.containers:
                # Check privileged
                if container.security_context and container.security_context.privileged:
                    issues.append(f"[red]Privileged container:[/red] {pod.metadata.name}/{container.name}")
                
                # Check root user
                if container.security_context and container.security_context.run_as_user == 0:
                    issues.append(f"[yellow]Running as root:[/yellow] {pod.metadata.name}/{container.name}")
        
        if issues:
            for issue in issues:
                console.print(f"  • {issue}")
        else:
            console.print("[green]No security issues detected[/green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def compliance(namespace: str = typer.Option("default", help="Namespace")):
    """Policy compliance checks"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        pods = v1.list_namespaced_pod(namespace)
        
        console.print(f"\n[bold cyan]Compliance Check - {namespace}[/bold cyan]\n")
        
        compliant = 0
        non_compliant = 0
        
        for pod in pods.items:
            has_limits = False
            has_requests = False
            
            for container in pod.spec.containers:
                if container.resources.limits:
                    has_limits = True
                if container.resources.requests:
                    has_requests = True
            
            if has_limits and has_requests:
                compliant += 1
            else:
                non_compliant += 1
                console.print(f"[yellow]Missing resource limits/requests:[/yellow] {pod.metadata.name}")
        
        console.print(f"\n[green]Compliant:[/green] {compliant}")
        console.print(f"[red]Non-compliant:[/red] {non_compliant}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def audit(namespace: str = typer.Option("default", help="Namespace"), limit: int = typer.Option(50, help="Number of events")):
    """Audit trail of cluster events"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        events = v1.list_namespaced_event(namespace)
        
        console.print(f"\n[bold cyan]Audit Trail - {namespace}[/bold cyan]\n")
        
        table = Table()
        table.add_column("Time", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Reason", style="magenta")
        table.add_column("Object", style="green")
        table.add_column("Message", style="white")
        
        for event in sorted(events.items, key=lambda x: x.last_timestamp or x.event_time, reverse=True)[:limit]:
            timestamp = event.last_timestamp or event.event_time
            table.add_row(
                timestamp.strftime("%H:%M:%S") if timestamp else "N/A",
                event.type,
                event.reason,
                f"{event.involved_object.kind}/{event.involved_object.name}",
                event.message[:60]
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def alert_webhook(
    webhook_url: str = typer.Option(..., help="Webhook URL (Slack/PagerDuty)"),
    threshold_cpu: int = typer.Option(80, help="CPU threshold %"),
    threshold_memory: int = typer.Option(85, help="Memory threshold %"),
    namespace: str = typer.Option("default", help="Namespace"),
    interval: int = typer.Option(60, help="Check interval in seconds")
):
    """Send alerts to webhook (Slack/PagerDuty)"""
    import requests
    
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        console.print(f"[bold green]TARS:[/bold green] Monitoring with webhook alerts enabled")
        console.print(f"Webhook: {webhook_url[:50]}...")
        
        while True:
            pods = v1.list_namespaced_pod(namespace)
            
            for pod in pods.items:
                if pod.status.phase != "Running":
                    message = {
                        "text": f"🚨 Alert: Pod {pod.metadata.name} is {pod.status.phase} in namespace {namespace}"
                    }
                    requests.post(webhook_url, json=message)
                    console.print(f"[yellow]Alert sent:[/yellow] {pod.metadata.name}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print("\n[bold green]TARS:[/bold green] Webhook monitoring stopped.")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def alert_history(namespace: str = typer.Option("default", help="Namespace")):
    """Alert history and trends"""
    try:
        config.load_kube_config()
        v1 = k8s_client.CoreV1Api()
        
        events = v1.list_namespaced_event(namespace)
        
        warning_events = [e for e in events.items if e.type == "Warning"]
        
        console.print(f"\n[bold cyan]Alert History - {namespace}[/bold cyan]\n")
        console.print(f"Total warnings in last hour: [yellow]{len(warning_events)}[/yellow]\n")
        
        table = Table()
        table.add_column("Time", style="cyan")
        table.add_column("Reason", style="yellow")
        table.add_column("Object", style="green")
        table.add_column("Message", style="white")
        
        for event in sorted(warning_events, key=lambda x: x.last_timestamp or x.event_time, reverse=True)[:20]:
            timestamp = event.last_timestamp or event.event_time
            table.add_row(
                timestamp.strftime("%H:%M:%S") if timestamp else "N/A",
                event.reason,
                f"{event.involved_object.kind}/{event.involved_object.name}",
                event.message[:60]
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def prom_record(
    namespace: str = typer.Option("default", help="Namespace"),
    duration: int = typer.Option(300, help="Recording duration in seconds"),
    url: str = typer.Option(None, help="Prometheus URL")
):
    """Record Prometheus metrics over time"""
    try:
        prom = get_prometheus_client(url)
        
        console.print(f"[bold cyan]Recording metrics for {duration}s...[/bold cyan]\n")
        
        start_time = time.time()
        metrics_data = []
        
        while time.time() - start_time < duration:
            result = prom.custom_query(f'container_memory_usage_bytes{{namespace="{namespace}"}}')
            metrics_data.append({
                'timestamp': datetime.now(),
                'data': result
            })
            time.sleep(10)
        
        console.print(f"[green]Recorded {len(metrics_data)} data points[/green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def prom_compare(
    namespace1: str = typer.Argument(..., help="First namespace"),
    namespace2: str = typer.Argument(..., help="Second namespace"),
    url: str = typer.Option(None, help="Prometheus URL")
):
    """Compare Prometheus metrics across namespaces"""
    try:
        prom = get_prometheus_client(url)
        
        result1 = prom.custom_query(f'sum(container_memory_usage_bytes{{namespace="{namespace1}"}})')
        result2 = prom.custom_query(f'sum(container_memory_usage_bytes{{namespace="{namespace2}"}})')
        
        console.print(f"\n[bold cyan]Metrics Comparison[/bold cyan]\n")
        
        if result1 and result2:
            val1 = float(result1[0]['value'][1])
            val2 = float(result2[0]['value'][1])
            
            console.print(f"{namespace1}: [yellow]{val1 / 1024 / 1024:.2f} Mi[/yellow]")
            console.print(f"{namespace2}: [yellow]{val2 / 1024 / 1024:.2f} Mi[/yellow]")
            console.print(f"Difference: [magenta]{abs(val1 - val2) / 1024 / 1024:.2f} Mi[/magenta]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def prom_export(
    query: str = typer.Argument(..., help="PromQL query"),
    output: str = typer.Option("metrics.json", help="Output file"),
    url: str = typer.Option(None, help="Prometheus URL")
):
    """Export Prometheus metrics to file"""
    import json
    
    try:
        prom = get_prometheus_client(url)
        result = prom.custom_query(query)
        
        with open(output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        console.print(f"[green]Metrics exported to {output}[/green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def cardinality(
    url: str = typer.Option(None, help="Prometheus URL"),
    threshold: int = typer.Option(1000, help="High cardinality threshold"),
    top: int = typer.Option(20, help="Show top N metrics")
):
    """Check for high cardinality metrics in Prometheus"""
    try:
        prom = get_prometheus_client(url)
        
        console.print("\n[bold cyan]Checking High Cardinality Metrics...[/bold cyan]\n")
        
        # Get all metric names
        metrics = prom.all_metrics()
        
        cardinality_data = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing {len(metrics)} metrics...", total=len(metrics))
            
            for metric in metrics:
                try:
                    # Query to get cardinality
                    result = prom.custom_query(f'count({metric})')
                    if result and len(result) > 0:
                        count = int(float(result[0]['value'][1]))
                        cardinality_data.append({
                            'metric': metric,
                            'cardinality': count
                        })
                    progress.advance(task)
                except:
                    progress.advance(task)
                    continue
        
        # Sort by cardinality
        cardinality_data.sort(key=lambda x: x['cardinality'], reverse=True)
        
        # Display results
        table = Table(title="High Cardinality Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Cardinality", style="yellow")
        table.add_column("Status", style="red")
        
        high_cardinality_count = 0
        
        for item in cardinality_data[:top]:
            status = "⚠ HIGH" if item['cardinality'] > threshold else "✓ OK"
            status_color = "red" if item['cardinality'] > threshold else "green"
            
            if item['cardinality'] > threshold:
                high_cardinality_count += 1
            
            table.add_row(
                item['metric'],
                f"{item['cardinality']:,}",
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        console.print(table)
        
        # Summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"Total metrics analyzed: [yellow]{len(cardinality_data)}[/yellow]")
        console.print(f"High cardinality metrics (>{threshold}): [red]{high_cardinality_count}[/red]")
        
        if high_cardinality_count > 0:
            console.print(f"\n[yellow]⚠ Warning:[/yellow] High cardinality metrics can impact Prometheus performance")
            console.print("[dim]Consider reducing labels or aggregating metrics[/dim]")
        else:
            console.print(f"\n[green]✓ All metrics are within acceptable cardinality limits[/green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def cardinality_labels(
    metric: str = typer.Argument(..., help="Metric name to analyze"),
    url: str = typer.Option(None, help="Prometheus URL"),
    top: int = typer.Option(10, help="Show top N labels")
):
    """Analyze label cardinality for a specific metric"""
    try:
        prom = get_prometheus_client(url)
        
        console.print(f"\n[bold cyan]Label Cardinality Analysis: {metric}[/bold cyan]\n")
        
        # Get all series for this metric
        result = prom.custom_query(metric)
        
        if not result:
            console.print(f"[yellow]No data found for metric: {metric}[/yellow]")
            return
        
        # Analyze labels
        label_values = {}
        
        for series in result:
            for label, value in series['metric'].items():
                if label == '__name__':
                    continue
                if label not in label_values:
                    label_values[label] = set()
                label_values[label].add(value)
        
        # Calculate cardinality per label
        label_cardinality = [
            {'label': label, 'cardinality': len(values)}
            for label, values in label_values.items()
        ]
        
        label_cardinality.sort(key=lambda x: x['cardinality'], reverse=True)
        
        # Display results
        table = Table(title=f"Label Cardinality for {metric}")
        table.add_column("Label", style="cyan")
        table.add_column("Unique Values", style="yellow")
        table.add_column("Impact", style="magenta")
        
        for item in label_cardinality[:top]:
            impact = "HIGH" if item['cardinality'] > 100 else "MEDIUM" if item['cardinality'] > 10 else "LOW"
            impact_color = "red" if item['cardinality'] > 100 else "yellow" if item['cardinality'] > 10 else "green"
            
            table.add_row(
                item['label'],
                str(item['cardinality']),
                f"[{impact_color}]{impact}[/{impact_color}]"
            )
        
        console.print(table)
        
        # Total cardinality
        total_series = len(result)
        console.print(f"\nTotal time series: [yellow]{total_series}[/yellow]")
        
        # Recommendations
        high_cardinality_labels = [l for l in label_cardinality if l['cardinality'] > 100]
        if high_cardinality_labels:
            console.print(f"\n[yellow]⚠ Recommendations:[/yellow]")
            for label in high_cardinality_labels:
                console.print(f"  • Consider reducing cardinality of label '[cyan]{label['label']}[/cyan]' ({label['cardinality']} unique values)")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

if __name__ == "__main__":
    app()
