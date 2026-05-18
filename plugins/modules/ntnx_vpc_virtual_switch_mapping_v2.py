#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Nutanix
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ntnx_vpc_virtual_switch_mapping_v2
short_description: Manage VPC virtual switch mappings in Nutanix Prism Central
version_added: 2.6.0
description:
  - Create, Update, Delete VPC virtual switch mappings.
  - Set VPC for virtual switch mappings traffic config.
  - The API manages the full list of VPC virtual switch mappings as a batch.
    Each create or update call replaces the entire configuration.
  - This module uses PC v4 APIs based SDKs
options:
  state:
    description:
      - Specify state.
      - If C(state) is set to C(present) then the module will create or update a VPC virtual switch mapping.
      - If C(state) is set to C(absent) with C(virtual_switch_uuid), then the module will delete the mapping.
    choices:
      - present
      - absent
    type: str
    default: present
  wait:
    description: Wait for the operation to complete.
    type: bool
    required: false
    default: True
  ext_id:
    description:
      - The external ID of the VPC virtual switch mapping (if available).
      - Can be used to identify a mapping for update or delete.
    type: str
  virtual_switch_uuid:
    description:
      - The UUID of the virtual switch to map.
      - Used as the key identifier for a specific mapping.
      - Required for create and delete operations.
    type: str
  cluster_uuids:
    description:
      - List of cluster UUIDs associated with the mapping.
    type: list
    elements: str
  is_all_traffic_permitted:
    description:
      - Whether all traffic is permitted for this mapping.
    type: bool
extends_documentation_fragment:
  - nutanix.ncp.ntnx_credentials
  - nutanix.ncp.ntnx_operations_v2
  - nutanix.ncp.ntnx_logger
  - nutanix.ncp.ntnx_proxy_v2
author:
  - Abhinav Bansal (@abhinavbansal29)
"""

EXAMPLES = r"""
- name: Create a VPC virtual switch mapping
  nutanix.ncp.ntnx_vpc_virtual_switch_mapping_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    state: present
    virtual_switch_uuid: "{{ virtual_switch_uuid }}"
    cluster_uuids:
      - "{{ cluster_uuid }}"
    is_all_traffic_permitted: true
  register: result

- name: Update a VPC virtual switch mapping
  nutanix.ncp.ntnx_vpc_virtual_switch_mapping_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    state: present
    virtual_switch_uuid: "{{ virtual_switch_uuid }}"
    cluster_uuids:
      - "{{ cluster_uuid }}"
    is_all_traffic_permitted: false
  register: result

- name: Delete a VPC virtual switch mapping
  nutanix.ncp.ntnx_vpc_virtual_switch_mapping_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    state: absent
    virtual_switch_uuid: "{{ virtual_switch_uuid }}"
  register: result
"""

RETURN = r"""
response:
  description: The VPC virtual switch mapping response.
  returned: always
  type: dict
  sample:
    {
      "ext_id": null,
      "virtual_switch_uuid": "11111111-1111-1111-1111-111111111111",
      "cluster_uuids": ["22222222-2222-2222-2222-222222222222"],
      "is_all_traffic_permitted": true,
      "metadata": null,
      "tenant_id": null
    }

changed:
  description: This indicates whether the task resulted in any changes.
  returned: always
  type: bool
  sample: true

msg:
  description: Status message.
  returned: When there is an error, module is idempotent or check mode.
  type: str

error:
  description: Error information if the task encountered errors.
  returned: When an error occurs.
  type: str

ext_id:
  description: The external ID of the VPC virtual switch mapping.
  returned: always
  type: str

task_ext_id:
  description: The external ID of the task.
  returned: When a task is created.
  type: str

skipped:
  description: Whether the task was skipped due to idempotency.
  returned: When no changes are needed.
  type: bool
  sample: false

failed:
  description: Whether the task failed.
  returned: always
  type: bool
  sample: false
