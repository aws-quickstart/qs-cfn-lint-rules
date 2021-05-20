"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re
import six
import json
import os
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

LINT_ERROR_MESSAGE = "IAM policy should not allow * resource; IAM Methods in this policy support granular permissions;"

custom_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/iam_methods.json")
with open(custom_dict_path) as f:
    d = f.read()

resource_only = json.loads(d)

def deep_get(source_dict, list_of_keys, default_value=None):
    x = source_dict
    for k in list_of_keys:
        if isinstance(k, int):
            x = x[k]
        else:
            x = x.get(k, {})
    if not x:
        return default_value
    return x

def determine_wildcard_resource_violations(cfn, policy_path):
    violating_methods = []
    actions = deep_get(cfn.template, policy_path+['Action'], [])
    if not isinstance(actions, list):
        actions = [actions]
    for iam_method in actions:
        if not resource_only.get(iam_method):
            violating_methods.append(iam_method)
    return violating_methods

class IAMResourceWildcard(CloudFormationLintRule):
    """Check ARN for partition agnostics."""
    id = 'E-IAM-POLICY-RESOURCE-WILDCARD'
    shortdesc = '* on Resource property is a bad idea'
    description = 'Making sure wildcard resources are only used where no other option exists'
    source_url = 'https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules'
    tags = ['iam']
    SEARCH_PROPS = ['Resource']

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            if tm[-1] not in ['*', ['*']]:
                continue
            violating_methods = determine_wildcard_resource_violations(cfn, tm[:-2])
            if violating_methods:
                violation_matches.append(RuleMatch(tm[:-2], f"{LINT_ERROR_MESSAGE} Methods: {str(violating_methods)}"))
        return violation_matches
