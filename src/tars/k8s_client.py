"""Kubernetes API client wrapper with security and error handling"""
from kubernetes import client, config as k8s_config, utils
from kubernetes.client.rest import ApiException
import logging
from typing import Optional, List, Dict, Any
from functools import wraps
import time
import yaml

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
        self.networking_v1 = client.NetworkingV1Api()
        self.api_extensions = client.ApiextensionsV1Api()
        self.custom_api = client.CustomObjectsApi()
        self.api_client = client.ApiClient()
    
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

    def rollback_resource(self, resource_type: str, name: str, namespace: str):
        """Rollback a resource"""
        try:
            if resource_type == "deployment":
                self.apps_v1.rollback_namespaced_deployment(name, namespace, {})
            else:
                raise ValueError(f"Rollback not supported for {resource_type}")
        except ApiException as e:
            logger.error(f"Failed to rollback: {e}")
            raise
    
    def cordon_node(self, node_name: str):
        """Cordon a node"""
        try:
            patch = {"spec": {"unschedulable": True}}
            self.core_v1.patch_node(node_name, patch)
        except ApiException as e:
            logger.error(f"Failed to cordon node: {e}")
            raise
    
    def uncordon_node(self, node_name: str):
        """Uncordon a node"""
        try:
            patch = {"spec": {"unschedulable": False}}
            self.core_v1.patch_node(node_name, patch)
        except ApiException as e:
            logger.error(f"Failed to uncordon node: {e}")
            raise
    
    def drain_node(self, node_name: str, force: bool):
        """Drain a node"""
        try:
            import subprocess
            cmd = ['kubectl', 'drain', node_name, '--ignore-daemonsets', '--delete-emptydir-data']
            if force:
                cmd.append('--force')
            subprocess.run(cmd, check=True)
        except Exception as e:
            logger.error(f"Failed to drain node: {e}")
            raise
    
    def list_crds(self):
        """List CRDs"""
        try:
            return self.api_extensions.list_custom_resource_definition().items
        except ApiException as e:
            logger.error(f"Failed to list CRDs: {e}")
            raise
    
    def list_network_policies(self, namespace: str):
        """List network policies"""
        try:
            return self.networking_v1.list_namespaced_network_policy(namespace).items
        except ApiException as e:
            logger.error(f"Failed to list network policies: {e}")
            raise
    
    def get_deployment_history(self, name: str, namespace: str):
        """Get deployment history"""
        try:
            import subprocess
            result = subprocess.run(
                ['kubectl', 'rollout', 'history', f'deployment/{name}', '-n', namespace],
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            raise
    
    def apply_yaml(self, file_path: str, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Apply YAML file to cluster"""
        try:
            with open(file_path, 'r') as f:
                resources = list(yaml.safe_load_all(f))
            
            results = []
            for resource in resources:
                if not resource:
                    continue
                
                # Override namespace if specified
                if namespace and 'metadata' in resource:
                    resource['metadata']['namespace'] = namespace
                
                # Apply resource
                result = utils.create_from_dict(self.api_client, resource, namespace=namespace)
                results.append({
                    'kind': resource.get('kind'),
                    'name': resource.get('metadata', {}).get('name'),
                    'namespace': resource.get('metadata', {}).get('namespace', 'default'),
                    'status': 'created'
                })
            
            return results
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to apply YAML: {e}")
            raise
    
    def create_from_yaml(self, file_path: str, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Create resources from YAML file (fails if exists)"""
        return self.apply_yaml(file_path, namespace)
    
    def delete_from_yaml(self, file_path: str, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Delete resources defined in YAML file"""
        try:
            with open(file_path, 'r') as f:
                resources = list(yaml.safe_load_all(f))
            
            results = []
            for resource in resources:
                if not resource:
                    continue
                
                kind = resource.get('kind')
                name = resource.get('metadata', {}).get('name')
                ns = namespace or resource.get('metadata', {}).get('namespace', 'default')
                
                # Delete based on kind
                try:
                    if kind == 'Deployment':
                        self.apps_v1.delete_namespaced_deployment(name, ns)
                    elif kind == 'Service':
                        self.core_v1.delete_namespaced_service(name, ns)
                    elif kind == 'ConfigMap':
                        self.core_v1.delete_namespaced_config_map(name, ns)
                    elif kind == 'Secret':
                        self.core_v1.delete_namespaced_secret(name, ns)
                    elif kind == 'Pod':
                        self.core_v1.delete_namespaced_pod(name, ns)
                    elif kind == 'Ingress':
                        self.networking_v1.delete_namespaced_ingress(name, ns)
                    else:
                        logger.warning(f"Unsupported kind for deletion: {kind}")
                        continue
                    
                    results.append({
                        'kind': kind,
                        'name': name,
                        'namespace': ns,
                        'status': 'deleted'
                    })
                except ApiException as e:
                    if e.status == 404:
                        results.append({
                            'kind': kind,
                            'name': name,
                            'namespace': ns,
                            'status': 'not_found'
                        })
                    else:
                        raise
            
            return results
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to delete from YAML: {e}")
            raise
