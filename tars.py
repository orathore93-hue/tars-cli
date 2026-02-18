#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from kubernetes import client, config
import google.generativeai as genai
import os
import time
from datetime import datetime
import sys

console = Console()
app = typer.Typer(
    help="T.A.R.S. - Technical Assistance & Reliability System for Kubernetes",
    add_completion=False,
    no_args_is_help=False
)

TARS_ASCII = """
[bold cyan]
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║  ████████╗     █████╗     ██████╗     ███████╗           ║
    ║  ╚══██╔══╝    ██╔══██╗    ██╔══██╗    ██╔════╝           ║
    ║     ██║       ███████║    ██████╔╝    ███████╗           ║
    ║     ██║   ██  ██╔══██║    ██╔══██╗    ╚════██║           ║
    ║     ██║   ██  ██║  ██║    ██║  ██║    ███████║           ║
    ║     ╚═╝   ╚═  ╚═╝  ╚═╝    ╚═╝  ╚═╝    ╚══════╝           ║
    ║                                                            ║
    ║    [bold yellow]Technical Assistance & Reliability System[/bold yellow]       ║
    ║                                                            ║
    ║         [dim]"Humor setting: 90%. Let's do this."[/dim]           ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
[/bold cyan]
"""

TARS_ROBOT = """[bold cyan]
        ╔═══════════════════════════════════╗
        ║   ┌─────────────────────────┐   ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │   ║
        ║   │  ▓ [bold yellow]◉[/bold yellow]  TARS  [bold yellow]◉[/bold yellow]  ▓  │   ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │   ║
        ║   │  ▓  [bold green]═══════════[/bold green]  ▓  │   ║
        ║   │  ▓  [bold green]═══════════[/bold green]  ▓  │   ║
        ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │   ║
        ║   └─────────────────────────┘   ║
        ║         ║           ║           ║
        ║      ┌──┴──┐     ┌──┴──┐        ║
        ║      │ ▓▓▓ │     │ ▓▓▓ │        ║
        ║      └─────┘     └─────┘        ║
        ╚═══════════════════════════════════╝
[/bold cyan]"""

WELCOME_MESSAGES = [
    "I'm ready to monitor your cluster.",
    "Humor setting at 90%. Cluster monitoring initiated.",
    "TARS online. Let's see what's broken today.",
    "Ready to analyze your Kubernetes mess... I mean cluster.",
    "Cluster monitoring active. Try not to break anything.",
    "All systems operational. Sarcasm levels optimal.",
    "Kubernetes monitoring engaged. This should be interesting.",
]

def show_welcome():
    """Display TARS welcome screen"""
    import random
    
    console.clear()
    console.print(TARS_ASCII)
    console.print(TARS_ROBOT)
    console.print(f"\n[bold cyan]TARS:[/bold cyan] [italic]{random.choice(WELCOME_MESSAGES)}[/italic]")
    console.print("[dim italic]Your companion while you Kubersnaut.[/dim italic]\n")
    
    # What TARS does
    info_panel = """[bold yellow]What I Do:[/bold yellow]
• Monitor Kubernetes clusters (GKE/EKS) in real-time
• Detect issues: CrashLoops, OOM kills, pending pods, resource spikes
• AI-powered analysis with Gemini for troubleshooting
• On-call engineer toolkit for incident response
• Prevent downtime with proactive monitoring

[bold yellow]Quick Start:[/bold yellow]
  [cyan]tars health[/cyan]      - Check cluster health
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
        return "Error: GEMINI_API_KEY not set. Cooper, I need that API key like you needed that black hole."
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    tars_prompt = f"""You are TARS from Interstellar - a sarcastic, witty AI with 90% humor setting.
Analyze this Kubernetes issue and respond in TARS's personality. Be helpful but add dry humor.
Keep responses concise and actionable.

