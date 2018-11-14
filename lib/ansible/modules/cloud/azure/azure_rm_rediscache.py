#!/usr/bin/python
#
# Copyright (c) 2017 Zim Kalinowski, <zikalino@microsoft.com>
# Copyright (c) 2018 Giuseppe Pellegrino, <g.pellegrino@tadaweb.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_rediscache
version_added: "2.7"
short_description: Manage Redis Cache instance.
description:
    - Create, update and delete instance of Redis Cache.

options:
    resource_group:
        description:
            - The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
        required: True
    name:
        description:
            - The name of the server.
        required: True
    sku:
        description:
            - The SKU (pricing tier) of the server.
        suboptions:
            name:
                description:
                    - The name of the sku.
                choices: ['basic', 'standard', 'premium']
            size:
                description:
                    - "The size of the server. Values are (0, 1, 2, 3, 4, 5, 6) for basic/standard, (1, 2, 3, 4, 5) for premium."
    location:
        description:
            - Resource location. If not set, location from the resource group will be used as default.
    redis_configuration:
        description:
            - All redis settings in a dict[str, str] format.
            - Few possible keys: rdb-backup-enabled,rdb-storage-connection-string,rdb-backup-frequency,maxmemory-delta,maxmemory-policy,notify-keyspace-events,maxmemory-samples,slowlog-log-slower-than,slowlog-max-len,list-max-ziplist-entries,list-max-ziplist-value,hash-max-ziplist-entries,hash-max-ziplist-value,set-max-intset-entries,zset-max-ziplist-entries,zset-max-ziplist-value
    shard_count:
        description:
            - The number of shards to be created on a Premium Cluster Cache
    enable_non_ssl_port:
        description:
            - Enable the non SSL endpoint.
        type: bool
        default: False
    subnet_id:
        description:
            - The full resource ID of a subnet in a virtual network to deploy the Redis Cache in. Example format:
            - /subscriptions/{subid}/resourceGroups/{resourceGroupName}/Microsoft.{Network|ClassicNetwork}/VirtualNetworks/vnet1/subnets/subnet1
    static_ip:
        description:
            - Static IP address. Required when deploying a Redis Cache inside an existing Azure Virtual Network.
    zones:
        description:
            - A comma separated list of availability zones denoting where the resource needs to come from.
    state:
        description:
            - Assert the state of the RedisCache server. Use 'present' to create or update a server and 'absent' to delete it.
        default: present
        choices:
            - present
            - absent

extends_documentation_fragment:
    - azure

author:
    - "Zim Kalinowski (@zikalino)"
    - "Giuseppe Pellegrino (@joe-pll)"

'''

EXAMPLES = '''
  - name: Create (or update) Redis Cache
    azure_rm_rediscache:
      resource_group: TestGroup
      name: testcache
      sku:
        name: Basic
        size: 0
      location: eastus
'''

RETURN = '''
id:
    description:
        - Resource ID
    returned: always
    type: str
    sample: /subscriptions/12345678-1234-1234-1234-123412341234/resourceGroups/samplerg/providers/Microsoft.Cache/Redis/testcache
version:
    description:
        - 'Server version.'
    returned: always
    type: str
    sample: 3.2.7
host_name:
    description:
        - The fully qualified domain name of a server.
    returned: always
    type: str
    sample: testcache.redis.cache.windows.net