"""

import traceback  # noqa: E402
import warnings  # noqa: E402

from ansible.module_utils.basic import missing_required_lib  # noqa: E402

from ..module_utils.utils import remove_param_with_none_value  # noqa: E402
from ..module_utils.v4.base_module_v4 import BaseModuleV4  # noqa: E402
from ..module_utils.v4.network.api_client import (  # noqa: E402
    get_vpc_virtual_switch_mappings_api_instance,
)
from ..module_utils.v4.prism.tasks import wait_for_completion  # noqa: E402
from ..module_utils.v4.utils import (  # noqa: E402
    raise_api_exception,
    strip_internal_attributes,
)

SDK_IMP_ERROR = None
try:
    import ntnx_networking_py_client as net_sdk  # noqa: E402
except ImportError:
    from ..module_utils.v4.sdk_mock import mock_sdk as net_sdk  # noqa: E402

    SDK_IMP_ERROR = traceback.format_exc()

warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made")


def get_module_spec():
    module_args = dict(
        ext_id=dict(type="str"),
        virtual_switch_uuid=dict(type="str"),
        cluster_uuids=dict(type="list", elements="str"),
        is_all_traffic_permitted=dict(type="bool"),
    )
    return module_args


def _list_existing_mappings(module, api_instance):
    """Fetch all current VPC virtual switch mappings from the API."""
    try:
        resp = api_instance.list_vpc_virtual_switch_mappings()
    except Exception as e:
        raise_api_exception(
            module=module,
            exception=e,
            msg="Api Exception raised while listing VPC virtual switch mappings",
        )
    if resp and resp.data:
        return list(resp.data)
    return []


def _find_mapping_by_vs_uuid(mappings, virtual_switch_uuid):
    """Find a mapping in the list by virtual_switch_uuid."""
    for mapping in mappings:
        if getattr(mapping, "virtual_switch_uuid", None) == virtual_switch_uuid:
            return mapping
    return None


def _build_mapping_spec(module):
    """Build a VpcVirtualSwitchMapping from module params."""
    spec = net_sdk.VpcVirtualSwitchMapping()
    params = module.params

    if params.get("virtual_switch_uuid"):
        spec.virtual_switch_uuid = params["virtual_switch_uuid"]
    if params.get("cluster_uuids"):
        spec.cluster_uuids = params["cluster_uuids"]
    if params.get("is_all_traffic_permitted") is not None:
        spec.is_all_traffic_permitted = params["is_all_traffic_permitted"]
    return spec


def _mapping_to_comparable_dict(mapping):
    """Convert a mapping to a dict suitable for idempotency comparison."""
    if hasattr(mapping, "to_dict"):
        d = mapping.to_dict()
    else:
        d = dict(mapping)
    strip_internal_attributes(d)
    for key in ("ext_id", "links", "tenant_id", "metadata"):
        d.pop(key, None)
    return d


def _post_mappings(module, api_instance, mappings_list, result):
    """POST the full list of VPC virtual switch mappings to the API."""
    try:
        resp = api_instance.create_vpc_virtual_switch_mapping(body=mappings_list)
    except Exception as e:
        raise_api_exception(
            module=module,
            exception=e,
            msg="Api Exception raised while setting VPC virtual switch mappings",
        )

    task_ext_id = resp.data.ext_id
    result["task_ext_id"] = task_ext_id
    result["response"] = strip_internal_attributes(resp.data.to_dict())

    if task_ext_id and module.params.get("wait"):
        task_status = wait_for_completion(module, task_ext_id)
        result["response"] = strip_internal_attributes(task_status.to_dict())


def create_mapping(module, api_instance, result):
    vs_uuid = module.params.get("virtual_switch_uuid")
    existing = _list_existing_mappings(module, api_instance)
    current = _find_mapping_by_vs_uuid(existing, vs_uuid)

    new_spec = _build_mapping_spec(module)

    if current:
        old_dict = _mapping_to_comparable_dict(current)
        new_dict = _mapping_to_comparable_dict(new_spec)
        if old_dict == new_dict:
            result["skipped"] = True
            result["response"] = strip_internal_attributes(current.to_dict())
            result["ext_id"] = getattr(current, "ext_id", None)
            module.exit_json(msg="Nothing to change.", **result)

    if module.check_mode:
        result["response"] = strip_internal_attributes(new_spec.to_dict())
        return

    updated_list = [
        m for m in existing if getattr(m, "virtual_switch_uuid", None) != vs_uuid
    ]
    updated_list.append(new_spec)

    _post_mappings(module, api_instance, updated_list, result)

    if module.params.get("wait"):
        refreshed = _list_existing_mappings(module, api_instance)
        mapping = _find_mapping_by_vs_uuid(refreshed, vs_uuid)
        if mapping:
            result["ext_id"] = getattr(mapping, "ext_id", None)
            result["response"] = strip_internal_attributes(mapping.to_dict())

    result["changed"] = True


def update_mapping(module, api_instance, result):
    ext_id = module.params.get("ext_id")
    vs_uuid = module.params.get("virtual_switch_uuid")
    result["ext_id"] = ext_id

    existing = _list_existing_mappings(module, api_instance)

    current = None
    if vs_uuid:
        current = _find_mapping_by_vs_uuid(existing, vs_uuid)
    if not current and ext_id:
        for m in existing:
            if getattr(m, "ext_id", None) == ext_id:
                current = m
                vs_uuid = getattr(m, "virtual_switch_uuid", None)
                break

    if not current:
        module.fail_json(
            msg="VPC virtual switch mapping not found for update",
            **result,
        )

    new_spec = _build_mapping_spec(module)
    if not new_spec.virtual_switch_uuid:
        new_spec.virtual_switch_uuid = vs_uuid

    old_dict = _mapping_to_comparable_dict(current)
    new_dict = _mapping_to_comparable_dict(new_spec)
    if old_dict == new_dict:
        result["skipped"] = True
        result["response"] = strip_internal_attributes(current.to_dict())
        module.exit_json(msg="Nothing to change.", **result)

    if module.check_mode:
        result["response"] = strip_internal_attributes(new_spec.to_dict())
        return

    updated_list = [
        m for m in existing if getattr(m, "virtual_switch_uuid", None) != vs_uuid
    ]
    updated_list.append(new_spec)

    _post_mappings(module, api_instance, updated_list, result)

    if module.params.get("wait"):
        refreshed = _list_existing_mappings(module, api_instance)
        mapping = _find_mapping_by_vs_uuid(refreshed, new_spec.virtual_switch_uuid)
        if mapping:
            result["ext_id"] = getattr(mapping, "ext_id", None)
            result["response"] = strip_internal_attributes(mapping.to_dict())

    result["changed"] = True


def delete_mapping(module, api_instance, result):
    ext_id = module.params.get("ext_id")
    vs_uuid = module.params.get("virtual_switch_uuid")
    result["ext_id"] = ext_id

    existing = _list_existing_mappings(module, api_instance)

    target = None
    if vs_uuid:
        target = _find_mapping_by_vs_uuid(existing, vs_uuid)
    if not target and ext_id:
        for m in existing:
            if getattr(m, "ext_id", None) == ext_id:
                target = m
                vs_uuid = getattr(m, "virtual_switch_uuid", None)
                break

    if not target:
        result["skipped"] = True
        result["msg"] = "VPC virtual switch mapping not found. Nothing to delete."
        module.exit_json(**result)

    if module.check_mode:
        result["msg"] = (
            "VPC virtual switch mapping for virtual switch {0} "
            "will be deleted.".format(vs_uuid)
        )
        return

    updated_list = [
        m for m in existing if getattr(m, "virtual_switch_uuid", None) != vs_uuid
    ]

    _post_mappings(module, api_instance, updated_list, result)
    result["changed"] = True


def run_module():
    module = BaseModuleV4(
        argument_spec=get_module_spec(),
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ("virtual_switch_uuid", "ext_id"), True),
            ("state", "present", ("virtual_switch_uuid",)),
        ],
    )
    if SDK_IMP_ERROR:
        module.fail_json(
            msg=missing_required_lib("ntnx_networking_py_client"),
            exception=SDK_IMP_ERROR,
        )

    remove_param_with_none_value(module.params)
    result = {
        "changed": False,
        "response": None,
        "ext_id": None,
        "error": None,
        "failed": False,
    }

    api_instance = get_vpc_virtual_switch_mappings_api_instance(module)
    state = module.params["state"]

    if state == "present":
        if module.params.get("ext_id"):
            update_mapping(module, api_instance, result)
        else:
            create_mapping(module, api_instance, result)
    else:
        delete_mapping(module, api_instance, result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
