#!/usr/bin/python
#
# Copyright (c) 2018 Zim Kalinowski, <zikalino@microsoft.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_cosmosdbdatabaseaccount_facts
version_added: "2.8"
short_description: Get Database Account facts.
description:
    - Get facts of Database Account.

options:
    resource_group:
        description:
            - Name of an Azure resource group.
        required: True
    account_name:
        description:
            - Cosmos DB database account name.

extends_documentation_fragment:
    - azure

author:
    - "Zim Kalinowski (@zikalino)"

'''

EXAMPLES = '''
  - name: Get instance of Database Account
    azure_rm_cosmosdbdatabaseaccount_facts:
      resource_group: resource_group_name
      account_name: account_name

  - name: List instances of Database Account
    azure_rm_cosmosdbdatabaseaccount_facts:
      resource_group: resource_group_name
'''

RETURN = '''
database_accounts:
    description: A list of dict results where the key is the name of the Database Account and the values are the facts for that Database Account.
    returned: always
    type: complex
    contains:
        databaseaccount_name:
            description: The key is the name of the server that the values relate to.
            type: complex
            contains:
                id:
                    description:
                        - The unique resource identifier of the database account.
                    returned: always
                    type: str
                    sample: /subscriptions/subid/resourceGroups/rg1/providers/Microsoft.DocumentDB/databaseAccounts/ddb1
                name:
                    description:
                        - The name of the database account.
                    returned: always
                    type: str
                    sample: ddb1
                type:
                    description:
                        - The type of Azure resource.
                    returned: always
                    type: str
                    sample: Microsoft.DocumentDB/databaseAccounts
                location:
                    description:
                        - The location of the resource group to which the resource belongs.
                    returned: always
                    type: str
                    sample: West US
                kind:
                    description:
                        - "Indicates the type of database account. This can only be set at database account creation. Possible values include:
                           'GlobalDocumentDB', 'MongoDB', 'Parse'"
                    returned: always
                    type: str
                    sample: GlobalDocumentDB
'''

from ansible.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from msrestazure.azure_operation import AzureOperationPoller
    from azure.mgmt.cosmosdb import CosmosDB
    from msrest.serialization import Model
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMDatabaseAccountsFacts(AzureRMModuleBase):
    def __init__(self):
        # define user inputs into argument
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            account_name=dict(
                type='str'
            )
        )
        # store the results of the module operation
        self.results = dict(
            changed=False,
            ansible_facts=dict()
        )
        self.mgmt_client = None
        self.resource_group = None
        self.account_name = None
        super(AzureRMDatabaseAccountsFacts, self).__init__(self.module_arg_spec)

    def exec_module(self, **kwargs):
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(CosmosDB,
                                                    base_url=self._cloud_environment.endpoints.resource_manager)

        if (self.resource_group is not None and
                self.account_name is not None):
            self.results['database_accounts'] = self.get()
        elif (self.resource_group is not None):
            self.results['database_accounts'] = self.list_by_resource_group()
        return self.results

    def get(self):
        '''
        Gets facts of the specified Database Account.

        :return: deserialized Database Accountinstance state dictionary
        '''
        response = None
        results = []
        try:
            response = self.mgmt_client.database_accounts.get(resource_group_name=self.resource_group,
                                                              account_name=self.account_name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for DatabaseAccounts.')

        if response is not None:
            results.push(this.format_item(response))

        return results

    def list_by_resource_group(self):
        '''
        Gets facts of the specified Database Account.

        :return: deserialized Database Accountinstance state dictionary
        '''
        response = None
        results = []
        try:
            response = self.mgmt_client.database_accounts.list_by_resource_group(resource_group_name=self.resource_group)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for DatabaseAccounts.')

        if response is not None:
            for item in response:
                results.push(format_item(item))

        return results

    def format_item(self, item):
        d = item.as_dict()
        d = {
            'id': d['id'],
            'resource_group': self.resource_group
        }
        return d


def main():
    AzureRMDatabaseAccountsFacts()


if __name__ == '__main__':
    main()
