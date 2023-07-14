from typing import Union
from typing_extensions import Annotated

from pydantic import Field

from polyaxon.polyflow.run.cleaner import V1CleanerJob
from polyaxon.polyflow.run.dag import V1Dag
from polyaxon.polyflow.run.dask import V1DaskJob, V1DaskReplica
from polyaxon.polyflow.run.job import V1Job
from polyaxon.polyflow.run.kinds import (
    V1CloningKind,
    V1PipelineKind,
    V1RunEdgeKind,
    V1RunKind,
)
from polyaxon.polyflow.run.kubeflow.clean_pod_policy import V1CleanPodPolicy
from polyaxon.polyflow.run.kubeflow.mpi_job import V1MPIJob
from polyaxon.polyflow.run.kubeflow.mx_job import MXJobMode, V1MXJob
from polyaxon.polyflow.run.kubeflow.paddle_job import V1PaddleJob
from polyaxon.polyflow.run.kubeflow.pytorch_job import V1PytorchJob
from polyaxon.polyflow.run.kubeflow.replica import V1KFReplica
from polyaxon.polyflow.run.kubeflow.scheduling_policy import V1SchedulingPolicy
from polyaxon.polyflow.run.kubeflow.tf_job import V1TFJob
from polyaxon.polyflow.run.kubeflow.xgboost_job import V1XGBoostJob
from polyaxon.polyflow.run.notifier import V1NotifierJob
from polyaxon.polyflow.run.patch import validate_run_patch
from polyaxon.polyflow.run.ray import V1RayJob, V1RayReplica
from polyaxon.polyflow.run.resources import V1RunResources
from polyaxon.polyflow.run.service import V1Service
from polyaxon.polyflow.run.spark import (
    V1SparkDeploy,
    V1SparkJob,
    V1SparkReplica,
    V1SparkType,
)
from polyaxon.polyflow.run.tuner import V1TunerJob

V1Runtime = Annotated[
    Union[
        V1Job,
        V1Service,
        V1Dag,
        V1MPIJob,
        V1PytorchJob,
        V1TFJob,
        V1MXJob,
        V1PaddleJob,
        V1XGBoostJob,
        V1SparkJob,
        V1DaskJob,
        V1RayJob,
        V1NotifierJob,
        V1CleanerJob,
        V1TunerJob,
    ],
    Field(discriminator="kind"),
]


class RunMixin:
    def get_run_kind(self):
        raise NotImplementedError

    @property
    def is_job_run(self):
        return self.get_run_kind() == V1RunKind.JOB

    @property
    def is_service_run(self):
        return self.get_run_kind() == V1RunKind.SERVICE

    @property
    def is_mpi_job_run(self):
        return self.get_run_kind() == V1RunKind.MPIJOB

    @property
    def is_paddle_job_run(self):
        return self.get_run_kind() == V1RunKind.PADDLEJOB

    @property
    def is_pytorch_job_run(self):
        return self.get_run_kind() == V1RunKind.PYTORCHJOB

    @property
    def is_tf_job_run(self):
        return self.get_run_kind() == V1RunKind.TFJOB

    @property
    def is_mx_job_run(self):
        return self.get_run_kind() == V1RunKind.MXJOB

    @property
    def is_xgb_job_run(self):
        return self.get_run_kind() == V1RunKind.XGBJOB

    @property
    def is_spark_job_run(self):
        return self.get_run_kind() == V1RunKind.SPARKJOB

    @property
    def is_ray_job_run(self):
        return self.get_run_kind() == V1RunKind.RAYJOB

    @property
    def is_dask_job_run(self):
        return self.get_run_kind() == V1RunKind.DASKJOB

    @property
    def is_dag_run(self):
        return self.get_run_kind() == V1RunKind.DAG

    @property
    def is_schedule_run(self):
        return self.get_run_kind() == V1RunKind.SCHEDULE

    @property
    def is_notifier_run(self):
        return self.get_run_kind() == V1RunKind.NOTIFIER

    @property
    def is_cleaner_run(self):
        return self.get_run_kind() == V1RunKind.CLEANER

    @property
    def is_tuner_run(self):
        return self.get_run_kind() == V1RunKind.TUNER

    @property
    def is_watchdog(self):
        return self.get_run_kind() == V1RunKind.WATCHDOG

    @property
    def is_distributed_run(self):
        return (
            self.is_mpi_job_run
            or self.is_pytorch_job_run
            or self.is_tf_job_run
            or self.is_mx_job_run
            or self.is_xgb_job_run
        )
