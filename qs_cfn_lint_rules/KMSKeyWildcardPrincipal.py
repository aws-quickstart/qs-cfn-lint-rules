"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class KMSKeyWildcardPrincipal(CloudFormationLintRule):
    id = 'EKMSKeyWildcardPrincipal' # New Rule ID
    shortdesc = 'No * principal for KMS Key' # A short description about the rule
    description = 'KMS key should not allow * principal (https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html)' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["kms"] # A set of tags (strings) for searching

    def check_value(self, value, path):
        """Check for * Principal"""
        matches = []
        principal = value.get('Principal').get('AWS')
        if ('*' in principal):
            message = 'Cannot use * principal on a KMS Key Policy'
            full_path = '/'.join(str(x) for x in path)
            matches.append(RuleMatch(path, message.format(value, full_path)))

        return matches

    def match(self, cfn):
        
        """Grab Key Policy results"""

        resources = cfn.get_resources(['AWS::KMS::Key'])
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties', 'KeyPolicy']

            policy = resource.get('Properties').get('KeyPolicy')
            if policy:
                matches.extend(
                    cfn.check_value(
                        policy, 'Statement', path,
                        check_value=self.check_value
                    )
                )
        print (matches)
        return matches