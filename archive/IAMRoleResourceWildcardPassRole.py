"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

class IAMRoleResourceWildcardPassRole(CloudFormationLintRule):
    id = 'EIAMRoleResourceWildardPassRole' # New Rule ID
    shortdesc = 'No * resource with PassRole Action on IAM role' # A short description about the rule
    description = 'IAM role should not allow * resource with PassRole action on its permissions policy' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["iam"] 

    def match(self, cfn):
        
        """Check if IAM role contains * Resource and PassRole Action"""

        resources = cfn.get_resources(['AWS::IAM::Role'])
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']
            properties = resource.get('Properties')
            if properties:
                actions = properties.get('Policies')[0].get('PolicyDocument').get('Statement')[0].get('Action')
                resources_wild = properties.get('Policies')[0].get('PolicyDocument').get('Statement')[0].get('Resource')
                is_wildcard = ''
                if '*' in resources_wild:
                    is_wildcard = '*'
                if ((actions == 'iam:PassRole') and (is_wildcard == '*')):
                    path = ['Resources', resource_name, 'Properties', 'Policies', 'PolicyDocument', 'Statement', 'Action']
                    message = 'Do not use a resource wildcard (*) with the PassRole Action'
                    matches.append(RuleMatch(path, message.format(resource_name)))
                else:
                    for action in actions:
                        if ((action == 'iam:PassRole') and (is_wildcard == '*')):
                            path = ['Resources', resource_name, 'Properties', 'Policies', 'PolicyName', 'Statement', 'Action']
                            message = 'Do not use a resource wildcard (*) with the PassRole Action'
                            matches.append(RuleMatch(path, message.format(resource_name)))
        return matches
