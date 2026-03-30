# get_pod_operator_params Function Documentation

## Overview

The `get_pod_operator_params` function generates parameters for a Kubernetes Pod Operator. This function creates a comprehensive configuration dictionary that can be used to deploy pods in a Kubernetes cluster with specific resource requirements, secrets, configmaps, and storage configurations.

## Function Signature

```python
def get_pod_operator_params(
    image: str,
    namespace: str = "default",
    image_pull_secrets: Optional[List[str]] = None,
    secrets: Optional[List[str]] = None,
    configmaps: Optional[List[str]] = None,
    cpus: float = 1.0,
    memory_in_Gi: float = 1.0,
    local_ephemeral_storage_in_Gi: float = 1.0,
    startup_timeout_in_seconds: int = 2 * 60,
    large_ephemeral_storage_volume: Optional[EphemeralVolume] = None,
    env_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `str` | `true` | - | The Docker image to use for the pod |
| `namespace` | `str` | `false` | `"default"` | The Kubernetes namespace in which to create the pod |
| `image_pull_secrets` | `Optional[List[str]]` | `false` | `None` | List of image pull secrets for private registries |
| `secrets` | `Optional[List[str]]` | `false` | `None` | List of Kubernetes secret names to mount in the pod as environment variables |
| `configmaps` | `Optional[List[str]]` | `false` | `None` | List of Kubernetes configmap names to mount in the pod as environment variables |
| `cpus` | `float` | `false` | `1.0` | Number of CPU cores to allocate to the pod |
| `memory_in_Gi` | `float` | `false` | `1.0` | Amount of memory in GiB to allocate to the pod |
| `local_ephemeral_storage_in_Gi` | `float` | `false` | `1.0` | Amount of local ephemeral storage in GiB to allocate to the pod |
| `startup_timeout_in_seconds` | `int` | `false` | `120` | Timeout in seconds for the pod to start up |
| `large_ephemeral_storage_volume` | `Optional[EphemeralVolume]` | `false` | `None` | Large ephemeral storage volume to allocate to the pod |
| `env_vars` | `Optional[Dict[str, str]]` | `false` | `None` | Additional environment variables to set in the pod |

## Return Value

**Type:** `Dict[str, Any]`

**Description:** A dictionary containing the parameters for the Kubernetes Pod Operator, including:

- `namespace`: The Kubernetes namespace
- `image`: The Docker image
- `image_pull_policy`: Set to "Always"
- `image_pull_secrets`: Configured image pull secrets
- `annotations`: Prometheus scraping annotations
- `get_logs`: Set to `True`
- `is_delete_operator_pod`: Set to `True`
- `in_cluster`: Set to `True`
- `configmaps`: List of configmap names
- `cmds`: Default command `["/bin/sh", "-cx"]`
- `volumes`: Configured volumes (including ephemeral storage if specified)
- `volume_mounts`: Configured volume mounts
- `container_resources`: CPU, memory, and storage resource requirements
- `startup_timeout_seconds`: Pod startup timeout
- `secrets`: Configured secrets as environment variables
- `env_vars`: Additional environment variables

## Resource Management

The function automatically configures resource requests and limits with a multiplier of **1.5x** for limits:

- **CPU**: Request = `cpus`, Limit = `cpus * 1.5`
- **Memory**: Request = `memory_in_Gi`, Limit = `memory_in_Gi * 1.5`
- **Ephemeral Storage**: Request = `local_ephemeral_storage_in_Gi`, Limit = `local_ephemeral_storage_in_Gi * 1.5`

## Usage Examples

### Basic Usage

```python
from hellodata_be_airflow_pod_operator_params import get_pod_operator_params

# Simple pod configuration
params = get_pod_operator_params(
    image="my-app:latest"
)
```

### Advanced Usage

```python
from hellodata_be_airflow_pod_operator_params import get_pod_operator_params, EphemeralVolume

# Advanced pod configuration with custom resources and storage
large_storage = EphemeralVolume(
    name="data-volume",
    size_in_Gi=10.0,
    mount_path="/data",
    storage_class="fast-ssd"
)

params = get_pod_operator_params(
    image="my-data-processor:v2.1.0",
    namespace="data-processing",
    image_pull_secrets=["registry-secret"],
    secrets=["db-credentials", "api-keys"],
    configmaps=["app-config"],
    cpus=2.0,
    memory_in_Gi=4.0,
    local_ephemeral_storage_in_Gi=2.0,
    startup_timeout_in_seconds=300,
    large_ephemeral_storage_volume=large_storage,
    env_vars={
        "LOG_LEVEL": "INFO",
        "ENVIRONMENT": "production"
    }
)
```

## Related Classes

### EphemeralVolume

The `EphemeralVolume` class is used to define large ephemeral storage volumes:

```python
class EphemeralVolume:
    def __init__(
        self,
        name: str,
        size_in_Gi: float,
        mount_path: str,
        storage_class: str
    ):
        # Class implementation
```

## Notes

- All optional list and dictionary parameters are automatically initialized to empty collections if `None` is provided
- The function sets up Kubernetes Pod Operator parameters compatible with Airflow's `KubernetesPodOperator`
- Resource limits are automatically calculated as 1.5x the requested resources
- Secrets are automatically configured as environment variables
- The pod is configured to run in-cluster with log collection enabled
