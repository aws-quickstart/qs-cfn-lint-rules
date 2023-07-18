"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class MQBrokerPassword(CloudFormationLintRule):
    id = 'EMQBrokerPassword' # New Rule ID
    shortdesc = 'No plaintext password or ref to a default value on a AmazonMQ Broker User' # A short description about the rule
    description = 'AmazonMQ Broker Users Password must not be a plaintext string or a Ref to a Parameter with a Default value. Can be Ref to a NoEcho Parameter without a Default, or a dynamic reference to a secretsmanager value.' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["amazonmq"]
    all_params = {}

    def check_value(self, value, path):
        """Check to make sure there is no plaintext password or ref to default parameter"""
        matches = []

        # Checking for dynamic ref is sloppy need to check if there is a better method
        if ("resolve" not in value.get('Password')):
            if(issubclass(type(value.get('Password')), str)):
                message = 'MQBroker User cannot have plaintext password'
                full_path = '/'.join(str(x) for x in path)
                matches.append(RuleMatch(path, message.format(value, full_path)))
            else:
                passw = value.get('Password')
                ref = passw.get('Ref')
                if (ref):
                    print (ref in all_params)
                    if ((ref in all_params) and (all_params.get(ref).get('Default'))):
                        message = 'MQBroker User cannot have password with a reference to a default value'
                        full_path = '/'.join(str(x) for x in path)
                        matches.append(RuleMatch(path, message.format(value, full_path)))

        return matches

    def match(self, cfn):

        """Check User list for MQBroker"""

        resources = cfn.get_resources(['AWS::AmazonMQ::Broker'])
        global all_params
        all_params = cfn.get_parameters_valid()
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            properties = resource.get('Properties')
            if properties:
                matches.extend(
                    cfn.check_value(
                        properties, 'Users', path,
                        check_value=self.check_value
                    )
                )

        return matches