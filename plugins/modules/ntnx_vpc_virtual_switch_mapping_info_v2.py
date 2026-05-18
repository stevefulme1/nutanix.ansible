#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Nutanix
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ntnx_vpc_virtual_switch_mapping_info_v2
short_description: Fetch VPC virtual switch mappings info in Nutanix Prism Central
version_added: 2.6.0
description:
  - This module fetches VPC virtual switch mappings info from Nutanix Prism Central.
  - If C(ext_id) is provided, fetch a specific mapping by filtering on its external ID.
  - If C(ext_id) is not provided, fetch all mappings with optional filtering and pagination.
  - This module uses PC v4 APIs based SDKs
options:
  ext_id:
    description:
      - The external identifier of the VPC virtual switch mapping.
    type: str
extends_documentation_fragment:
  - nutanix.ncp.ntnx_credentials
  - nutanix.ncp.ntnx_info_v2
  - nutanix.ncp.ntnx_logger
  - nutanix.ncp.ntnx_proxy_v2
author:
  - Abhinav Bansal (@abhinavbansal29)
"""

EXAMPLES = r"""
- name: List all VPC virtual switch mappings
  nutanix.ncp.ntnx_vpc_virtual_switch_mapping_info_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
  register: result

- name: Get a specific VPC virtual switch mapping by ext_id
  nutanix.ncp.ntnx_vpc_virtual_switch_mapping_info_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    ext_id: "{{ mapping_ext_id }}"
  register: result

- name: List VPC virtual switch mappings with limit
  nutanix.ncp.ntnx_vpc_virtual_switch_mapping_info_v2:
    nutanix_host: "{{ ip }}"
    nutanix_username: "{{ username }}"
    nutanix_password: "{{ password }}"
    validate_certs: false
    limit: 10
  register: result
"""

RETURN = r"""
response:
  description:
    - Response for fetching VPC virtual switch mappings info.
    - Specific mapping info if External ID is provided.
    - List of mappings if External ID is not provided.
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
  sample: false

ext_id:
  description: External ID of the VPC virtual switch mapping.
  type: str
  returned: When external ID is provided.

msg:
  description: Status message.
  returned: When there is an error.
  type: str

error:
  description: Error information if the task encountered errors.
  returned: When an error occurs.
  type: str

failed:
  description: Whether the task failed.
  returned: always
  type: bool
  sample: false
"""

import warnings  # noqa: E402

from ..module_utils.utils import remove_param_with_none_value  # noqa: E402
from ..module_utils.v4.base_info_module import BaseInfoModule  # noqa: E402
from ..module_utils.v4.network.api_client import (  # noqa: E402
    get_vpc_virtual_switch_mappings_api_instance,
)
from ..module_utils.v4.spec_generator import SpecGenerator  # noqa: E402
from ..module_utils.v4.utils import (  # noqa: E402
    raise_api_exception,
    strip_internal_attributes,
)

warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made")


def get_module_spec():
    module_args = dict(
        ext_id=dict(type="str"),
    )
    return module_args


def get_mapping_by_ext_id(module, api_instance, result):
    ext_id = module.params.get("ext_id")
    result["ext_id"] = ext_id

    try:
        resp = api_instance.list_vpc_virtual_switch_mappings(
            _filter="extId eq '{0}'".format(ext_id)
        )
    except Exception as e:
        raise_api_exception(
            module=module,
            exception=e,
            msg="Api Exception raised while fetching VPC virtual switch mapping",
        )

    if resp and resp.data:
        for mapping in resp.data:
            if getattr(mapping, "ext_id", None) == ext_id:
                result["response"] = strip_internal_attributes(mapping.to_dict())
                return

    module.fail_json(
        msg="VPC virtual switch mapping with ext_id {0} not found".format(ext_id),
        **result,
    )


def list_mappings(module, api_instance, result):
    sg = SpecGenerator(module)
    kwargs, err = sg.get_info_spec(attr=module.params)

    if err:
        result["error"] = err
        module.fail_json(
            msg="Failed generating VPC virtual switch mappings info spec",
            **result,
        )

    try:
        resp = api_instance.list_vpc_virtual_switch_mappings(**kwargs)
    except Exception as e:
        raise_api_exception(
            module=module,
            exception=e,
            msg="Api Exception raised while fetching VPC virtual switch mappings",
        )

    resp = strip_internal_attributes(resp.to_dict())
    metadata = resp.get("metadata") or {}
    total_available_results = metadata.get("total_available_results")
    result["total_available_results"] = total_available_results
    resp = resp.get("data")

    if not resp:
        resp = []
    result["response"] = resp


def run_module():
    module = BaseInfoModule(
        argument_spec=get_module_spec(),
        supports_check_mode=False,
        mutually_exclusive=[
            ("ext_id", "filter"),
        ],
    )
    remove_param_with_none_value(module.params)
    result = {"changed": False, "response": None, "error": None}

    api_instance = get_vpc_virtual_switch_mappings_api_instance(module)

    if module.params.get("ext_id"):
        get_mapping_by_ext_id(module, api_instance, result)
    else:
        list_mappings(module, api_instance, result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