'''

import time
from ansible.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from azure.mgmt.redis import RedisManagementClient
    from msrestazure.azure_exceptions import CloudError
    from msrest.polling import LROPoller
    # from msrest.serialization import Model
except ImportError:
    # This is handled in azure_rm_common
    pass


class Actions:
    NoAction, Create, Update, Delete = range(4)


class AzureRMRedis(AzureRMModuleBase):
    """Configuration class for an Azure RM Resis Cache resource"""

    def __init__(self):
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str',
                required=True
            ),
            sku=dict(
                type='dict'
            ),
            location=dict(
                type='str'
            ),
            shard_count=dict(
                type='int'
            ),
            redis_configuration=dict(
                type='dict'
            ),
            enable_non_ssl_port=dict(
                type='bool',
                default=False
            ),
            tags=dict(
                type='dict'
            ),
            state=dict(
                type='str',
                default='present',
                choices=['present', 'absent']
            )
        )

        self.resource_group = None
        self.name = None
        self.parameters = dict()

        self.results = dict(changed=False)
        self.mgmt_client = None
        self.state = None
        self.to_do = Actions.NoAction

        super(AzureRMRedis, self).__init__(derived_arg_spec=self.module_arg_spec,
                                           supports_check_mode=True,
                                           supports_tags=True)

    def exec_module(self, **kwargs):
        """Main module execution method"""

        for key in list(self.module_arg_spec.keys()):
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
            elif kwargs[key] is not None:
                if key == "sku":
                    ev = dict()
                    sku_name = None
                    if 'size' in kwargs[key]:
                        ev['capacity'] = kwargs[key]['size']
                    if 'name' in kwargs[key]:
                        name = kwargs[key]['name']
                        ev['name'] = name[0].upper() + name[1:]
                        sku_name = ev['name']
                    if sku_name is not None:
                        ev['family'] = 'P' if sku_name == 'Premium' else 'C'
                    self.parameters["sku"] = ev
                elif key == "location":
                    self.parameters["location"] = kwargs[key]
                elif key == "redis_configuration":
                    self.parameters['redis_configuration'] = kwargs[key]
                elif key == "shard_count":
                    self.parameters['shard_count'] = kwargs[key]
                elif key == "enabled_non_ssl_port":
                    self.parameters['enable_non_ssl_port'] = kwargs[key]
                elif key == "subnet_ip":
                    self.parameters['subnet_ip'] = kwargs[key]
                elif key == "static_ip":
                    self.parameters['static_ip'] = kwargs[key]
                elif key == "zones":
                    self.parameters['zones'] = kwargs[key].split(',')
                elif key == "tags":
                    self.parameters['tags'] = kwargs[key]

        old_response = None
        response = None

        self.mgmt_client = self.get_mgmt_svc_client(RedisManagementClient,
                                                    base_url=self._cloud_environment.endpoints.resource_manager)

        resource_group = self.get_resource_group(self.resource_group)

        if "location" not in self.parameters:
            self.parameters["location"] = resource_group.location

        old_response = self.get_rediscache()

        if not old_response:
            self.log("Redis Cache instance doesn't exist")
            if self.state == 'absent':
                self.log("Old instance didn't exist")
            else:
                self.to_do = Actions.Create
        else:
            self.log("Redis Cache instance already exists")
            if self.state == 'absent':
                self.to_do = Actions.Delete
            elif self.state == 'present':
                self.log("Need to check if Redis Cache instance has to be deleted or may be updated")
                self.to_do = Actions.Update

        if (self.to_do == Actions.Create) or (self.to_do == Actions.Update):
            self.log("Need to Create / Update the Redis Cache instance")

            if self.check_mode:
                self.results['changed'] = True
                return self.results

            response = self.create_update_rediscache()

            if not old_response:
                self.results['changed'] = True
            else:
                self.results['changed'] = old_response.__ne__(response)
            self.log("Creation / Update done")
        elif self.to_do == Actions.Delete:
            self.log("Redis Cache instance must be deleted")
            self.results['changed'] = True

            if self.check_mode:
                return self.results

            self.delete_rediscache()
            self.log("Redis Cache instance deleted")
            # make sure instance is actually deleted, for some Azure resources, instance is hanging around
            # for some time after deletion -- this should be really fixed in Azure
            while self.get_rediscache():
                time.sleep(20)
        else:
            self.log("Redis Cache instance unchanged")
            self.results['changed'] = False
            response = old_response

        if response:
            self.results["id"] = response["id"]
            self.results["host_name"] = response["host_name"]
            self.results["version"] = response["redis_version"]

        return self.results

    def create_update_rediscache(self):
        '''
        Creates or updates Redis Cache with the specified configuration.

        :return: deserialized Redis Cache instance state dictionary
        '''
        self.log("Creating / Updating the Redis Cache instance {0}".format(self.name))

        try:
            if self.to_do == Actions.Create:
                response = self.mgmt_client.redis.create(resource_group_name=self.resource_group,
                                                         name=self.name,
                                                         parameters=self.parameters)
            else:
                response = self.mgmt_client.redis.update(resource_group_name=self.resource_group,
                                                         name=self.name,
                                                         parameters=self.parameters)
            if isinstance(response, LROPoller):
                response = self.get_poller_result(response)

        except CloudError as exc:
            self.log('Error attempting to create the Redis Cache instance.')
            self.fail("Error creating the Redis Cache instance: {0}".format(str(exc)))
        return response.as_dict()

    def delete_rediscache(self):
        '''
        Deletes specified Redis Cache instance in the specified subscription and resource group.

        :return: True
        '''
        self.log("Deleting the Redis Cache instance {0}".format(self.name))
        try:
            self.mgmt_client.redis.delete(resource_group_name=self.resource_group,
                                          name=self.name)
        except CloudError as e:
            self.log('Error attempting to delete the Redis Cache instance.')
            self.fail("Error deleting the Redis Cache instance: {0}".format(str(e)))

        return True

    def get_rediscache(self):
        '''
        Gets the properties of the specified Redis Cache.

        :return: deserialized Redis Cache instance state dictionary
        '''
        self.log("Checking if the Redis Cache instance {0} is present".format(self.name))
        found = False
        try:
            response = self.mgmt_client.redis.get(resource_group_name=self.resource_group,
                                                  name=self.name)
            found = True
            self.log("Response : {0}".format(response))
            self.log("Redis Cache instance : {0} found".format(response.name))
        except CloudError:
            self.log('Did not find the Redis Cache instance.')
        if found is True:
            return response.as_dict()

        return False


def main():
    """Main execution"""
    AzureRMRedis()


if __name__ == '__main__':
    main()
