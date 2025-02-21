from kubernetes import client
from kubernetes.client import models as k8s
from airflow.kubernetes.secret import Secret
from typing import Optional, List
import os

__LIMIT_MULTIPLIER = 1.5

class EphemeralVolume:
    def __init__(self, name: str, size_in_Gi: float, mount_path: str, storage_class: str):
        self.name = name
        self.size_in_Gi = size_in_Gi
        self.mount_path = mount_path
        self.storage_class = storage_class

def get_pod_operator_params(
    image: str,
    namespace: str,
    secret_names: List[str] = [],
    configmap_names: List[str] = [],
    cpus: float = 1.0, 
    memory_in_Gi: float = 1.0, 
    mount_storage_hellodata_pvc: bool = True,
    local_ephemeral_storage_in_Gi: float = 1.0,
    startup_timeout_in_seconds: int = 2 * 60,
    large_ephemeral_storage_in_Gi: Optional[EphemeralVolume] = None,
    env_vars: dict = {}
    ) -> dict:
    """
    Generate parameters for a Kubernetes Pod Operator.
    Args:
        image (str): The Docker image to use for the pod.
        secret_names (List[str], optional): List of Kubernetes secret names to mount in the pod as env variables. Defaults to an empty list.
        configmap_names (List[str], optional): List of Kubernetes configmap names to mount in the pod as env variables. Defaults to an empty list.
        cpus (float, optional): Number of CPU cores to allocate to the pod. Defaults to 1.0.
        memory_in_Gi (float, optional): Amount of memory in GiB to allocate to the pod. Defaults to 1.0.
        mount_storage_hellodata_pvc (bool, optional): Whether to mount the storage-hellodata volume under /mnt/storage-hellodata. Defaults to True.
        local_ephemeral_storage_in_Gi (float, optional): Amount of local ephemeral storage in GiB to allocate to the pod. Defaults to 1.0.
        startup_timeout_in_seconds (int, optional): Timeout in seconds for the pod to start up. Defaults to 120 seconds.
        large_ephemeral_storage_in_Gi (Optional[EphemeralVolume], optional): Additional large ephemeral storage volume to allocate to the pod. Defaults to None.
        env_vars (dict, optional): Additional environment variables to set in the pod. Defaults to an empty dictionary.
    Returns:
        dict: A dictionary containing the parameters for the Kubernetes Pod Operator.
    """
    
    resources = __get_compute_resources(cpus, memory_in_Gi, local_ephemeral_storage_in_Gi)
    secrets = [__get_secret(secret_name) for secret_name in secret_names]
    return __get_params_with_resources(image, namespace, secrets, configmap_names, resources, large_ephemeral_storage_in_Gi, startup_timeout_in_seconds, mount_storage_hellodata_pvc, env_vars)

def __get_secret(secret_name: str):
    return Secret('env', None, secret_name)
    
def __get_compute_resources(cpus: float, memory_in_Gi: float, storage_in_Gi: float):
    return k8s.V1ResourceRequirements(
        requests={
            'memory': f'{memory_in_Gi}Gi',
            'cpu': str(cpus),
            'ephemeral-storage': f'{storage_in_Gi}Gi'
        },
        limits={
            'memory': f'{memory_in_Gi * __LIMIT_MULTIPLIER}Gi',
            'cpu': str(cpus * __LIMIT_MULTIPLIER),
            'ephemeral-storage': f'{storage_in_Gi * __LIMIT_MULTIPLIER}Gi'
        }
    ) 

def __get_ephemeral_storage_volume(name: str, size_in_Gi: int, storage_class: str):
    return client.V1Volume(
        name=name,
        ephemeral=client.V1EphemeralVolumeSource(
            volume_claim_template=client.V1PersistentVolumeClaimTemplate(
                metadata=client.V1ObjectMeta(
                    labels={"type": "ephemeral-storage"}
                ),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    storage_class_name=storage_class,
                    resources=client.V1ResourceRequirements(
                        requests={"storage": f"{size_in_Gi}Gi"},
                        limits={"storage": f"{size_in_Gi * __LIMIT_MULTIPLIER}Gi"}
                    )
                )
            )
        )
    )
def __get_volume_mount_for(volume_name: str, mount_path: str = None):
    if mount_path is None:
        mount_path = f"/{volume_name}"
    return client.V1VolumeMount(name=volume_name, read_only=False, mount_path=mount_path)

def __get_params_with_resources(
    image: str,
    namespace: str,
    secrets: List[Secret],
    configmaps: List[str],
    compute_resources: k8s.V1ResourceRequirements,
    ephemeral_volume: Optional[EphemeralVolume],
    timeout_in_seconds: int,
    mount_storage_hellodata_pvc: bool,
    env_vars: dict
    ) -> dict:

    data_path = "/mnt/storage/" # the data storage mount path into the container-image

    storage_hellodata_volume_claim_name = "storage-hellodata"
    storage_hellodata_volume_name = "storage"

    in_cluster = True

    volumes = []
    volume_mounts = []

    if mount_storage_hellodata_pvc:
        # hellodata-storage pv
        storage_hellodata_volume_claim = k8s.V1PersistentVolumeClaimVolumeSource(claim_name=storage_hellodata_volume_claim_name)
        volumes.append(k8s.V1Volume(name=storage_hellodata_volume_name, persistent_volume_claim=storage_hellodata_volume_claim))
        volume_mounts.append(__get_volume_mount_for(volume_name=storage_hellodata_volume_name, mount_path=data_path))
    
    if ephemeral_volume is not None:
        # Ephemeral storage for duckdb file
        volumes.append(__get_ephemeral_storage_volume(ephemeral_volume.name, ephemeral_volume.size_in_Gi, ephemeral_volume.storage_class))
        volume_mounts.append(__get_volume_mount_for(ephemeral_volume.name, mount_path=ephemeral_volume.mount_path))
    
    # Define common parameters for KubernetesPodOperator tasks
    common_k8s_pod_operator_params = {
        "namespace": namespace,
        "image": image,
        "image_pull_policy": "Always",
        "image_pull_secrets": [k8s.V1LocalObjectReference("regcred")],
        "annotations": {'prometheus.io/scrape': 'true'},
        "get_logs": True,
        "is_delete_operator_pod": True,
        "in_cluster": in_cluster,
        "configmaps": configmaps,
        "cmds": ["/bin/bash", "-cx"],
        "volumes": volumes,
        "volume_mounts": volume_mounts,
        "container_resources": compute_resources,
        "startup_timeout_seconds": timeout_in_seconds,
        "secrets": secrets,
        "env_vars": env_vars,
    }

    return common_k8s_pod_operator_params