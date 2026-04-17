"""Provide parameters for a Kubernetes Pod Operator."""

# pylint: disable=too-many-arguments
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-positional-arguments
from typing import Optional, List, Any, Dict
from kubernetes.client import models as k8s

# pylint: disable-next=import-error,no-name-in-module
from airflow.providers.cncf.kubernetes.secret import Secret  # type: ignore

LIMIT_MULTIPLIER = 1.5


def get_pod_operator_params(
    image: str,
    namespace: str = "default",
    image_pull_secrets: Optional[List[str]] = None,
    secrets: Optional[List[str]] = None,
    configmaps: Optional[List[str]] = None,
    cpus: float = 1.0,
    memory_in_Gi: float = 1.0,
    storage_in_Gi: float = 1.0,
    startup_timeout_in_seconds: int = 2 * 60,
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
        storage_in_Gi (float, optional): Amount of storage in GiB to allocate to the pod. Defaults to 1.0.
        startup_timeout_in_seconds (int, optional): Timeout in seconds for the pod to start up. Defaults to 120 seconds.
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

    resources = __get_compute_resources(cpus, memory_in_Gi, storage_in_Gi)
    secrets = [__get_secret(secret_name) for secret_name in secrets]
    return __get_params_with_resources(
        image,
        namespace,
        image_pull_secrets,
        secrets,
        configmaps,
        resources,
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
            "memory": f"{memory_in_Gi * LIMIT_MULTIPLIER}Gi",
            "cpu": str(cpus * LIMIT_MULTIPLIER),
            "ephemeral-storage": f"{storage_in_Gi * LIMIT_MULTIPLIER}Gi",
        },
    )


def __get_params_with_resources(
    image: str,
    namespace: str,
    image_pull_secrets: List[str],
    secrets: List[Secret],
    configmaps: List[str],
    compute_resources: k8s.V1ResourceRequirements,
    timeout_in_seconds: int,
    env_vars: Dict[str, str],
) -> Dict[str, Any]:

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
        "container_resources": compute_resources,
        "startup_timeout_seconds": timeout_in_seconds,
        "secrets": secrets,
        "env_vars": env_vars,
    }

    return common_k8s_pod_operator_params
