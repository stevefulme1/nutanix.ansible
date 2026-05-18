#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Nutanix
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: ntnx_vm_startup_policy_v2
short_description: Manage VM startup policies in Nutanix Prism Central
description:
    - This module allows you to create, update, and delete VM startup policies in Nutanix Prism Central.
    - This module uses PC v4 APIs based SDKs
version_added: "2.6.0"
author:
 - Abhinav Bansal (@abhinavbansal29)
options:
    ext_id:
        description:
            - The unique identifier of the VM startup policy.
            - This parameter is required for update and delete operations.
        required: false
        type: str
    name:
        description:
            - The name of the VM startup policy.
        required: false
        type: str
    description:
        description:
            - The description of the VM startup policy.
        required: false
        type: str
    groups:
        description:
            - List of dependency groups for the VM startup policy.
            - Each group contains a list of category references.
        required: false
        type: list
        elements: dict
        suboptions:
            categories:
                description:
                    - List of category references in the dependency group.
                required: true
                type: list
                elements: dict
                suboptions:
                    ext_id:
                        description:
                            - The external ID of the category.
                        required: true
                        type: str
    start_conditions:
        description:
            - List of start conditions for the VM startup policy.
        required: false
        type: list
        elements: dict
        suboptions:
            power_state_criteria:
                description:
                    - The power state criteria for the start condition.
                required: true
                type: dict
                suboptions:
                    criteria_type:
                        description:
                            - The type of power state criteria.
                        required: true
                        choices:
                            - POWER_ON
                            - GUEST_BOOTUP
                        type: str
                    timeout_duration_secs:
                        description:
                            - Timeout duration in seconds for guest bootup criteria.
                            - Only applicable when criteria_type is GUEST_BOOTUP.
                        required: false
                        type: int
            delay_duration_secs:
                description:
                    - Delay duration in seconds before starting the next group.
                required: false
                type: int
    state:
        description:
            - Specify state
            - If C(state) is set to C(present) then the operation will be to create the item.
            - if C(state) is set to C(present) and C(ext_id) is given then it will update that policy.
            - if C(state) is set to C(present) then C(ext_id) or C(name) needs to be set.
            - >-
                If C(state) is set to C(absent) and if the item exists, then
                item is removed.
        choices:
            - present
            - absent
        type: str
        default: present
    wait:
        description: Wait for the CRUD operation to complete.
        type: bool
        required: false
        default: True
extends_documentation_fragment:
    - nutanix.ncp.ntnx_credentials
    - nutanix.ncp.ntnx_operations_v2
    - nutanix.ncp.ntnx_logger
    - nutanix.ncp.ntnx_proxy_v2
notes:
    - "Ref: U(https://developers.nutanix.com/api-reference?namespace=vmm)"
"""

EXAMPLES = r"""
- name: Create a VM startup policy
  nutanix.ncp.ntnx_vm_startup_policy_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    name: my_startup_policy
    description: My VM startup policy
    groups:
      - categories:
          - ext_id: "category-ext-id-1"
      - categories:
          - ext_id: "category-ext-id-2"
    start_conditions:
      - power_state_criteria:
          criteria_type: GUEST_BOOTUP
          timeout_duration_secs: 300
        delay_duration_secs: 60
    state: present
    wait: true

- name: Update a VM startup policy
  nutanix.ncp.ntnx_vm_startup_policy_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    ext_id: "605a0cf9-d04e-3be7-911b-1e6f193f6eb9"
    name: my_startup_policy_updated
    state: present
    wait: true

- name: Delete a VM startup policy
  nutanix.ncp.ntnx_vm_startup_policy_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    ext_id: "605a0cf9-d04e-3be7-911b-1e6f193f6eb9"
    state: absent
    wait: true
"""


RETURN = r"""
response:
    description:
        - The response from the VM startup policy operation.
        - It will be task response if C(wait) is false.
    type: dict
    returned: always
    sample: {
            "name": "my_startup_policy",
            "description": "My VM startup policy",
            "ext_id": "54fe0ed5-02d8-4588-b10b-3b9736bf3d06",
            "groups": [
                {
                    "categories": [
                        {"ext_id": "category-ext-id-1"}
                    ]
                }
            ],
            "start_conditions": [
                {
                    "power_state_criteria": {"timeout_duration_secs": 300},
                    "delay_duration_secs": 60
                }
            ]
        }
task_ext_id:
    description:
        - The external ID of the task associated with the VM startup policy operation.
    type: str
    returned: when a task is created
    sample: "98b9dc89-be08-3c56-b554-692b8b676fd2"
ext_id:
    description:
        - The external ID of the VM startup policy.
    type: str
    sample: "98b9dc89-be08-3c56-b554-692b8b676fd2"
    returned: always
changed:
    description: Indicates whether the VM startup policy was changed.
    type: bool
    returned: always
