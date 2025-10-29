"""Provide parameters for a Kubernetes Pod Operator."""

# pylint: disable=too-many-arguments
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-positional-arguments
from typing import Optional, List, Any, Dict
from kubernetes import client
from kubernetes.client import models as k8s

# pylint: disable-next=import-error,no-name-in-module
from airflow.providers.cncf.kubernetes.secret import Secret  # type: ignore

__LIMIT_MULTIPLIER = 1.5


class EphemeralVolume:
    """
    Represents an ephemeral storage volume to be mounted in a Kubernetes pod.
    Args:
        name (str): The name of the volume.
        size_in_Gi (float): The size of the volume in GiB.
        mount_path (str): The path at which to mount the volume in the pod.
        storage_class (str): The storage class to use for the volume.
    """

    def __init__(
        self, name: str, size_in_Gi: float, mount_path: str, storage_class: str
    ):
        self.name = name
        self.size_in_Gi = size_in_Gi
        self.mount_path = mount_path
        self.storage_class = storage_class


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
    """
    Generate parameters for a Kubernetes Pod Operator.
    Args:
        image (str): The Docker image to use for the pod.
        namespace (str): The Kubernetes namespace in which to create the pod. Defaults to 'default'.
        image_pull_secrets (List[str], optional): List of image pull secrets for private registries.
        secrets (List[str], optional): List of Kubernetes secret names to mount in the pod as env variables.
        configmaps (List[str], optional): List of Kubernetes configmap names to mount in the pod as env variables.
        cpus (float, optional): Number of CPU cores to allocate to the pod. Defaults to 1.0.
        memory_in_Gi (float, optional): Amount of memory in GiB to allocate to the pod. Defaults to 1.0.
        local_ephemeral_storage_in_Gi (float, optional): Amount of local ephemeral storage in GiB to allocate to the pod. Defaults to 1.0.
        startup_timeout_in_seconds (int, optional): Timeout in seconds for the pod to start up. Defaults to 120 seconds.
        large_ephemeral_storage_volume (Optional[EphemeralVolume], optional): Large ephemeral storage volume to allocate to the pod.
        env_vars (Dict, optional): Additional environment variables to set in the pod. Defaults to an empty dictionary.
    Returns:
        Dict: A dictionary containing the parameters for the Kubernetes Pod Operator.
    """

    if image_pull_secrets is None:
        image_pull_secrets = []

    if secrets is None:
        secrets = []

    if configmaps is None:
        configmaps = []

    if env_vars is None:
        env_vars = {}

    resources = __get_compute_resources(
        cpus, memory_in_Gi, local_ephemeral_storage_in_Gi
    )
    secrets = [__get_secret(secret_name) for secret_name in secrets]
    return __get_params_with_resources(
        image,
        namespace,
        image_pull_secrets,
        secrets,
        configmaps,
        resources,
        large_ephemeral_storage_volume,
        startup_timeout_in_seconds,
        env_vars,
    )


def __get_secret(secret_name: str) -> Secret:
    return Secret("env", None, secret_name)


def __get_compute_resources(
    cpus: float, memory_in_Gi: float, storage_in_Gi: float
) -> k8s.V1ResourceRequirements:
    return k8s.V1ResourceRequirements(
        requests={
            "memory": f"{memory_in_Gi}Gi",
            "cpu": str(cpus),
            "ephemeral-storage": f"{storage_in_Gi}Gi",
        },
        limits={
            "memory": f"{memory_in_Gi * __LIMIT_MULTIPLIER}Gi",
            "cpu": str(cpus * __LIMIT_MULTIPLIER),
            "ephemeral-storage": f"{storage_in_Gi * __LIMIT_MULTIPLIER}Gi",
        },
    )


def __get_ephemeral_storage_volume(
    name: str, size_in_Gi: float, storage_class: str
) -> client.V1Volume:
    return client.V1Volume(
        name=name,
        ephemeral=client.V1EphemeralVolumeSource(
            volume_claim_template=client.V1PersistentVolumeClaimTemplate(
                metadata=client.V1ObjectMeta(labels={"type": "ephemeral-storage"}),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    storage_class_name=storage_class,
                    resources=client.V1ResourceRequirements(
                        requests={"storage": f"{size_in_Gi}Gi"},
                        limits={"storage": f"{size_in_Gi * __LIMIT_MULTIPLIER}Gi"},
                    ),
                ),
            )
        ),
    )


def get_volume_mount_for(
    volume_name: str, mount_path: Optional[str] = None
) -> client.V1VolumeMount:
    """
    Get a volume mount for a Kubernetes pod.
    Args:
        volume_name (str): The name of the volume to mount.
        mount_path (str, optional): The path at which to mount the volume in the pod. Defaults to '/{volume_name}'.
    Returns:
        client.V1VolumeMount: The volume mount object.
    """
    if mount_path is None:
        mount_path = f"/{volume_name}"
    return client.V1VolumeMount(
        name=volume_name, read_only=False, mount_path=mount_path
    )


def __get_params_with_resources(
    image: str,
    namespace: str,
    image_pull_secrets: List[str],
    secrets: List[Secret],
    configmaps: List[str],
    compute_resources: k8s.V1ResourceRequirements,
    ephemeral_volume: Optional[EphemeralVolume],
    timeout_in_seconds: int,
    env_vars: Dict[str, str],
) -> Dict[str, Any]:

    volumes = []
    volume_mounts = []

    if ephemeral_volume is not None:
        # Ephemeral storage for duckdb file
        volumes.append(
            __get_ephemeral_storage_volume(
                ephemeral_volume.name,
                ephemeral_volume.size_in_Gi,
                ephemeral_volume.storage_class,
            )
        )
        volume_mounts.append(
            get_volume_mount_for(
                ephemeral_volume.name, mount_path=ephemeral_volume.mount_path
            )
        )

    # Define common parameters for KubernetesPodOperator tasks
    common_k8s_pod_operator_params = {
        "namespace": namespace,
        "image": image,
        "image_pull_policy": "Always",
        "image_pull_secrets": [k8s.V1LocalObjectReference(image_pull_secret) for image_pull_secret in image_pull_secrets],  # type: ignore [misc]
        "annotations": {"prometheus.io/scrape": "true"},
        "get_logs": True,
        "is_delete_operator_pod": True,
        "in_cluster": True,
        "configmaps": configmaps,
        "cmds": ["/bin/sh", "-cx"],
        "volumes": volumes,
        "volume_mounts": volume_mounts,
        "container_resources": compute_resources,
        "startup_timeout_seconds": timeout_in_seconds,
        "secrets": secrets,
        "env_vars": env_vars,
    }

    return common_k8s_pod_operator_params
