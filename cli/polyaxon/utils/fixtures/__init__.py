#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from polyaxon.utils.fixtures.bo import (
    get_fxt_bo_with_inputs_outputs,
    get_fxt_bo_with_run_patch,
)
from polyaxon.utils.fixtures.build import set_build_fixture
from polyaxon.utils.fixtures.grid import get_fxt_grid_with_inputs_outputs
from polyaxon.utils.fixtures.jobs import (
    get_fxt_job,
    get_fxt_job_with_inputs,
    get_fxt_job_with_inputs_and_conditions,
    get_fxt_job_with_inputs_and_joins,
    get_fxt_job_with_inputs_outputs,
    get_fxt_tf_job,
)
from polyaxon.utils.fixtures.mapping import (
    get_fxt_mapping_with_inputs_outputs,
    get_fxt_mapping_with_run_patch,
)
from polyaxon.utils.fixtures.pipelines import (
    get_fxt_build_run_pipeline,
    get_fxt_build_run_pipeline_with_inputs,
    get_fxt_map_reduce,
    get_fxt_pipeline_params_env_termination,
    get_fxt_templated_pipeline_with_upstream_run,
    get_fxt_templated_pipeline_without_params,
    get_fxt_train_tensorboard_events_pipeline,
)
from polyaxon.utils.fixtures.schedule import get_fxt_schedule_with_inputs_outputs
from polyaxon.utils.fixtures.services import (
    get_fxt_job_with_hub_ref,
    get_fxt_service,
    get_fxt_service_with_inputs,
    get_fxt_service_with_upstream_runs,
)
