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
module: azure_rm_rediscache_facts
version_added: "2.7"
short_description: Get Azure Redis Cache facts.
description:
    - Get facts of Redis Cache.

options:
    resource_group:
        description:
            - The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
        required: True
    name:
        description:
            - The name of the server.
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.

extends_documentation_fragment:
    - azure

author:
    - "Zim Kalinowski (@zikalino)"
    - "Giuseppe Pellegrino (@joe-pll)"

'''

EXAMPLES = '''
  - name: Get instance of Redis Cache
    azure_rm_rediscache_facts:
      resource_group: resource_group_name
      name: name

  - name: List instances of Redis Cache
    azure_rm_rediscache_facts:
      resource_group: resource_group_name
'''

RETURN = '''
instances:
    description: A list of dictionaries containing facts for Redis Cache instances.
    returned: always
    type: complex
    contains:
        id:
            description:
                - Resource ID
            returned: always
            type: str
            sample: /subscriptions/ffffffff-ffff-ffff-ffff-ffffffffffff/resourceGroups/TestGroup/providers/Microsoft.Cache/Redis/testcache
        name:
            description:
                - Resource name.
            returned: always
            type: str
            sample: testcache
        location:
            description:
                - The location the resource resides in.
            returned: always
            type: str
            sample: eastus
        sku:
            description:
                - The SKU of the server.
            returned: always
            type: complex
            contains:
                name:
                    description:
                        - The name of the SKU
                    returned: always
                    type: str
                    sample: Standard
                family:
                    description:
                        - The SKU family
                    returned: always
                    type: str
                    sample: C
                capacity:
                    description:
                        - The size of the Redis Cache.
                    returned: always
                    type: int
                    sample: 1
        version:
            description:
                - Server version.
            returned: always
            type: str
            sample: "3.2.7"
        host_name:
            description:
                - The fully qualified domain name of a server.
            returned: always
            type: str
            sample: testcache.redis.cache.windows.net
        enable_non_ssl_port:
            description:
                - If the server accepts non SSL connections
            returned: always
            type: bool
            sample: False
        port:
            description:
                - The non SSL port of the server.
            return: always
            type: int
            sample: 6379
        ssl_port:
            description:
                - The SSL port of the server.
            return: always
            type: int
            sample: 6380
        redis_configuration:
            description:
                - The configuration value for redis
            type: complex
            returned: always
            contains:
                maxclients:
                    description:
                        - Maximum number of concurrent connections
                    returned: always
                    type: str
                    sample: "1000"
                maxfragmentationmemory-reserved:
                    description:
                        - MB reserverd for fragmentation
                    returned: always
                    type: str
                    sample: "50"
                maxmemory-policy:
                    description:
                        - The eviction strategy used when the data won't fit within its memory limit.
                    returned: always
                    type: str
                    sample: "volatile-lru"
                maxmemory-reserver:
                    description:
                        - MB reserverd for non-cache usage such as failover.
                    returned: always
                    type: str
                    sample: "50"
        shard_count:
            description:
                - The number of shards to be created on Premium Cluster Cache
            type: str
            sample: "10"
        subnet_id:
            description:
                - The full resource ID of a subnet in a virtual network to deploy the Redis Cache in.
                - Valid for Premium Cluster Cache
            type: str
            sample: "/subscriptions/{subid}/resourceGroups/{resourceGroupName}/Microsoft.{Network|ClassicNetwork}/VirtualNetworks/vnet1/subnets/subnet1"
        static_ip:
            description:
                - Static IP address. Required when deploying a Redis Cache inside an existing Azure Virtual Network.
            type: str
            sample: 192.168.0.25
        zones:
            description:
                - A comma separated list of availability zones denoting where the resource needs to come from.
            type: str
            sample: eastus-1

'''

from ansible.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMRedisFacts(AzureRMModuleBase):
    def __init__(self):
        # define user inputs into argument
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str'
            ),
            tags=dict(
                type='list'
            )
        )
        # store the results of the module operation
        self.results = dict(
            changed=False
        )
        self.resource_group = None
        self.name = None
        self.tags = None
        super(AzureRMRedisFacts, self).__init__(self.module_arg_spec,
                                                supports_tags=False)

    def exec_module(self, **kwargs):
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if (self.resource_group is not None and
                self.name is not None):
            self.results['instances'] = self.get()
        elif (self.resource_group is not None):
            self.results['instances'] = self.list_by_resource_group()
        return self.results

    def get(self):
        response = None
        results = []
        try:
            response = self.redis_client.redis.get(resource_group_name=self.resource_group,
                                                   name=self.name)
            self.log("Response : {0}".format(response))
        except CloudError:
            self.log('Could not get facts for Redis Cache.')

        if response and self.has_tags(response.tags, self.tags):
            results.append(self.format_item(response))

        return results

    def list_by_resource_group(self):
        response = None
        results = []
        try:
            response = self.redis_client.redis.list_by_resource_group(resource_group_name=self.resource_group)
            self.log("Response : {0}".format(response))
        except CloudError:
            self.log('Could not get facts for Redis Cache.')

        if response is not None:
            for item in response:
                if self.has_tags(item.tags, self.tags):
                    results.append(self.format_item(item))

        return results

    def format_item(self, item):
        item = item.as_dict()
        d = {
            'id': item['id'],
            'resource_group': self.resource_group,
            'name': item['name'],
            'sku': item['sku'],
            'location': item['location'],
            'version': item['redis_version'],
            'enable_non_ssl_port': item['enable_non_ssl_port'],
            'host_name': item['host_name'],
            'port': item['port'],
            'ssl_port': item['ssl_port'],
            'redis_configuration': item['redis_configuration']
        }

        if 'shard_count' in item:
            d['shard_count'] = item['shard_count']
        if 'subnet_id' in item:
            d['subnet_id'] = item['subnet_id']
        if 'static_ip' in item:
            d['static_ip'] = item['static_ip']
        if 'zones' in item:
            d['zones'] = item['zones']

        return d


def main():
    AzureRMRedisFacts()


if __name__ == '__main__':
    main()
