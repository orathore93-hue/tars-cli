"""Core monitoring commands - Business logic only, delegates to API and output layers"""
import logging
from typing import Optional
from .k8s_client import KubernetesClient
from .ai import analyzer, GeminiAPIError
from .utils import (
    create_table, print_error, print_success, 
    print_info, print_warning, format_pod_status, console
)
from .security import validate_namespace

logger = logging.getLogger(__name__)


class MonitoringCommands:
    """Kubernetes monitoring commands - orchestrates API calls and output"""
    
    def __init__(self):
        try:
            self.k8s = KubernetesClient()
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    def health_check(self, namespace: Optional[str] = None):
        """Check cluster health - delegates to API and output layers"""
        try:
            # Get data from API (no output here)
            nodes = self.k8s.list_nodes()
            pods = self.k8s.list_pods(namespace)
            
            # Process data (business logic)
            health_metrics = self._calculate_health_metrics(nodes, pods)
            
            # Output results (delegated to utils)
            self._display_health_report(health_metrics)
            
            # AI analysis (if available)
            if analyzer.is_available():
                try:
                    analysis = analyzer.analyze_cluster_health(health_metrics)
                    console.print(f"\n[dim]AI Analysis: {analysis}[/dim]")
                except GeminiAPIError as e:
                    logger.debug(f"AI analysis unavailable: {e}")
            
        except Exception as e:
            print_error(f"Health check failed: {e}")
            logger.error(f"Health check error: {e}", exc_info=True)
            raise
    
    def list_pods(self, namespace: Optional[str] = None):
        """List pods with status"""
        try:
            if namespace and not validate_namespace(namespace):
                print_error(f"Invalid namespace: {namespace}")
                return
            
            # Get data from API
            pods = self.k8s.list_pods(namespace)
            
            # Process and display
            self._display_pods_table(pods, namespace)
        
        except Exception as e:
            print_error(f"Failed to list pods: {e}")
            logger.error(f"List pods error: {e}", exc_info=True)
            raise
    
    def diagnose_pod(self, pod_name: str, namespace: str = "default"):
        """Diagnose pod issues"""
        try:
            if not validate_namespace(namespace):
                print_error(f"Invalid namespace: {namespace}")
                return
            
            # Get data from API
            pod = self.k8s.get_pod(pod_name, namespace)
            
            # Display basic info
            self._display_pod_info(pod)
            
            # AI analysis if pod has issues
            if pod.status.phase != "Running" and analyzer.is_available():
                try:
                    pod_data = self._extract_pod_data(pod)
                    analysis = analyzer.analyze_pod_issue(pod_data)
                    console.print(f"\n[bold]Analysis:[/bold]\n{analysis}")
                except GeminiAPIError as e:
                    logger.debug(f"AI analysis failed: {e}")
        
        except Exception as e:
            print_error(f"Diagnosis failed: {e}")
            logger.error(f"Diagnose error: {e}", exc_info=True)
            raise
    
    # Private methods - business logic and data processing
    
    def _calculate_health_metrics(self, nodes, pods) -> dict:
        """Calculate health metrics from raw data"""
        total_nodes = len(nodes)
        ready_nodes = sum(1 for n in nodes if self._is_node_ready(n))
        
        total_pods = len(pods)
        running_pods = sum(1 for p in pods if p.status.phase == "Running")
        failed_pods = sum(1 for p in pods if p.status.phase == "Failed")
        pending_pods = sum(1 for p in pods if p.status.phase == "Pending")
        
        return {
            "nodes": {"total": total_nodes, "ready": ready_nodes},
            "pods": {
                "total": total_pods,
                "running": running_pods,
                "failed": failed_pods,
                "pending": pending_pods
            }
        }
    
    def _display_health_report(self, metrics: dict):
        """Display health report using Rich"""
        table = create_table("Cluster Health Report", ["Metric", "Value", "Status"])
        
        nodes = metrics["nodes"]
        pods = metrics["pods"]
        
        table.add_row(
            "Nodes",
            f"{nodes['ready']}/{nodes['total']}",
            "✓" if nodes['ready'] == nodes['total'] else "⚠"
        )
        table.add_row(
            "Pods Running",
            f"{pods['running']}/{pods['total']}",
            "✓" if pods['running'] == pods['total'] else "⚠"
        )
        table.add_row(
            "Failed Pods",
            str(pods['failed']),
            "✓" if pods['failed'] == 0 else "✗"
        )
        table.add_row(
            "Pending Pods",
            str(pods['pending']),
            "✓" if pods['pending'] == 0 else "⚠"
        )
        
        console.print(table)
    
    def _display_pods_table(self, pods, namespace: Optional[str]):
        """Display pods in a table"""
        table = create_table(
            f"Pods in {namespace or 'all namespaces'}", 
            ["Namespace", "Name", "Status", "Restarts", "Age"]
        )
        
        for pod in pods[:50]:  # Limit for performance
            restarts = sum(
                c.restart_count for c in pod.status.container_statuses or []
            )
            age = self._calculate_age(pod.metadata.creation_timestamp)
            
            table.add_row(
                pod.metadata.namespace,
                pod.metadata.name,
                format_pod_status(pod.status.phase),
                str(restarts),
                age
            )
        
        console.print(table)
        
        if len(pods) > 50:
            console.print(f"\n[dim]Showing 50 of {len(pods)} pods[/dim]")
    
    def _display_pod_info(self, pod):
        """Display pod information"""
        console.print(f"\n[bold]Pod:[/bold] {pod.metadata.name}")
        console.print(f"[bold]Status:[/bold] {format_pod_status(pod.status.phase)}")
        console.print(f"[bold]Node:[/bold] {pod.spec.node_name}")
        
        if pod.status.container_statuses:
            console.print("\n[bold]Containers:[/bold]")
            for container in pod.status.container_statuses:
                console.print(
                    f"  • {container.name}: "
                    f"Ready={container.ready}, "
                    f"Restarts={container.restart_count}"
                )
    
    def _extract_pod_data(self, pod) -> dict:
        """Extract relevant pod data for AI analysis"""
        return {
            "name": pod.metadata.name,
            "status": pod.status.phase,
            "containers": [
                {
                    "name": c.name,
                    "ready": c.ready,
                    "restarts": c.restart_count
                }
                for c in (pod.status.container_statuses or [])
            ]
        }
    
    def _is_node_ready(self, node) -> bool:
        """Check if node is ready"""
        for condition in node.status.conditions or []:
            if condition.type == "Ready":
                return condition.status == "True"
        return False
    
    def _calculate_age(self, timestamp) -> str:
        """Calculate resource age"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        age = now - timestamp
        
        days = age.days
        hours = age.seconds // 3600
        minutes = (age.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
