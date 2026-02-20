"""SRE-focused utilities and quick fixes"""
import re
from typing import List, Dict, Optional
from kubernetes import client
from rich.console import Console
from rich.table import Table

console = Console()


def validate_resource_name(name: str) -> bool:
    """Validate Kubernetes resource name - SECURITY"""
    if not name:
        return False
    # K8s DNS-1123 subdomain: lowercase alphanumeric, '-', '.'
    pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$'
    return bool(re.match(pattern, name)) and len(name) <= 253


def validate_namespace(namespace: str) -> bool:
    """Validate namespace name - SECURITY"""
    if not namespace:
        return False
    # K8s DNS-1123 label
    pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'
    return bool(re.match(pattern, namespace)) and len(namespace) <= 63


def sanitize_command_arg(arg: str) -> str:
    """Sanitize command arguments - SECURITY"""
    # Remove dangerous characters
    dangerous = ['&', '|', ';', '$', '`', '\\n', '\\r', '>', '<', '(', ')']
    for char in dangerous:
        arg = arg.replace(char, '')
    return arg.strip()


class BlastRadiusAnalyzer:
    """Analyze blast radius of resource changes"""
    
    def __init__(self, k8s_client):
        self.k8s = k8s_client
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    def analyze_deployment(self, name: str, namespace: str) -> Dict:
        """Analyze blast radius of a deployment"""
        if not validate_resource_name(name) or not validate_namespace(namespace):
            raise ValueError("Invalid resource name or namespace")
        
        blast_radius = {
            "deployment": name,
            "namespace": namespace,
            "pods": [],
            "services": [],
            "ingresses": [],
            "configmaps": [],
            "secrets": [],
            "estimated_impact": "low"
        }
        
        try:
            # Get deployment
            deployment = self.apps_v1.read_namespaced_deployment(name, namespace)
            replicas = deployment.spec.replicas or 0
            
            # Get pods
            label_selector = ",".join([f"{k}={v}" for k, v in deployment.spec.selector.match_labels.items()])
            pods = self.core_v1.list_namespaced_pod(namespace, label_selector=label_selector)
            blast_radius["pods"] = [pod.metadata.name for pod in pods.items]
            
            # Get services pointing to these pods
            services = self.core_v1.list_namespaced_service(namespace)
            for svc in services.items:
                if svc.spec.selector:
                    if any(k in deployment.spec.selector.match_labels and 
                          deployment.spec.selector.match_labels[k] == v 
                          for k, v in svc.spec.selector.items()):
                        blast_radius["services"].append(svc.metadata.name)
            
            # Estimate impact
            if replicas > 10:
                blast_radius["estimated_impact"] = "high"
            elif replicas > 3:
                blast_radius["estimated_impact"] = "medium"
            
            blast_radius["replica_count"] = replicas
            
        except Exception as e:
            console.print(f"[red]Error analyzing blast radius: {e}[/red]")
        
        return blast_radius
    
    def display_blast_radius(self, blast_radius: Dict):
        """Display blast radius analysis"""
        impact_color = {
            "low": "green",
            "medium": "yellow",
            "high": "red"
        }
        
        color = impact_color.get(blast_radius["estimated_impact"], "yellow")
        
        console.print(f"\n[bold]Blast Radius Analysis[/bold]")
        console.print(f"[bold]Deployment:[/bold] {blast_radius['deployment']}")
        console.print(f"[bold]Namespace:[/bold] {blast_radius['namespace']}")
        console.print(f"[bold]Impact:[/bold] [{color}]{blast_radius['estimated_impact'].upper()}[/{color}]\n")
        
        table = Table(show_header=True)
        table.add_column("Resource Type", style="cyan")
        table.add_column("Count", style="yellow")
        table.add_column("Names", style="white")
        
        table.add_row("Pods", str(len(blast_radius['pods'])), ", ".join(blast_radius['pods'][:3]) + ("..." if len(blast_radius['pods']) > 3 else ""))
        table.add_row("Services", str(len(blast_radius['services'])), ", ".join(blast_radius['services']))
        table.add_row("Replicas", str(blast_radius.get('replica_count', 0)), "-")
        
        console.print(table)
        
        if blast_radius["estimated_impact"] == "high":
            console.print("\n[bold red]⚠️  HIGH IMPACT: This change will affect many resources![/bold red]")
            console.print("[yellow]Consider:[/yellow]")
            console.print("  • Rolling update with small batch size")
            console.print("  • Blue-green deployment")
            console.print("  • Canary deployment")
            console.print("  • Schedule during maintenance window\n")


class QuickFixer:
    """Quick fixes for common issues"""
    
    def __init__(self, k8s_client):
        self.k8s = k8s_client
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    def fix_crashloop(self, pod_name: str, namespace: str, dry_run: bool = True) -> List[str]:
        """Suggest fixes for crashloop backoff"""
        if not validate_resource_name(pod_name) or not validate_namespace(namespace):
            raise ValueError("Invalid pod name or namespace")
        
        fixes = []
        
        try:
            pod = self.core_v1.read_namespaced_pod(pod_name, namespace)
            
            # Check container statuses
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff":
                        # Get recent logs
                        try:
                            logs = self.core_v1.read_namespaced_pod_log(
                                pod_name, namespace, 
                                container=container.name,
                                tail_lines=50
                            )
                            
                            # Analyze logs for common issues
                            if "OOMKilled" in logs or "out of memory" in logs.lower():
                                fixes.append(f"Increase memory limit for container '{container.name}'")
                            
                            if "connection refused" in logs.lower() or "cannot connect" in logs.lower():
                                fixes.append(f"Check service dependencies for container '{container.name}'")
                            
                            if "permission denied" in logs.lower():
                                fixes.append(f"Check RBAC permissions for container '{container.name}'")
                            
                            if "no such file" in logs.lower() or "not found" in logs.lower():
                                fixes.append(f"Check volume mounts for container '{container.name}'")
                            
                        except Exception:
                            fixes.append(f"Unable to read logs for container '{container.name}'")
            
            if not fixes:
                fixes.append("No obvious fix detected. Check pod logs manually.")
        
        except Exception as e:
            console.print(f"[red]Error analyzing pod: {e}[/red]")
        
        return fixes
    
    def clear_evicted_pods(self, namespace: str, dry_run: bool = True) -> int:
        """Remove all evicted pods"""
        if not validate_namespace(namespace):
            raise ValueError("Invalid namespace")
        
        try:
            pods = self.core_v1.list_namespaced_pod(namespace)
            evicted_pods = [pod for pod in pods.items if pod.status.phase == "Failed" and 
                           pod.status.reason == "Evicted"]
            
            if dry_run:
                console.print(f"\n[yellow]DRY RUN: Would delete {len(evicted_pods)} evicted pods[/yellow]")
                for pod in evicted_pods[:10]:
                    console.print(f"  • {pod.metadata.name}")
                if len(evicted_pods) > 10:
                    console.print(f"  ... and {len(evicted_pods) - 10} more")
                return len(evicted_pods)
            
            deleted = 0
            for pod in evicted_pods:
                try:
                    self.core_v1.delete_namespaced_pod(pod.metadata.name, namespace)
                    deleted += 1
                except Exception as e:
                    console.print(f"[red]Failed to delete {pod.metadata.name}: {e}[/red]")
            
            console.print(f"[green]✓ Deleted {deleted} evicted pods[/green]")
            return deleted
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return 0
