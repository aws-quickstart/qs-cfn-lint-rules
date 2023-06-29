"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class IAMPolicyOnlyGroup(CloudFormationLintRule):
    id = 'EIAMPolicyOnlyGroup' # New Rule ID
    shortdesc = 'No direct user on IAM policy' # A short description about the rule
    description = 'IAM policy should not apply directly to users. Should be on group' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["iam"] 

    def match(self, cfn):
        
        """Check if user is mentioned in IAM policy"""

        resources = cfn.get_resources(['AWS::IAM::Policy'])
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            properties = resource.get('Properties')
            if properties:
                if ((properties.get('Users')) and (len(properties.get('Users')) >= 1)):
                    path = ['Resources', resource_name, 'Properties', 'Users']
                    message = 'Do not assign IAM policies directly to Users'
                    matches.append(RuleMatch(path, message.format(resource_name)))
        return matches