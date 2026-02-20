"""Kubernetes API client wrapper with security and error handling"""
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException
import logging
from typing import Optional, List, Dict, Any
from functools import wraps
import time

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, backoff: float = 1.0):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ApiException as e:
                    if attempt == max_retries - 1:
                        raise
                    if e.status in [429, 500, 502, 503, 504]:
                        delay = backoff * (2 ** attempt)
                        logger.warning(f"API call failed, retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        raise
            return None
        return wrapper
    return decorator


class KubernetesClient:
    """Kubernetes API client with security and error handling"""
    
    def __init__(self):
        try:
            k8s_config.load_kube_config()
        except Exception as e:
            logger.error(f"Failed to load kubeconfig: {e}")
            raise
        
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.auth_v1 = client.AuthorizationV1Api()
    
    @retry_on_failure()
    def list_pods(self, namespace: Optional[str] = None) -> List[Any]:
        """List pods in namespace or all namespaces"""
        try:
            if namespace:
                return self.core_v1.list_namespaced_pod(namespace).items
            return self.core_v1.list_pod_for_all_namespaces().items
        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            raise
    
    @retry_on_failure()
    def get_pod(self, name: str, namespace: str = "default") -> Any:
        """Get specific pod"""
        try:
            return self.core_v1.read_namespaced_pod(name, namespace)
        except ApiException as e:
            logger.error(f"Failed to get pod {name}: {e}")
            raise
    
    @retry_on_failure()
    def list_nodes(self) -> List[Any]:
        """List all nodes"""
        try:
            return self.core_v1.list_node().items
        except ApiException as e:
            logger.error(f"Failed to list nodes: {e}")
            raise
    
    @retry_on_failure()
    def list_deployments(self, namespace: Optional[str] = None) -> List[Any]:
        """List deployments"""
        try:
            if namespace:
                return self.apps_v1.list_namespaced_deployment(namespace).items
            return self.apps_v1.list_deployment_for_all_namespaces().items
        except ApiException as e:
            logger.error(f"Failed to list deployments: {e}")
            raise
    
    @retry_on_failure()
    def list_namespaces(self) -> List[Any]:
        """List all namespaces"""
        try:
            return self.core_v1.list_namespace().items
        except ApiException as e:
            logger.error(f"Failed to list namespaces: {e}")
            raise
    
    @retry_on_failure()
    def get_pod_logs(self, name: str, namespace: str = "default", tail_lines: int = 100) -> str:
        """Get pod logs"""
        try:
            return self.core_v1.read_namespaced_pod_log(
                name, namespace, tail_lines=tail_lines
            )
        except ApiException as e:
            logger.error(f"Failed to get logs for {name}: {e}")
            raise
    
    @retry_on_failure()
    def delete_pod(self, name: str, namespace: str = "default"):
        """Delete a pod"""
        try:
            return self.core_v1.delete_namespaced_pod(name, namespace)
        except ApiException as e:
            logger.error(f"Failed to delete pod {name}: {e}")
            raise
    
    def check_rbac_permission(self, verb: str, resource: str, namespace: str = "") -> bool:
        """Check if user has RBAC permission"""
        try:
            review = client.V1SelfSubjectAccessReview(
                spec=client.V1SelfSubjectAccessReviewSpec(
                    resource_attributes=client.V1ResourceAttributes(
                        verb=verb,
                        resource=resource,
                        namespace=namespace
                    )
                )
            )
            result = self.auth_v1.create_self_subject_access_review(review)
            return result.status.allowed
        except Exception as e:
            logger.warning(f"RBAC check failed: {e}")
            return False
    
    @retry_on_failure()
    def get_pod_logs(self, name: str, namespace: str, tail: int = 50):
        """Get pod logs"""
        try:
            return self.core_v1.read_namespaced_pod_log(name, namespace, tail_lines=tail)
        except ApiException as e:
            logger.error(f"Failed to get logs for {name}: {e}")
            raise
    
    @retry_on_failure()
    def list_events(self, namespace: str = "default"):
        """List events in namespace"""
        try:
            events = self.core_v1.list_namespaced_event(namespace)
            return sorted(events.items, key=lambda x: x.last_timestamp or x.event_time, reverse=True)
        except ApiException as e:
            logger.error(f"Failed to list events: {e}")
            raise
    
    @retry_on_failure()
    def list_deployments(self, namespace: str = "default"):
        """List deployments"""
        try:
            return self.apps_v1.list_namespaced_deployment(namespace).items
        except ApiException as e:
            logger.error(f"Failed to list deployments: {e}")
            raise
    
    @retry_on_failure()
    def list_services(self, namespace: str = "default"):
        """List services"""
        try:
            return self.core_v1.list_namespaced_service(namespace).items
        except ApiException as e:
            logger.error(f"Failed to list services: {e}")
            raise

    @retry_on_failure()
    def list_namespaces(self):
        """List all namespaces"""
        try:
            return self.core_v1.list_namespace().items
        except ApiException as e:
            logger.error(f"Failed to list namespaces: {e}")
            raise
    
    @retry_on_failure()
    def list_configmaps(self, namespace: str = "default"):
        """List configmaps"""
        try:
            return self.core_v1.list_namespaced_config_map(namespace).items
        except ApiException as e:
            logger.error(f"Failed to list configmaps: {e}")
            raise
    
    @retry_on_failure()
    def list_secrets(self, namespace: str = "default"):
        """List secrets"""
        try:
            return self.core_v1.list_namespaced_secret(namespace).items
        except ApiException as e:
            logger.error(f"Failed to list secrets: {e}")
            raise
    
    @retry_on_failure()
    def list_ingress(self, namespace: str = "default"):
        """List ingress resources"""
        try:
            return self.networking_v1.list_namespaced_ingress(namespace).items
        except ApiException as e:
            logger.error(f"Failed to list ingress: {e}")
            raise
    
    @retry_on_failure()
    def list_pvcs(self, namespace: str = "default"):
        """List persistent volume claims"""
        try:
            return self.core_v1.list_namespaced_persistent_volume_claim(namespace).items
        except ApiException as e:
            logger.error(f"Failed to list PVCs: {e}")
            raise
    
    @retry_on_failure()
    def get_resource(self, resource_type: str, name: str, namespace: str):
        """Get a specific resource"""
        try:
            if resource_type == "pod":
                return self.core_v1.read_namespaced_pod(name, namespace)
            elif resource_type == "deployment":
                return self.apps_v1.read_namespaced_deployment(name, namespace)
            elif resource_type == "service":
                return self.core_v1.read_namespaced_service(name, namespace)
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
        except ApiException as e:
            logger.error(f"Failed to get {resource_type}/{name}: {e}")
            raise
    
    @retry_on_failure()
    def get_pod_metrics(self, namespace: str = "default"):
        """Get pod metrics"""
        try:
            return self.custom_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )['items']
        except ApiException as e:
            logger.error(f"Failed to get pod metrics: {e}")
            raise
    
    @retry_on_failure()
    def restart_resource(self, resource_type: str, name: str, namespace: str):
        """Restart a resource by updating annotation"""
        try:
            from datetime import datetime
            patch = {
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {
                                "kubectl.kubernetes.io/restartedAt": datetime.utcnow().isoformat()
                            }
                        }
                    }
                }
            }
            
            if resource_type == "deployment":
                self.apps_v1.patch_namespaced_deployment(name, namespace, patch)
            elif resource_type == "statefulset":
                self.apps_v1.patch_namespaced_stateful_set(name, namespace, patch)
            else:
                raise ValueError(f"Cannot restart {resource_type}")
        except ApiException as e:
            logger.error(f"Failed to restart {resource_type}/{name}: {e}")
            raise
    
    @retry_on_failure()
    def scale_resource(self, resource_type: str, name: str, replicas: int, namespace: str):
        """Scale a resource"""
        try:
            patch = {"spec": {"replicas": replicas}}
            
            if resource_type == "deployment":
                self.apps_v1.patch_namespaced_deployment_scale(name, namespace, patch)
            elif resource_type == "statefulset":
                self.apps_v1.patch_namespaced_stateful_set_scale(name, namespace, patch)
            else:
                raise ValueError(f"Cannot scale {resource_type}")
        except ApiException as e:
            logger.error(f"Failed to scale {resource_type}/{name}: {e}")
            raise
    
    def exec_in_pod(self, pod_name: str, command: str, namespace: str, container: str = None):
        """Execute command in pod"""
        try:
            from kubernetes.stream import stream
            exec_command = ['/bin/sh', '-c', command]
            
            resp = stream(
                self.core_v1.connect_get_namespaced_pod_exec,
                pod_name,
                namespace,
                container=container,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False
            )
            return resp
        except Exception as e:
            logger.error(f"Failed to exec in pod: {e}")
            raise
    
    def port_forward_pod(self, pod_name: str, port: str, namespace: str):
        """Port forward to pod"""
        try:
            import subprocess
            local_port, remote_port = port.split(':')
            cmd = ['kubectl', 'port-forward', f'pod/{pod_name}', f'{local_port}:{remote_port}', '-n', namespace]
            subprocess.run(cmd)
        except Exception as e:
            logger.error(f"Failed to port forward: {e}")
            raise
    
    def get_current_context(self):
        """Get current context"""
        try:
            from kubernetes import config as k8s_config
            contexts, active_context = k8s_config.list_kube_config_contexts()
            return active_context
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            raise
    
    def get_resource_quotas(self, namespace: str):
        """Get resource quotas"""
        try:
            return self.core_v1.list_namespaced_resource_quota(namespace).items
        except ApiException as e:
            logger.error(f"Failed to get quotas: {e}")
            raise
    
    def get_namespace_usage(self, namespace: str):
        """Get namespace resource usage"""
        try:
            pods = self.list_pods(namespace)
            usage = {'pods': len(pods), 'cpu': 0, 'memory': 0}
            return usage
        except Exception as e:
            logger.error(f"Failed to get usage: {e}")
            raise