{prompt}"""
    
    response = model.generate_content(tars_prompt)
    return response.text

@app.command()
def check():
    """Check cluster connectivity"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        console.print("[bold green]✓[/bold green] Kubernetes config loaded")
        
        version = client.VersionApi().get_code()
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def pods(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor pod health and detect issues"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
            
            # Get resource requests
            cpu = "N/A"
            memory = "N/A"
            if pod.spec.containers:
                if pod.spec.containers[0].resources.requests:
                    cpu = pod.spec.containers[0].resources.requests.get('cpu', 'N/A')
                    memory = pod.spec.containers[0].resources.requests.get('memory', 'N/A')
            
            if status != "Running":
                issues.append(f"Pod {pod.metadata.name} is {status}")
            if restarts > 5:
                issues.append(f"Pod {pod.metadata.name} has {restarts} restarts")
            
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
            console.print("\n[bold red]Issues detected:[/bold red]")
            for issue in issues:
                console.print(f"  • {issue}")
        else:
            console.print("\n[bold green]All pods healthy! Even I'm impressed.[/bold green]")
            
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def watch(namespace: str = typer.Option("default", help="Namespace to watch"), interval: int = typer.Option(5, help="Refresh interval in seconds")):
    """Real-time pod monitoring dashboard"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        console.print("[bold cyan]TARS watching your cluster... Press Ctrl+C to stop[/bold cyan]\n")
        
        while True:
            pods = v1.list_namespaced_pod(namespace)
            
            table = Table(title=f"Live Pod Monitor - {datetime.now().strftime('%H:%M:%S')}")
            table.add_column("Pod", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Restarts", style="yellow")
            table.add_column("Ready")
            
            for pod in pods.items:
                status = pod.status.phase
                restarts = sum([c.restart_count for c in pod.status.container_statuses]) if pod.status.container_statuses else 0
                ready = f"{sum([1 for c in pod.status.container_statuses if c.ready])}/{len(pod.status.container_statuses)}" if pod.status.container_statuses else "0/0"
                
                status_color = "green" if status == "Running" else "red"
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
        console.print("\n[bold cyan]TARS stopped watching. I'll be here if you need me.[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def analyze(namespace: str = typer.Option("default", help="Namespace to analyze")):
    """Analyze cluster issues with TARS AI"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        console.print("[bold cyan]TARS analyzing cluster...[/bold cyan]\n")
        
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
        
        with console.status("[bold cyan]TARS thinking...[/bold cyan]"):
            response = get_gemini_response(prompt)
        
        console.print(Panel(response, title="[bold cyan]TARS Analysis[/bold cyan]", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def logs(pod_name: str, namespace: str = typer.Option("default", help="Namespace"), tail: int = typer.Option(50, help="Number of lines")):
    """Get pod logs with AI summary"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        console.print(f"[bold cyan]Fetching logs for {pod_name}...[/bold cyan]\n")
        
        logs = v1.read_namespaced_pod_log(pod_name, namespace, tail_lines=tail)
        
        console.print(Panel(logs, title=f"[bold cyan]Logs: {pod_name}[/bold cyan]", border_style="cyan"))
        
        # AI analysis
        if os.getenv("GEMINI_API_KEY"):
            analyze_logs = typer.confirm("\nWant TARS to analyze these logs?")
            if analyze_logs:
                with console.status("[bold cyan]TARS reading logs...[/bold cyan]"):
                    response = get_gemini_response(f"Analyze these Kubernetes pod logs and identify any issues:\n{logs}")
                console.print(Panel(response, title="[bold cyan]TARS Log Analysis[/bold cyan]", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def events(namespace: str = typer.Option("default", help="Namespace"), limit: int = typer.Option(20, help="Number of events")):
    """Show recent cluster events"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def health():
    """Comprehensive cluster health check"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        console.print("[bold cyan]TARS running health diagnostics...[/bold cyan]\n")
        
        # Check nodes
        nodes = v1.list_node()
        healthy_nodes = sum([1 for n in nodes.items if all([c.status == "False" for c in n.status.conditions if c.type != "Ready"])])
        
        # Check pods across all namespaces
        all_pods = v1.list_pod_for_all_namespaces()
        running_pods = sum([1 for p in all_pods.items if p.status.phase == "Running"])
        total_pods = len(all_pods.items)
        failed_pods = sum([1 for p in all_pods.items if p.status.phase == "Failed"])
        
        # Check namespaces
        namespaces = v1.list_namespace()
        
        health_data = [
            ("Nodes", f"{len(nodes.items)} total", "green"),
            ("Pods Running", f"{running_pods}/{total_pods}", "green" if running_pods == total_pods else "yellow"),
            ("Failed Pods", str(failed_pods), "red" if failed_pods > 0 else "green"),
            ("Namespaces", str(len(namespaces.items)), "cyan"),
        ]
        
        table = Table(title="Cluster Health Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Status")
        
        for metric, value, color in health_data:
            status = "✓" if color == "green" else "⚠" if color == "yellow" else "✗"
            table.add_row(metric, value, f"[{color}]{status}[/{color}]")
        
        console.print(table)
        
        if failed_pods > 0:
            console.print(f"\n[bold yellow]TARS recommends running: tars analyze[/bold yellow]")
        else:
            console.print(f"\n[bold green]Cluster health is optimal. I'd give it a 95% rating.[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def diagnose(pod_name: str, namespace: str = typer.Option("default", help="Namespace")):
    """Deep dive diagnosis of a specific pod"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        console.print(f"[bold cyan]TARS diagnosing {pod_name}...[/bold cyan]\n")
        
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
            with console.status("[bold cyan]TARS analyzing...[/bold cyan]"):
                response = get_gemini_response(f"Diagnose this Kubernetes pod:\n" + "\n".join(info))
            console.print(Panel(response, title="[bold cyan]TARS Diagnosis[/bold cyan]", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

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
        90: "Humor at 90%. This is my sweet spot, Cooper.",
        100: "Humor at 100%. Warning: Sarcasm levels critical. Proceed with caution."
    }
    
    closest = min(responses.keys(), key=lambda x: abs(x - level))
    console.print(f"[bold cyan]{responses[closest]}[/bold cyan]")

@app.command()
def metrics(namespace: str = typer.Option("default", help="Namespace to check")):
    """Check CPU and memory usage across pods"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        custom_api = client.CustomObjectsApi()
        
        console.print("[bold cyan]TARS checking resource metrics...[/bold cyan]\n")
        
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
            console.print(f"[bold yellow]⚠[/bold yellow] Metrics server not available: {e}")
            console.print("[bold cyan]Tip: Install metrics-server with: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml[/bold cyan]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

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
        custom_api = client.CustomObjectsApi()
        
        console.print(f"[bold cyan]TARS monitoring for spikes (CPU > {cpu_threshold} cores, Memory > {memory_threshold}Mi)...[/bold cyan]")
        console.print("[bold cyan]Press Ctrl+C to stop[/bold cyan]\n")
        
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
                        spikes_detected.append(f"[bold red]🔥 CPU SPIKE[/bold red] {pod_name}: {total_cpu:.3f} cores")
                        spike_history[pod_name] = spike_history.get(pod_name, 0) + 1
                    
                    if total_memory > memory_threshold:
                        spikes_detected.append(f"[bold red]🔥 MEMORY SPIKE[/bold red] {pod_name}: {total_memory:.1f}Mi")
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
        console.print("\n\n[bold cyan]TARS stopped monitoring.[/bold cyan]")
        if spike_history:
            console.print("\n[bold yellow]Spike Summary:[/bold yellow]")
            for pod, count in sorted(spike_history.items(), key=lambda x: x[1], reverse=True):
                console.print(f"  {pod}: {count} spikes detected")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def top(namespace: str = typer.Option("default", help="Namespace to check"), limit: int = typer.Option(10, help="Number of pods to show")):
    """Show top resource-consuming pods"""
    try:
        config.load_kube_config()
        custom_api = client.CustomObjectsApi()
        
        console.print("[bold cyan]TARS calculating top resource consumers...[/bold cyan]\n")
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def services(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor services and endpoints"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def deployments(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor deployments and replica status"""
    try:
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def crds():
    """List Custom Resource Definitions"""
    try:
        config.load_kube_config()
        api_client = client.ApiextensionsV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def nodes():
    """Monitor node health and resources"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def ingress(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor ingress resources"""
    try:
        config.load_kube_config()
        networking_v1 = client.NetworkingV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def volumes(namespace: str = typer.Option("default", help="Namespace to check")):
    """Monitor persistent volumes and claims"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def namespaces():
    """List all namespaces with resource counts"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

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
║  GitHub: [bold blue]@orathore93-hue[/bold blue]                            ║
║                                                       ║
║  [dim]"An AI-powered Kubernetes monitoring tool with[/dim]    ║
║  [dim]90% humor setting and 100% functionality."[/dim]        ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(creator_info)
    console.print("\n[bold cyan]TARS:[/bold cyan] [italic]Yes, I was built by a human. Surprising, I know.[/italic]\n")

@app.command()
def restart(pod_name: str, namespace: str = typer.Option("default", help="Namespace")):
    """Restart a pod (delete and let controller recreate)"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        confirm = typer.confirm(f"Are you sure you want to restart {pod_name}?")
        if not confirm:
            console.print("[yellow]Restart cancelled[/yellow]")
            return
        
        console.print(f"[bold cyan]TARS restarting {pod_name}...[/bold cyan]")
        v1.delete_namespaced_pod(pod_name, namespace)
        console.print(f"[bold green]✓[/bold green] Pod {pod_name} deleted. Controller will recreate it.")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def scale(deployment: str, replicas: int, namespace: str = typer.Option("default", help="Namespace")):
    """Scale a deployment up or down"""
    try:
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()
        
        console.print(f"[bold cyan]TARS scaling {deployment} to {replicas} replicas...[/bold cyan]")
        
        body = {"spec": {"replicas": replicas}}
        apps_v1.patch_namespaced_deployment_scale(deployment, namespace, body)
        
        console.print(f"[bold green]✓[/bold green] Deployment {deployment} scaled to {replicas} replicas")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def errors(namespace: str = typer.Option("default", help="Namespace"), limit: int = typer.Option(20, help="Number of errors")):
    """Show pods with errors and crash loops"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def crashloop(namespace: str = typer.Option("default", help="Namespace")):
    """Detect and analyze crash looping pods"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def pending(namespace: str = typer.Option("default", help="Namespace")):
    """Show pending pods and why they're stuck"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def oom(namespace: str = typer.Option("default", help="Namespace")):
    """Detect Out of Memory killed pods"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def network(namespace: str = typer.Option("default", help="Namespace")):
    """Check network connectivity issues"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        networking_v1 = client.NetworkingV1Api()
        
        console.print("[bold cyan]TARS checking network configuration...[/bold cyan]\n")
        
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
            except:
                pass
        
        if issues > 0:
            console.print(table)
            console.print(f"\n[bold yellow]⚠ {issues} services have no endpoints[/bold yellow]")
        else:
            console.print("[bold green]All services have healthy endpoints![/bold green]")
        
        # Check network policies
        try:
            policies = networking_v1.list_namespaced_network_policy(namespace)
            console.print(f"\n[bold cyan]Network Policies:[/bold cyan] {len(policies.items)}")
        except:
            pass
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def quota(namespace: str = typer.Option("default", help="Namespace")):
    """Check resource quotas and usage"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
                    except:
                        pass
                    
                    table.add_row(
                        resource,
                        str(used),
                        str(hard),
                        f"[{status_color}]{status}[/{status_color}]"
                    )
            
            console.print(table)
            console.print()
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def triage(namespace: str = typer.Option("default", help="Namespace")):
    """Quick incident triage - show all critical issues"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        console.print("[bold cyan]TARS performing incident triage...[/bold cyan]\n")
        
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
                critical_pods.append(f"[red]FAILED[/red]: {pod.metadata.name}")
            
            if status == "Pending":
                issues["pending"] += 1
                critical_pods.append(f"[yellow]PENDING[/yellow]: {pod.metadata.name}")
            
            if restarts > 10:
                issues["high_restarts"] += 1
                critical_pods.append(f"[yellow]HIGH RESTARTS ({restarts})[/yellow]: {pod.metadata.name}")
            
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def rollback(deployment: str, namespace: str = typer.Option("default", help="Namespace")):
    """Rollback deployment to previous revision"""
    try:
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()
        
        console.print(f"[bold cyan]TARS rolling back {deployment}...[/bold cyan]")
        
        # Get rollout history
        result = os.popen(f"kubectl rollout history deployment/{deployment} -n {namespace}").read()
        console.print(f"\n[dim]{result}[/dim]")
        
        confirm = typer.confirm(f"Rollback {deployment} to previous revision?")
        if not confirm:
            console.print("[yellow]Rollback cancelled[/yellow]")
            return
        
        # Perform rollback
        os.system(f"kubectl rollout undo deployment/{deployment} -n {namespace}")
        console.print(f"\n[bold green]✓[/bold green] Rollback initiated for {deployment}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

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
        
        console.print(f"[bold cyan]TARS draining node {node_name}...[/bold cyan]")
        os.system(f"kubectl drain {node_name} --ignore-daemonsets --delete-emptydir-data")
        
        console.print(f"\n[bold green]✓[/bold green] Node {node_name} drained successfully")
        console.print(f"[bold cyan]Tip: Use 'kubectl uncordon {node_name}' to make it schedulable again[/bold cyan]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def cordon(node_name: str):
    """Mark node as unschedulable"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold cyan]TARS cordoning node {node_name}...[/bold cyan]")
        os.system(f"kubectl cordon {node_name}")
        
        console.print(f"[bold green]✓[/bold green] Node {node_name} marked unschedulable")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def uncordon(node_name: str):
    """Mark node as schedulable"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold cyan]TARS uncordoning node {node_name}...[/bold cyan]")
        os.system(f"kubectl uncordon {node_name}")
        
        console.print(f"[bold green]✓[/bold green] Node {node_name} marked schedulable")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def exec(pod_name: str, namespace: str = typer.Option("default", help="Namespace"), command: str = typer.Option("/bin/sh", help="Command to execute")):
    """Execute command in a pod"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold cyan]TARS executing in {pod_name}...[/bold cyan]")
        os.system(f"kubectl exec -it {pod_name} -n {namespace} -- {command}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def port_forward(pod_name: str, ports: str, namespace: str = typer.Option("default", help="Namespace")):
    """Port forward to a pod (e.g., 8080:80)"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold cyan]TARS forwarding ports {ports} to {pod_name}...[/bold cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        os.system(f"kubectl port-forward {pod_name} {ports} -n {namespace}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def describe(resource: str, name: str, namespace: str = typer.Option("default", help="Namespace")):
    """Describe a Kubernetes resource"""
    try:
        config.load_kube_config()
        
        console.print(f"[bold cyan]TARS describing {resource}/{name}...[/bold cyan]\n")
        os.system(f"kubectl describe {resource} {name} -n {namespace}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def context():
    """Show and switch Kubernetes contexts"""
    try:
        config.load_kube_config()
        
        console.print("[bold cyan]Available Contexts:[/bold cyan]\n")
        os.system("kubectl config get-contexts")
        
        console.print("\n[bold cyan]Current Context:[/bold cyan]")
        os.system("kubectl config current-context")
        
        switch = typer.confirm("\nSwitch context?")
        if switch:
            context_name = typer.prompt("Enter context name")
            os.system(f"kubectl config use-context {context_name}")
            console.print(f"[bold green]✓[/bold green] Switched to {context_name}")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def secrets(namespace: str = typer.Option("default", help="Namespace")):
    """List secrets (names only, no values)"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

@app.command()
def configmaps(namespace: str = typer.Option("default", help="Namespace")):
    """List ConfigMaps"""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
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
        console.print(f"[bold red]✗[/bold red] Error: {e}")

if __name__ == "__main__":
    app()
