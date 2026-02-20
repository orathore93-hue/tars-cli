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
    
    def get_pod_logs(self, pod_name: str, namespace: str, tail: int):
        """Get pod logs"""
        try:
            logs = self.k8s.get_pod_logs(pod_name, namespace, tail)
            console.print(f"\n[bold]Logs for {pod_name}[/bold] (last {tail} lines)\n")
            console.print(logs)
        except Exception as e:
            print_error(f"Failed to get logs: {e}")
            raise
    
    def list_events(self, namespace: str, limit: int):
        """List cluster events"""
        try:
            events = self.k8s.list_events(namespace)
            table = create_table(f"Events in {namespace}", ["Time", "Type", "Reason", "Object", "Message"])
            
            for event in events[:limit]:
                table.add_row(
                    self._calculate_age(event.last_timestamp or event.event_time),
                    event.type,
                    event.reason,
                    f"{event.involved_object.kind}/{event.involved_object.name}",
                    event.message[:80]
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list events: {e}")
            raise
    
    def list_nodes(self):
        """List cluster nodes"""
        try:
            nodes = self.k8s.list_nodes()
            table = create_table("Cluster Nodes", ["Name", "Status", "Roles", "Age", "Version"])
            
            for node in nodes:
                status = "Ready" if self._is_node_ready(node) else "NotReady"
                roles = ",".join(node.metadata.labels.get("node-role.kubernetes.io", {}).keys()) or "worker"
                
                table.add_row(
                    node.metadata.name,
                    format_pod_status(status),
                    roles,
                    self._calculate_age(node.metadata.creation_timestamp),
                    node.status.node_info.kubelet_version
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list nodes: {e}")
            raise
    
    def list_deployments(self, namespace: str):
        """List deployments"""
        try:
            deployments = self.k8s.list_deployments(namespace)
            table = create_table(f"Deployments in {namespace}", ["Name", "Ready", "Up-to-date", "Available", "Age"])
            
            for deploy in deployments:
                table.add_row(
                    deploy.metadata.name,
                    f"{deploy.status.ready_replicas or 0}/{deploy.spec.replicas or 0}",
                    str(deploy.status.updated_replicas or 0),
                    str(deploy.status.available_replicas or 0),
                    self._calculate_age(deploy.metadata.creation_timestamp)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list deployments: {e}")
            raise
    
    def list_services(self, namespace: str):
        """List services"""
        try:
            services = self.k8s.list_services(namespace)
            table = create_table(f"Services in {namespace}", ["Name", "Type", "Cluster-IP", "External-IP", "Port(s)", "Age"])
            
            for svc in services:
                ports = ",".join([f"{p.port}/{p.protocol}" for p in svc.spec.ports or []])
                external_ip = ",".join(svc.status.load_balancer.ingress or []) if svc.status.load_balancer else "<none>"
                
                table.add_row(
                    svc.metadata.name,
                    svc.spec.type,
                    svc.spec.cluster_ip or "<none>",
                    external_ip,
                    ports,
                    self._calculate_age(svc.metadata.creation_timestamp)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list services: {e}")
            raise

    def list_namespaces(self):
        """List all namespaces"""
        try:
            namespaces = self.k8s.list_namespaces()
            table = create_table("Namespaces", ["Name", "Status", "Age"])
            
            for ns in namespaces:
                table.add_row(
                    ns.metadata.name,
                    ns.status.phase,
                    self._calculate_age(ns.metadata.creation_timestamp)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list namespaces: {e}")
            raise
    
    def list_configmaps(self, namespace: str):
        """List configmaps"""
        try:
            configmaps = self.k8s.list_configmaps(namespace)
            table = create_table(f"ConfigMaps in {namespace}", ["Name", "Data", "Age"])
            
            for cm in configmaps:
                table.add_row(
                    cm.metadata.name,
                    str(len(cm.data or {})),
                    self._calculate_age(cm.metadata.creation_timestamp)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list configmaps: {e}")
            raise
    
    def list_secrets(self, namespace: str):
        """List secrets"""
        try:
            secrets = self.k8s.list_secrets(namespace)
            table = create_table(f"Secrets in {namespace}", ["Name", "Type", "Data", "Age"])
            
            for secret in secrets:
                table.add_row(
                    secret.metadata.name,
                    secret.type,
                    str(len(secret.data or {})),
                    self._calculate_age(secret.metadata.creation_timestamp)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list secrets: {e}")
            raise
    
    def list_ingress(self, namespace: str):
        """List ingress resources"""
        try:
            ingresses = self.k8s.list_ingress(namespace)
            table = create_table(f"Ingress in {namespace}", ["Name", "Hosts", "Address", "Age"])
            
            for ing in ingresses:
                hosts = ",".join([rule.host for rule in ing.spec.rules or []])
                address = ",".join([lb.ip for lb in ing.status.load_balancer.ingress or []]) if ing.status.load_balancer else "<none>"
                
                table.add_row(
                    ing.metadata.name,
                    hosts or "*",
                    address,
                    self._calculate_age(ing.metadata.creation_timestamp)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list ingress: {e}")
            raise
    
    def list_volumes(self, namespace: str):
        """List persistent volume claims"""
        try:
            pvcs = self.k8s.list_pvcs(namespace)
            table = create_table(f"Persistent Volume Claims in {namespace}", ["Name", "Status", "Volume", "Capacity", "Access Modes", "Age"])
            
            for pvc in pvcs:
                table.add_row(
                    pvc.metadata.name,
                    pvc.status.phase,
                    pvc.spec.volume_name or "<pending>",
                    str(pvc.status.capacity.get('storage', 'N/A')) if pvc.status.capacity else "N/A",
                    ",".join(pvc.spec.access_modes or []),
                    self._calculate_age(pvc.metadata.creation_timestamp)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list volumes: {e}")
            raise
    
    def describe_resource(self, resource_type: str, resource_name: str, namespace: str):
        """Describe a resource"""
        try:
            resource = self.k8s.get_resource(resource_type, resource_name, namespace)
            console.print(f"\n[bold]Name:[/bold] {resource.metadata.name}")
            console.print(f"[bold]Namespace:[/bold] {resource.metadata.namespace or 'cluster-wide'}")
            console.print(f"[bold]Type:[/bold] {resource_type}")
            console.print(f"[bold]Created:[/bold] {resource.metadata.creation_timestamp}")
            
            if hasattr(resource, 'status'):
                console.print(f"\n[bold]Status:[/bold]")
                console.print(resource.status)
        except Exception as e:
            print_error(f"Failed to describe {resource_type}/{resource_name}: {e}")
            raise
    
    def top_pods(self, namespace: str, limit: int):
        """Show top resource-consuming pods"""
        try:
            metrics = self.k8s.get_pod_metrics(namespace)
            table = create_table(f"Top {limit} Pods by Resource Usage", ["Pod", "CPU", "Memory"])
            
            sorted_metrics = sorted(metrics, key=lambda x: x.containers[0].usage['cpu'], reverse=True)[:limit]
            
            for metric in sorted_metrics:
                cpu = metric.containers[0].usage.get('cpu', '0')
                memory = metric.containers[0].usage.get('memory', '0')
                table.add_row(metric.metadata.name, cpu, memory)
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to get metrics: {e}")
            raise
    
    def restart_resource(self, resource_type: str, resource_name: str, namespace: str):
        """Restart a resource"""
        try:
            self.k8s.restart_resource(resource_type, resource_name, namespace)
            print_success(f"Restarted {resource_type}/{resource_name}")
        except Exception as e:
            print_error(f"Failed to restart: {e}")
            raise
    
    def scale_resource(self, resource_type: str, resource_name: str, replicas: int, namespace: str):
        """Scale a resource"""
        try:
            self.k8s.scale_resource(resource_type, resource_name, replicas, namespace)
            print_success(f"Scaled {resource_type}/{resource_name} to {replicas} replicas")
        except Exception as e:
            print_error(f"Failed to scale: {e}")
            raise
    
    def exec_pod(self, pod_name: str, command: str, namespace: str, container: str = None):
        """Execute command in pod"""
        try:
            output = self.k8s.exec_in_pod(pod_name, command, namespace, container)
            console.print(output)
        except Exception as e:
            print_error(f"Failed to execute command: {e}")
            raise
    
    def port_forward(self, pod_name: str, port: str, namespace: str):
        """Port forward to pod"""
        try:
            console.print(f"[bold]Port forwarding {port} to {pod_name}...[/bold]")
            console.print("Press Ctrl+C to stop")
            self.k8s.port_forward_pod(pod_name, port, namespace)
        except Exception as e:
            print_error(f"Failed to port forward: {e}")
            raise
    
    def show_context(self):
        """Show current context"""
        try:
            context = self.k8s.get_current_context()
            console.print(f"\n[bold]Current Context:[/bold] {context['name']}")
            console.print(f"[bold]Cluster:[/bold] {context['context'].get('cluster', 'N/A')}")
            console.print(f"[bold]User:[/bold] {context['context'].get('user', 'N/A')}")
            console.print(f"[bold]Namespace:[/bold] {context['context'].get('namespace', 'default')}")
        except Exception as e:
            print_error(f"Failed to get context: {e}")
            raise
    
    def show_resources(self, namespace: str):
        """Show resource usage and quotas"""
        try:
            quotas = self.k8s.get_resource_quotas(namespace)
            usage = self.k8s.get_namespace_usage(namespace)
            
            console.print(f"\n[bold]Resource Usage for {namespace}[/bold]\n")
            
            table = create_table("Resources", ["Resource", "Used", "Limit", "Percentage"])
            for resource, values in usage.items():
                used = values.get('used', 'N/A')
                limit = values.get('limit', 'N/A')
                pct = values.get('percentage', 'N/A')
                table.add_row(resource, str(used), str(limit), str(pct))
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to get resources: {e}")
            raise
