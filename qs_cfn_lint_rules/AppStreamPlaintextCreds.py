"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class AppStreamPlaintextCreds(CloudFormationLintRule):
    id = 'EAppStreamPlaintextCreds' # New Rule ID
    shortdesc = 'No plaintext password or ref to a default value on AppStream DirectoryConfig Credentials' # A short description about the rule
    description = 'AppStream DirectoryConfig ServiceAccountCredentials AccountPassword must not be a plaintext string or a Ref to a Parameter with a Default value. Can be Ref to a NoEcho Parameter without a Default, or a dynamic reference to a secretsmanager value.' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["appstream"]
    all_params = {}

    def check_value(self, value, path):
        """Check to make sure there is no plaintext password or ref to default parameter"""
        matches = []
        # Checking for dynamic ref is sloppy need to check if there is a better method
        if ("resolve" not in value):
            check = issubclass(type(value), str)
            if(check == True):
                message = 'ServiceAccountCredentials cannot have a plaintext password'
                full_path = '/'.join(str(x) for x in path)
                matches.append(RuleMatch(path, message.format(value, full_path)))
            else:
                acct_password = value.get('AccountPassword')
                check_pass = issubclass(type(acct_password), str)
                if (check_pass == True):
                    message = 'ServiceAccountCredentials AccountPassword cannot be a plaintext string'
                    full_path = '/'.join(str(x) for x in path)
                    matches.append(RuleMatch(path, message.format(value, full_path)))
                else:
                    ref_pass = acct_password.get('Ref')
                    if (ref_pass):
                        if ((ref_pass in all_params) and (all_params.get(ref_pass).get('Default'))):
                            message = 'ServiceAccountCredentials AccountPassword cannot have a reference to a default value'
                            full_path = '/'.join(str(x) for x in path)
                            matches.append(RuleMatch(path, message.format(value, full_path)))

        return matches

    def match(self, cfn):

        """Fetch ServiceAccountCredentials"""

        resources = cfn.get_resources(['AWS::AppStream::DirectoryConfig'])
        global all_params
        all_params = cfn.get_parameters_valid()
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            properties = resource.get('Properties')
            if properties:
                matches.extend(
                    cfn.check_value(
                        properties, 'ServiceAccountCredentials', path,
                        check_value=self.check_value
                    )
                )

        return matches