from datetime import timedelta
from pendulum import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

##### REMOVE BETWEEN #####
import os
import sys

current_file = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file)
sys.path.append(current_directory)
##### REMOVE BETWEEN #####

from hellodata_be_airflow_pod_operator_params import (
    get_pod_operator_params,
    EphemeralVolume,
)  # library import

operator_params = get_pod_operator_params(
    "alpine:latest",
    namespace="al1-hellodata-projectsdev",
    secrets=["superset-repsda-env"],
    configmaps=["superset-repsda-extra-config"],
    cpus=0.5,
    memory_in_Gi=0.5,
    local_ephemeral_storage_in_Gi=1,
    startup_timeout_in_seconds=10 * 60,
    large_ephemeral_storage_volume=EphemeralVolume(
        "my-storage", 5, "/app/large_ephemeral_storage", "block-nutanix"
    ),
    env_vars={"key": "value"},
)

operator_params["tolerations"] = [
    {
        "key": "io.bedag.ch/hypervisor",
        "operator": "Equal",
        "value": "nutanix",
        "effect": "NoSchedule",
    },
]

default_args = {
    "owner": "airflow",
    "depend_on_past": False,
    "start_date": datetime(2025, 8, 1, tz="Europe/Zurich"),
}

with DAG(
    dag_id="example_dag_advanced",
    schedule="@once",
    default_args=default_args,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=60 * 5),
) as dag:

    my_task = KubernetesPodOperator(
        **operator_params,
        name="my_task",
        task_id="my_task",
        arguments=[
            """
    echo "I run on kubernetes and have the following env vars" &&
    printenv
    """
        ],
    )
