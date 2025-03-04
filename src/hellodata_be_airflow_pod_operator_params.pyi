"""Provide parameters for a Kubernetes Pod Operator."""

# pylint: disable-all
from typing import Any

class EphemeralVolume:
    """
    Represents an ephemeral storage volume to be mounted in a Kubernetes pod.
    Args:
        name (str): The name of the volume.
        size_in_Gi (float): The size of the volume in GiB.
        mount_path (str): The path at which to mount the volume in the pod.
        storage_class (str): The storage class to use for the volume.
    """

    name: str
    size_in_Gi: float
    mount_path: str
    storage_class: str
    def __init__(
        self, name: str, size_in_Gi: float, mount_path: str, storage_class: str
    ) -> None: ...

def get_pod_operator_params(
    image: str,
    namespace: str,
    secret_names: list[str] | None = None,
    configmap_names: list[str] | None = None,
    cpus: float = 1.0,
    memory_in_Gi: float = 1.0,
    mount_storage_hellodata_pvc: bool = True,
    local_ephemeral_storage_in_Gi: float = 1.0,
    startup_timeout_in_seconds: int = ...,
    large_ephemeral_storage_volume: EphemeralVolume | None = None,
    env_vars: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Generate parameters for a Kubernetes Pod Operator.
    Args:
        image (str): The Docker image to use for the pod.
        namespace (str): The Kubernetes namespace in which to create the pod.
        secret_names (List[str], optional): List of Kubernetes secret names to mount in the pod as env variables.
        configmap_names (List[str], optional): List of Kubernetes configmap names to mount in the pod as env variables.
        cpus (float, optional): Number of CPU cores to allocate to the pod. Defaults to 1.0.
        memory_in_Gi (float, optional): Amount of memory in GiB to allocate to the pod. Defaults to 1.0.
        mount_storage_hellodata_pvc (bool, optional): Whether to mount the storage-hellodata volume under /mnt/storage-hellodata.
        local_ephemeral_storage_in_Gi (float, optional): Amount of local ephemeral storage in GiB to allocate to the pod. Defaults to 1.0.
        startup_timeout_in_seconds (int, optional): Timeout in seconds for the pod to start up. Defaults to 120 seconds.
        large_ephemeral_storage_volume (Optional[EphemeralVolume], optional): Large ephemeral storage volume to allocate to the pod.
        env_vars (dict, optional): Additional environment variables to set in the pod. Defaults to an empty dictionary.
    Returns:
        dict: A dictionary containing the parameters for the Kubernetes Pod Operator.
    """
    ...
