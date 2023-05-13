from typing import Dict

from pydantic import ValidationError

from polyaxon.exceptions import PolyaxonValidationError
from polyaxon.polyflow.run.cleaner import V1CleanerJob
from polyaxon.polyflow.run.dag import V1Dag
from polyaxon.polyflow.run.dask import V1Dask
from polyaxon.polyflow.run.job import V1Job
from polyaxon.polyflow.run.kinds import V1RunKind
from polyaxon.polyflow.run.kubeflow.mpi_job import V1MPIJob
from polyaxon.polyflow.run.kubeflow.mx_job import V1MXJob
from polyaxon.polyflow.run.kubeflow.paddle_job import V1PaddleJob
from polyaxon.polyflow.run.kubeflow.pytorch_job import V1PytorchJob
from polyaxon.polyflow.run.kubeflow.replica import V1KFReplica
from polyaxon.polyflow.run.kubeflow.tf_job import V1TFJob
from polyaxon.polyflow.run.kubeflow.xgboost_job import V1XGBoostJob
from polyaxon.polyflow.run.notifier import V1NotifierJob
from polyaxon.polyflow.run.service import V1Service
from polyaxon.polyflow.run.spark.replica import V1SparkReplica
from polyaxon.polyflow.run.spark.spark import V1Spark
from polyaxon.polyflow.run.tuner import V1TunerJob


def validate_run_patch(run_patch: Dict, kind: V1RunKind):
    if kind == V1RunKind.JOB:
        patch = V1Job.from_dict(run_patch)
    elif kind == V1RunKind.SERVICE:
        patch = V1Service.from_dict(run_patch)
    elif kind == V1RunKind.DAG:
        patch = V1Dag.from_dict(run_patch)
    elif kind == V1RunKind.MPIJOB:
        try:
            patch = V1MPIJob.from_dict(run_patch)
        except ValidationError:
            patch = V1KFReplica.from_dict(run_patch)
    elif kind == V1RunKind.PYTORCHJOB:
        try:
            patch = V1PytorchJob.from_dict(run_patch)
        except ValidationError:
            patch = V1KFReplica.from_dict(run_patch)
    elif kind == V1RunKind.PADDLEJOB:
        try:
            patch = V1PaddleJob.from_dict(run_patch)
        except ValidationError:
            patch = V1KFReplica.from_dict(run_patch)
    elif kind == V1RunKind.TFJOB:
        try:
            patch = V1TFJob.from_dict(run_patch)
        except ValidationError:
            patch = V1KFReplica.from_dict(run_patch)
    elif kind == V1RunKind.MXJOB:
        try:
            patch = V1MXJob.from_dict(run_patch)
        except ValidationError:
            patch = V1KFReplica.from_dict(run_patch)
    elif kind == V1RunKind.XGBJOB:
        try:
            patch = V1XGBoostJob.from_dict(run_patch)
        except ValidationError:
            patch = V1KFReplica.from_dict(run_patch)
    elif kind == V1RunKind.SPARK:
        try:
            patch = V1Spark.from_dict(run_patch)
        except ValidationError:
            patch = V1SparkReplica.from_dict(run_patch)
    elif kind == V1RunKind.DASK:
        patch = V1Dask.from_dict(run_patch)
    elif kind == V1RunKind.NOTIFIER:
        patch = V1NotifierJob.from_dict(run_patch)
    elif kind == V1RunKind.TUNER:
        patch = V1TunerJob.from_dict(run_patch)
    elif kind == V1RunKind.CLEANER:
        patch = V1CleanerJob.from_dict(run_patch)
    else:
        raise PolyaxonValidationError(
            "runPatch cannot be validate without a supported kind."
        )

    return patch
