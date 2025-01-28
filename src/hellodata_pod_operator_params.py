from kubernetes import client
from kubernetes.client import models as k8s
from airflow.kubernetes.secret import Secret
from typing import Optional
import os

__LIMIT_MULTIPLIER = 1.5

class EphemeralVolume:
    def __init__(self, name: str, size_in_Gi: float, mount_path: str):
        self.name = name
        self.size_in_Gi = size_in_Gi
        self.mount_path = mount_path

def get_pod_operator_params(
    image:str,
    secret_name:str,
    cpus: float = 1.0, 
    memory_in_Gi: float = 1.0, 
    local_ephemeral_storage_in_Gi: float = 1.0,
    timeout_in_seconds: int = 2 * 60,
    large_ephemeral_storage_in_Gi: Optional[EphemeralVolume] = None):
    
    resources = __get_compute_resources(cpus, memory_in_Gi, local_ephemeral_storage_in_Gi)
    return __get_params_with_resources(image, secret_name, resources, large_ephemeral_storage_in_Gi, timeout_in_seconds)

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

def __get_ephemeral_storage_volume(name: str, size_in_Gi: int):
    return client.V1Volume(
        name=name,
        ephemeral=client.V1EphemeralVolumeSource(
            volume_claim_template=client.V1PersistentVolumeClaimTemplate(
                metadata=client.V1ObjectMeta(
                    labels={"type": "ephemeral-storage"}
                ),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    storage_class_name="msa-01",
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
    secret_name: str,
    compute_resources: k8s.V1ResourceRequirements,
    ephemeral_volume: Optional[EphemeralVolume],
    timeout_in_seconds: int):

    data_path = "/mnt/storage/" # the data storage mount path into the container-image
    namespace = os.getenv("HD_NAMESPACE")

    storage_hellodata_volume_claim_name = "storage-hellodata"
    storage_hellodata_volume_name = "storage"

    in_cluster = True
    config_file = None
    secrets = [
        Secret('env', None, secret_name),
    ]

    # hellodata-storage pv
    storage_hellodata_volume_claim = k8s.V1PersistentVolumeClaimVolumeSource(claim_name=storage_hellodata_volume_claim_name)
    storage_hellodata_volume = k8s.V1Volume(name=storage_hellodata_volume_name, persistent_volume_claim=storage_hellodata_volume_claim)
    storage_hellodata_volume_mount = __get_volume_mount_for(volume_name=storage_hellodata_volume_name, mount_path=data_path)

    volumes = [storage_hellodata_volume]
    volume_mounts = [storage_hellodata_volume_mount]
    
    if ephemeral_volume is not None:
        # Ephemeral storage for duckdb file
        volumes.append(__get_ephemeral_storage_volume(ephemeral_volume.name, ephemeral_volume.size_in_Gi))
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
        "config_file": config_file,
        "cmds": ["/bin/bash", "-cx"],
        "volumes": volumes,
        "volume_mounts": volume_mounts,
        "container_resources": compute_resources,
        "startup_timeout_seconds": timeout_in_seconds,
        "secrets": secrets,
        "env_vars": {
            "HD_NAMESPACE": os.getenv("HD_NAMESPACE"),
            "HTTP_PROXY": "http://proxy.kb-bedag.ch:8080",
            "HTTPS_PROXY": "http://proxy.kb-bedag.ch:8080",
            "http_proxy": "http://proxy.kb-bedag.ch:8080",
            "https_proxy": "http://proxy.kb-bedag.ch:8080",
            "no_proxy": "localhost,127.0.0.1,svc.,cluster.local,cisvc.local,ad.bedag.ch,kbsvc.local,10.3.*,svc.kb-bedag.ch,kbsvc.local,mgmtbi.ch,sso.be.ch,sso-test.be.ch",
            "NO_PROXY": "localhost,127.0.0.1,svc.,cluster.local,cisvc.local,ad.bedag.ch,kbsvc.local,10.3.*,svc.kb-bedag.ch,kbsvc.local,mgmtbi.ch,sso.be.ch,sso-test.be.ch"
        },
    }

    return common_k8s_pod_operator_params