msg:
    description: This indicates the message if any message occurred
    returned: When there is an error, module is idempotent or check mode (in delete operation)
    type: str
    sample: "Failed generating create VM startup policy Spec"
error:
    description: The error message if an error occurred during the VM startup policy operation.
    type: str
    returned: when an error occurs
skipped:
    description: Indicates whether the VM startup policy operation was skipped.
    type: bool
    returned: when the operation is skipped
failed:
    description: Indicates whether the VM startup policy operation failed.
    type: bool
    returned: always
"""

import traceback  # noqa: E402
import warnings  # noqa: E402
from copy import deepcopy  # noqa: E402

from ansible.module_utils.basic import missing_required_lib  # noqa: E402

from ..module_utils.utils import remove_param_with_none_value  # noqa: E402
from ..module_utils.v4.base_module_v4 import BaseModuleV4  # noqa: E402
from ..module_utils.v4.constants import Tasks  # noqa: E402
from ..module_utils.v4.prism.tasks import (  # noqa: E402
    get_entity_ext_id_from_task,
    wait_for_completion,
)
from ..module_utils.v4.utils import (  # noqa: E402
    raise_api_exception,
    strip_internal_attributes,
)
from ..module_utils.v4.vmm.api_client import (  # noqa: E402
    get_etag,
    get_vm_startup_policies_api_instance,
)
from ..module_utils.v4.vmm.helpers import get_vm_startup_policy  # noqa: E402

SDK_IMP_ERROR = None
try:
    import ntnx_vmm_py_client as vmm_sdk
except ImportError:

    from ..module_utils.v4.sdk_mock import mock_sdk as vmm_sdk

    SDK_IMP_ERROR = traceback.format_exc()

warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made")


def get_module_spec():
    """
    Returns the module specification for ntnx_vm_startup_policy_v2.
    """
    category_ref_spec = dict(
        ext_id=dict(type="str", required=True),
    )
    dependency_group_spec = dict(
        categories=dict(
            type="list",
            required=True,
            elements="dict",
            options=category_ref_spec,
            obj=vmm_sdk.AhvPoliciesCategoryReference,
        ),
    )
    power_state_criteria_spec = dict(
        criteria_type=dict(
            type="str",
            required=True,
            choices=["POWER_ON", "GUEST_BOOTUP"],
        ),
        timeout_duration_secs=dict(type="int", required=False),
    )
    start_condition_spec = dict(
        power_state_criteria=dict(
            type="dict",
            required=True,
            options=power_state_criteria_spec,
        ),
        delay_duration_secs=dict(type="int", required=False),
    )
    module_args = dict(
        ext_id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        groups=dict(
            type="list",
            required=False,
            elements="dict",
            options=dependency_group_spec,
            obj=vmm_sdk.DependencyGroup,
        ),
        start_conditions=dict(
            type="list",
            required=False,
            elements="dict",
            options=start_condition_spec,
            obj=vmm_sdk.StartCondition,
        ),
    )
    return module_args


def _build_start_conditions(params_start_conditions):
    """
    Build StartCondition SDK objects from module params.
    The SpecGenerator cannot handle the OneOf power_state_criteria polymorphism,
    so we build these manually.
    """
    if not params_start_conditions:
        return None

    conditions = []
    for sc_param in params_start_conditions:
        condition = vmm_sdk.StartCondition()
        psc = sc_param.get("power_state_criteria")
        if psc:
            criteria_type = psc.get("criteria_type")
            if criteria_type == "GUEST_BOOTUP":
                timeout = psc.get("timeout_duration_secs")
                condition.power_state_criteria = vmm_sdk.PowerStateCriteriaGuestBootup(
                    timeout_duration_secs=timeout
                )
            else:
                condition.power_state_criteria = vmm_sdk.PowerStateCriteriaPowerOn()
        delay = sc_param.get("delay_duration_secs")
        if delay is not None:
            condition.delay_duration_secs = delay
        conditions.append(condition)
    return conditions


def _build_groups(params_groups):
    """
    Build DependencyGroup SDK objects from module params.
    """
    if not params_groups:
        return None

    groups = []
    for g_param in params_groups:
        group = vmm_sdk.DependencyGroup()
        cats = g_param.get("categories")
        if cats:
            cat_refs = []
            for c in cats:
                cat_ref = vmm_sdk.AhvPoliciesCategoryReference()
                cat_ref.ext_id = c.get("ext_id")
                cat_refs.append(cat_ref)
            group.categories = cat_refs
        groups.append(group)
    return groups


def create_policy(module, api_instance, result):
    """Create a new VM startup policy."""
    spec = vmm_sdk.VmStartupPolicy()
    spec.name = module.params.get("name")
    spec.description = module.params.get("description")

    groups = _build_groups(module.params.get("groups"))
    if groups is not None:
        spec.groups = groups

    start_conditions = _build_start_conditions(module.params.get("start_conditions"))
    if start_conditions is not None:
        spec.start_conditions = start_conditions

    if module.check_mode:
        result["response"] = strip_internal_attributes(spec.to_dict())
        return

    resp = None
    try:
        resp = api_instance.create_vm_startup_policy(body=spec)
    except Exception as e:
        raise_api_exception(
            module=module,
            exception=e,
            msg="Api Exception raised while creating VM startup policy",
        )

    task_ext_id = resp.data.ext_id
    result["task_ext_id"] = task_ext_id
    result["response"] = strip_internal_attributes(resp.data.to_dict())
    if task_ext_id and module.params.get("wait"):
        task = wait_for_completion(module, task_ext_id)
        ext_id = get_entity_ext_id_from_task(
            task, rel=Tasks.RelEntityType.VM_STARTUP_POLICY
        )
        if ext_id:
            result["ext_id"] = ext_id
            policy = get_vm_startup_policy(module, api_instance, ext_id)
            result["response"] = strip_internal_attributes(policy.to_dict())

    result["changed"] = True


def update_policy(module, api_instance, result):
    """Update an existing VM startup policy."""
    ext_id = module.params.get("ext_id")
    result["ext_id"] = ext_id

    current_spec = get_vm_startup_policy(module, api_instance, ext_id=ext_id)

    update_spec = deepcopy(current_spec)

    if module.params.get("name") is not None:
        update_spec.name = module.params["name"]
    if module.params.get("description") is not None:
        update_spec.description = module.params["description"]

    groups = _build_groups(module.params.get("groups"))
    if groups is not None:
        update_spec.groups = groups

    start_conditions = _build_start_conditions(module.params.get("start_conditions"))
    if start_conditions is not None:
        update_spec.start_conditions = start_conditions

    if current_spec == update_spec:
        result["skipped"] = True
        module.exit_json(msg="Nothing to change.", **result)

    if module.check_mode:
        result["response"] = strip_internal_attributes(update_spec.to_dict())
        return

    etag = get_etag(data=current_spec)
    if not etag:
        return module.fail_json(
            "unable to fetch etag for updating VM startup policy", **result
        )

    kwargs = {"if_match": etag}

    resp = None
    try:
        resp = api_instance.update_vm_startup_policy_by_id(
            extId=ext_id, body=update_spec, **kwargs
        )
    except Exception as e:
        raise_api_exception(
            module=module,
            exception=e,
            msg="Api Exception raised while updating VM startup policy",
        )

    task_ext_id = resp.data.ext_id
    result["task_ext_id"] = task_ext_id
    result["response"] = strip_internal_attributes(resp.data.to_dict())
    if task_ext_id and module.params.get("wait"):
        wait_for_completion(module, task_ext_id)

    updated_policy = get_vm_startup_policy(module, api_instance, ext_id)
    result["response"] = strip_internal_attributes(updated_policy.to_dict())
    result["changed"] = True


def delete_policy(module, api_instance, result):
    """Delete an existing VM startup policy."""
    ext_id = module.params.get("ext_id")
    result["ext_id"] = ext_id

    if module.check_mode:
        result["msg"] = "Policy with ext_id:{0} will be deleted.".format(ext_id)
        return

    current_spec = get_vm_startup_policy(module, api_instance, ext_id=ext_id)

    etag = get_etag(data=current_spec)
    if not etag:
        return module.fail_json(
            "unable to fetch etag for deleting VM startup policy", **result
        )

    kwargs = {"if_match": etag}

    try:
        resp = api_instance.delete_vm_startup_policy_by_id(extId=ext_id, **kwargs)
    except Exception as e:
        raise_api_exception(
            module=module,
            exception=e,
            msg="Api Exception raised while deleting VM startup policy",
        )

    task_ext_id = resp.data.ext_id
    result["task_ext_id"] = task_ext_id
    result["response"] = strip_internal_attributes(resp.data.to_dict())
    if task_ext_id and module.params.get("wait"):
        resp = wait_for_completion(module, task_ext_id)
        result["response"] = strip_internal_attributes(resp.to_dict())
    result["changed"] = True


def run_module():
    module = BaseModuleV4(
        argument_spec=get_module_spec(),
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("name", "ext_id"), True),
            ("state", "absent", ("ext_id",)),
        ],
    )
    if SDK_IMP_ERROR:
        module.fail_json(
            msg=missing_required_lib("ntnx_vmm_py_client"),
            exception=SDK_IMP_ERROR,
        )

    remove_param_with_none_value(module.params)
    result = {
        "changed": False,
        "error": None,
        "response": None,
        "ext_id": None,
    }

    api_instance = get_vm_startup_policies_api_instance(module)

    state = module.params["state"]
    if state == "present":
        if module.params.get("ext_id"):
            update_policy(module, api_instance, result)
        else:
            create_policy(module, api_instance, result)
    else:
        delete_policy(module, api_instance, result)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
