"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class IAMPolicyOnlyGroup(CloudFormationLintRule):
    id = 'EIAMUserNotInGroup' # New Rule ID
    shortdesc = 'User not assigned to group' # A short description about the rule
    description = 'IAM User is not assigned to any group' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["iam"] 

    def match(self, cfn):
        
        """Check if user is mentioned in IAM policy"""

        resources = cfn.get_resources(['AWS::IAM::User'])
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            properties = resource.get('Properties')
            if properties:
                groups = properties.get('Groups')
                if ((groups == None) or (groups[0] == None)):
                    path = ['Resources', resource_name, 'Properties', 'Groups']
                    message = 'An IAM User must be assigned to a group'
                    matches.append(RuleMatch(path, message.format(resource_name)))
        return matches