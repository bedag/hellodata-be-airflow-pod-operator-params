from datetime import timedelta
from pendulum import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

# ##### REMOVE BETWEEN #####
import os
import sys

current_file = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file)
sys.path.append(current_directory)
from pod_operator_params import (
    get_pod_operator_params,
)  # local import --> copy library file next to DAG file and name it pod_operator_params.py

# ##### REMOVE BETWEEN #####
# from hellodata_be_airflow_pod_operator_params import (
#     get_pod_operator_params,
# )  # library import

operator_params = get_pod_operator_params(
    "artifacts.bedag.cloud/dockerhub/alpine:latest",
    namespace="x0e-hellodata-test-bd01",
    cpus=8,
    memory_in_Gi=10,
    storage_in_Gi=6,
    secrets=["superset-demo-config"],
    configmaps=["superset-demo-extra-config"],
    startup_timeout_in_seconds=10 * 60,
    env_vars={"key": "value"},
)

default_args = {
    "owner": "airflow",
    "depend_on_past": False,
    "start_date": datetime(2025, 8, 1, tz="Europe/Zurich"),
}

with DAG(
    dag_id="example_dag_simple",
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
