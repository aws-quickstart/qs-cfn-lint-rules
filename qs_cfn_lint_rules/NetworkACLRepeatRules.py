"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class NetworkACLRepeatRules(CloudFormationLintRule):
    id = 'ENetworkACLRepeatRules' # New Rule ID
    shortdesc = 'No repeat rules on Network ACL unless different types' # A short description about the rule
    description = 'A NetworkACL\'s rule numbers cannot be repeated unless one is egress and one is ingress.' # (Longer) description about the rule
    source_url = 'https://github.com/aws-quickstart/qs-cfn-lint-rules/tree/main' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = ["networkacl"] # A set of tags (strings) for searching

    global ingress
    global egress
    is_egress = 'Ingress'
    curr_role = False # False for ingress, True for egress
    curr_rule_num = 0
    ingress = []
    egress = []

    def check_value(self, value, path):
        """Checks to make sure there are no duplicate rule numbers with the same type"""
        matches = []

        if ((curr_role == False) and (value in ingress)):
            message = 'Cannot have repeat rule numbers unless one is egress and the other is ingress'
            full_path = '/'.join(str(x) for x in path)
            matches.append(RuleMatch(path, message.format(value, full_path)))
        elif ((curr_role == True) and (value in egress)):
            message = 'Cannot have repeat rule numbers unless one is egress and the other is ingress'
            full_path = '/'.join(str(x) for x in path)
            matches.append(RuleMatch(path, message.format(value, full_path)))
        else:
            if ((is_egress) and (is_egress == True)):
                egress.append(curr_rule_num)
            else:
                ingress.append(curr_rule_num)
        return matches
    

    def match(self, cfn):

        """Collects ACL Entry details: rule number, is egress/ingress"""

        resources = cfn.get_resources(['AWS::EC2::NetworkAclEntry'])
        matches = []
        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            properties = resource.get('Properties')
            if properties:
                global curr_role
                global is_egress
                global curr_rule_num
                is_egress = properties.get('Egress')
                if ((is_egress) and (is_egress == True)):
                    curr_rule_num = properties.get('RuleNumber')
                    curr_role = True
                else:
                    curr_rule_num = properties.get('RuleNumber')
                    curr_role = False
                matches.extend(
                    cfn.check_value(
                        properties, 'RuleNumber', path,
                        check_value=self.check_value, 
                    )
                )

        return matches