"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class IAMNoInlinePolicy(CloudFormationLintRule):
    id = 'EIAMNoInlinePolicy' # New Rule ID
    shortdesc = 'No inline IAM policies for a user' # A short description about the rule
    description = 'IAM user should not have any inline policies. Should be centralized Policy object on group' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["iam"] 

    def match(self, cfn):
        
        """Check if user has inline IAM policies"""

        resources = cfn.get_resources(['AWS::IAM::User'])
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            properties = resource.get('Properties')
            if ((properties) and (properties.get('Policies'))):
                if (len(properties.get('Policies')) >= 1):
                    path = ['Resources', resource_name, 'Properties', 'Policies']
                    message = 'IAM Users should not have inline policies'
                    matches.append(RuleMatch(path, message.format(resource_name)))
        return matches