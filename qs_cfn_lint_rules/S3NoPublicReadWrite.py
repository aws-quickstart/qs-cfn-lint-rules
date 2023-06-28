"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class S3NoPublicReadWrite(CloudFormationLintRule):
    id = 'ES3NoPublicReadWrite' # New Rule ID
    shortdesc = 'No public read-write ACL on S3' # A short description about the rule
    description = 'S3 Bucket should not have a public read-write acl' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["S3"] # A set of tags (strings) for searching

    def check_value(self, value, path):
        """Check ACL for S3 Bucket"""
        matches = []

        # Check max length
        if value == "PublicReadWrite":
            message = 'S3 Bucket cannot have PublicReadWrite on the ACL'
            full_path = '/'.join(str(x) for x in path)
            matches.append(RuleMatch(path, message.format(value, full_path)))

        return matches

    def match(self, cfn):

        """Check ACL for S3 Bucket"""

        resources = cfn.get_resources(['AWS::S3::Bucket'])
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            properties = resource.get('Properties')
            if properties:
                matches.extend(
                    cfn.check_value(
                        properties, 'AccessControl', path,
                        check_value=self.check_value
                    )
                )

        return matches