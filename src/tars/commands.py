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

    def watch_pods(self, namespace: str, interval: int):
        """Watch pods in real-time"""
        import time
        try:
            while True:
                console.clear()
                self.list_pods(namespace)
                console.print(f"\n[dim]Refreshing every {interval}s... Press Ctrl+C to stop[/dim]")
                time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped watching[/yellow]")
    
    def analyze_cluster(self, namespace: str):
        """Analyze cluster with AI"""
        try:
            pods = self.k8s.list_pods(namespace)
            events = self.k8s.list_events(namespace)
            
            if analyzer.is_available():
                analysis = analyzer.analyze_cluster_health({
                    'pods': len(pods),
                    'events': len(events)
                })
                console.print(f"\n[bold]AI Analysis:[/bold]\n{analysis}")
            else:
                print_warning("AI analysis not available - GEMINI_API_KEY not set")
        except Exception as e:
            print_error(f"Analysis failed: {e}")
            raise
    
    def show_errors(self, namespace: str, limit: int):
        """Show pods with errors"""
        try:
            pods = self.k8s.list_pods(namespace)
            error_pods = [p for p in pods if p.status.phase in ['Failed', 'Unknown']]
            
            table = create_table(f"Error Pods in {namespace}", ["Name", "Status", "Reason", "Message"])
            for pod in error_pods[:limit]:
                reason = pod.status.reason or "N/A"
                message = pod.status.message or "N/A"
                table.add_row(pod.metadata.name, pod.status.phase, reason, message[:50])
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to show errors: {e}")
            raise
    
    def find_crashloop(self, namespace: str):
        """Find CrashLoopBackOff pods"""
        try:
            pods = self.k8s.list_pods(namespace)
            crashloop_pods = []
            
            for pod in pods:
                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        if container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff":
                            crashloop_pods.append((pod, container))
            
            table = create_table(f"CrashLoopBackOff Pods in {namespace}", ["Pod", "Container", "Restarts", "Message"])
            for pod, container in crashloop_pods:
                table.add_row(
                    pod.metadata.name,
                    container.name,
                    str(container.restart_count),
                    container.state.waiting.message[:50] if container.state.waiting.message else "N/A"
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to find crashloop pods: {e}")
            raise
    
    def find_pending(self, namespace: str):
        """Find pending pods"""
        try:
            pods = self.k8s.list_pods(namespace)
            pending_pods = [p for p in pods if p.status.phase == 'Pending']
            
            table = create_table(f"Pending Pods in {namespace}", ["Name", "Reason", "Message"])
            for pod in pending_pods:
                reason = pod.status.reason or "N/A"
                message = pod.status.message or "N/A"
                table.add_row(pod.metadata.name, reason, message[:60])
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to find pending pods: {e}")
            raise
    
    def find_oom(self, namespace: str):
        """Find OOMKilled pods"""
        try:
            pods = self.k8s.list_pods(namespace)
            oom_pods = []
            
            for pod in pods:
                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        if container.last_state.terminated and container.last_state.terminated.reason == "OOMKilled":
                            oom_pods.append((pod, container))
            
            table = create_table(f"OOMKilled Pods in {namespace}", ["Pod", "Container", "Exit Code", "Finished At"])
            for pod, container in oom_pods:
                table.add_row(
                    pod.metadata.name,
                    container.name,
                    str(container.last_state.terminated.exit_code),
                    str(container.last_state.terminated.finished_at)
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to find OOM pods: {e}")
            raise
    
    def rollback_resource(self, resource_type: str, resource_name: str, namespace: str):
        """Rollback a resource"""
        try:
            self.k8s.rollback_resource(resource_type, resource_name, namespace)
            print_success(f"Rolled back {resource_type}/{resource_name}")
        except Exception as e:
            print_error(f"Rollback failed: {e}")
            raise
    
    def cordon_node(self, node_name: str):
        """Cordon a node"""
        try:
            self.k8s.cordon_node(node_name)
            print_success(f"Cordoned node {node_name}")
        except Exception as e:
            print_error(f"Failed to cordon: {e}")
            raise
    
    def uncordon_node(self, node_name: str):
        """Uncordon a node"""
        try:
            self.k8s.uncordon_node(node_name)
            print_success(f"Uncordoned node {node_name}")
        except Exception as e:
            print_error(f"Failed to uncordon: {e}")
            raise
    
    def drain_node(self, node_name: str, force: bool):
        """Drain a node"""
        try:
            self.k8s.drain_node(node_name, force)
            print_success(f"Drained node {node_name}")
        except Exception as e:
            print_error(f"Failed to drain: {e}")
            raise
    
    def show_quota(self, namespace: str):
        """Show resource quotas"""
        try:
            quotas = self.k8s.get_resource_quotas(namespace)
            
            if not quotas:
                console.print(f"[yellow]No quotas found in {namespace}[/yellow]")
                return
            
            for quota in quotas:
                console.print(f"\n[bold]Quota: {quota.metadata.name}[/bold]")
                table = create_table("Resources", ["Resource", "Used", "Hard"])
                
                for resource, hard in (quota.spec.hard or {}).items():
                    used = quota.status.used.get(resource, "0") if quota.status.used else "0"
                    table.add_row(resource, str(used), str(hard))
                
                console.print(table)
        except Exception as e:
            print_error(f"Failed to show quota: {e}")
            raise
    
    def list_crds(self):
        """List CRDs"""
        try:
            crds = self.k8s.list_crds()
            table = create_table("Custom Resource Definitions", ["Name", "Group", "Version", "Scope"])
            
            for crd in crds:
                table.add_row(
                    crd.metadata.name,
                    crd.spec.group,
                    ",".join([v.name for v in crd.spec.versions]),
                    crd.spec.scope
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to list CRDs: {e}")
            raise
    
    def show_network(self, namespace: str):
        """Show network policies"""
        try:
            policies = self.k8s.list_network_policies(namespace)
            
            if not policies:
                console.print(f"[yellow]No network policies in {namespace}[/yellow]")
                return
            
            table = create_table(f"Network Policies in {namespace}", ["Name", "Pod Selector", "Policy Types"])
            for policy in policies:
                selector = str(policy.spec.pod_selector.match_labels) if policy.spec.pod_selector else "All"
                types = ",".join(policy.spec.policy_types or [])
                table.add_row(policy.metadata.name, selector, types)
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to show network: {e}")
            raise
    
    def estimate_cost(self, namespace: str):
        """Estimate costs"""
        try:
            pods = self.k8s.list_pods(namespace)
            console.print(f"\n[bold]Cost Estimation for {namespace or 'all namespaces'}[/bold]")
            console.print(f"Total Pods: {len(pods)}")
            console.print("[dim]Note: Detailed cost estimation requires metrics server[/dim]")
        except Exception as e:
            print_error(f"Failed to estimate cost: {e}")
            raise
    
    def show_audit(self, namespace: str, hours: int):
        """Show audit logs"""
        try:
            events = self.k8s.list_events(namespace)
            console.print(f"\n[bold]Audit Events (last {hours}h)[/bold]")
            
            table = create_table("Events", ["Time", "Type", "Reason", "Object"])
            for event in events[:50]:
                table.add_row(
                    self._calculate_age(event.last_timestamp or event.event_time),
                    event.type,
                    event.reason,
                    f"{event.involved_object.kind}/{event.involved_object.name}"
                )
            
            console.print(table)
        except Exception as e:
            print_error(f"Failed to show audit: {e}")
            raise
    
    def security_scan(self, namespace: str):
        """Security scan"""
        try:
            pods = self.k8s.list_pods(namespace)
            issues = []
            
            for pod in pods:
                if pod.spec.security_context is None:
                    issues.append(f"{pod.metadata.name}: No security context")
                if pod.spec.containers:
                    for container in pod.spec.containers:
                        if container.security_context is None or not container.security_context.run_as_non_root:
                            issues.append(f"{pod.metadata.name}/{container.name}: Running as root")
            
            console.print(f"\n[bold]Security Issues in {namespace}[/bold]")
            for issue in issues[:20]:
                console.print(f"⚠ {issue}")
        except Exception as e:
            print_error(f"Security scan failed: {e}")
            raise
    
    def check_compliance(self, namespace: str):
        """Check compliance"""
        try:
            pods = self.k8s.list_pods(namespace)
            deployments = self.k8s.list_deployments(namespace)
            
            console.print(f"\n[bold]Compliance Check for {namespace}[/bold]\n")
            
            checks = {
                "Pods with resource limits": sum(1 for p in pods if p.spec.containers[0].resources.limits),
                "Deployments with replicas > 1": sum(1 for d in deployments if d.spec.replicas > 1),
                "Total pods": len(pods),
                "Total deployments": len(deployments)
            }
            
            for check, value in checks.items():
                console.print(f"✓ {check}: {value}")
        except Exception as e:
            print_error(f"Compliance check failed: {e}")
            raise
    
    def export_resources(self, output_file: str, namespace: str, format: str):
        """Export resources"""
        try:
            import yaml, json
            
            resources = {
                'pods': [self.k8s.api_client.sanitize_for_serialization(p) for p in self.k8s.list_pods(namespace)],
                'deployments': [self.k8s.api_client.sanitize_for_serialization(d) for d in self.k8s.list_deployments(namespace)],
                'services': [self.k8s.api_client.sanitize_for_serialization(s) for s in self.k8s.list_services(namespace)]
            }
            
            with open(output_file, 'w') as f:
                if format == 'json':
                    json.dump(resources, f, indent=2)
                else:
                    yaml.dump(resources, f)
            
            print_success(f"Exported resources to {output_file}")
        except Exception as e:
            print_error(f"Export failed: {e}")
            raise
    
    def show_diff(self, resource_type: str, resource_name: str, file_path: str, namespace: str):
        """Show diff"""
        try:
            console.print(f"[yellow]Diff functionality requires kubectl diff[/yellow]")
            console.print(f"Run: kubectl diff -f {file_path}")
        except Exception as e:
            print_error(f"Diff failed: {e}")
            raise
    
    def show_history(self, resource_type: str, resource_name: str, namespace: str):
        """Show rollout history"""
        try:
            if resource_type == "deployment":
                history = self.k8s.get_deployment_history(resource_name, namespace)
                console.print(f"\n[bold]Rollout History for {resource_name}[/bold]")
                console.print(history)
            else:
                console.print(f"[yellow]History only supported for deployments[/yellow]")
        except Exception as e:
            print_error(f"Failed to show history: {e}")
            raise
    
    def triage_issues(self, namespace: str):
        """AI-powered triage"""
        try:
            pods = self.k8s.list_pods(namespace)
            problem_pods = [p for p in pods if p.status.phase != 'Running']
            
            if not problem_pods:
                console.print(f"[green]No issues found in {namespace}[/green]")
                return
            
            console.print(f"\n[bold]Issues Found:[/bold]")
            for pod in problem_pods:
                console.print(f"• {pod.metadata.name}: {pod.status.phase}")
            
            if analyzer.is_available():
                console.print("\n[bold]AI Recommendations:[/bold]")
                for pod in problem_pods[:3]:
                    analysis = analyzer.analyze_pod_issue(self._extract_pod_data(pod))
                    console.print(f"\n{pod.metadata.name}:\n{analysis}")
        except Exception as e:
            print_error(f"Triage failed: {e}")
            raise
    
    def show_metrics(self, namespace: str, resource: str):
        """Show metrics"""
        try:
            if resource == "pods":
                metrics = self.k8s.get_pod_metrics(namespace)
                table = create_table(f"Pod Metrics in {namespace}", ["Pod", "CPU", "Memory"])
                
                for metric in metrics[:20]:
                    if metric.get('containers'):
                        cpu = metric['containers'][0]['usage'].get('cpu', 'N/A')
                        memory = metric['containers'][0]['usage'].get('memory', 'N/A')
                        table.add_row(metric['metadata']['name'], cpu, memory)
                
                console.print(table)
            else:
                console.print(f"[yellow]Metrics for {resource} not yet implemented[/yellow]")
        except Exception as e:
            print_error(f"Failed to show metrics: {e}")
            raise
