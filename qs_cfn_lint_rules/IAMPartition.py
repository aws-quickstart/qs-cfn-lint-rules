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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch

LINT_ERROR_MESSAGE = "ARNs must be partition-agnostic. Please leverage ${AWS::Partition}"

def verify_agnostic_partition(cfn, resource_path, arndata):
   
    def _not_partition_agnostic_str(arnstr):
        if re.search('arn:(aws[a-zA-Z-]*)?', arnstr):
            return True

    def _not_partition_agnostic_list(resource_path, arnlist):
        matches = []
        for idx, subitem in enumerate(arnlist):
            if isinstance(subitem, six.string_types):
                if _not_partition_agnostic_str(subitem):
                    matches.append(resource_path + [idx])
            elif isinstance(subitem, dict):
                matches += _not_partition_agnostic_dict(resource_path + [idx], subitem)
            elif isinstance(subitem, list):
                matches += _not_partition_agnostic_list(resource_path + [idx], subitem)
        return matches

    def _not_partition_agnostic_dict(resource_path, subitem):
        matches = []
        for key, value in subitem.items():
            if not key == 'Fn::Sub':
                return []
            if isinstance(value, list):
                if len(value) == 2:
                    sub_str = value[0]
                    params = value[1]
                    if _not_partition_agnostic_str(sub_str):
                        matches.append(resource_path + [key, 0])
            elif isinstance(value, six.string_types):
                if _not_partition_agnostic_str(value):
                    matches.append(resource_path + [key])
        return matches

    matches = []
    if isinstance(arndata, six.string_types):
        if _not_partition_agnostic_str(arndata):
            matches.append(RuleMatch(resource_path, LINT_ERROR_MESSAGE))
    elif hasattr(arndata, 'update'):
        _t = arndata.copy()
        if isinstance(_t, dict):
            lm = _not_partition_agnostic_dict(resource_path, arndata)
            for rp in lm:
                matches.append(RuleMatch(rp, LINT_ERROR_MESSAGE))
    elif hasattr(arndata, 'copy'):
        _t = arndata.copy()
        if isinstance(arndata, list):
            lm = _not_partition_agnostic_list(resource_path, _t)
            for rp in lm:
                matches.append(RuleMatch(rp, LINT_ERROR_MESSAGE))
    return matches

class Base(CloudFormationLintRule):
    """Check ARN for partition agnostics."""
    id = 'E9007'
    shortdesc = 'ARNs should be partition argnostic'
    description = 'Making sure all ARNs leverage ${AWS::Partition}'
    source_url = 'https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules'
    tags = ['iam']
    SEARCH_PROPS = [
        'Resource',
        'ManagedPolicyArns'
    ]

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        search_terms = []
        for prop in self.SEARCH_PROPS:
            search_terms += cfn.search_deep_keys(prop)

        for st in search_terms:
            matches += verify_agnostic_partition(cfn, st[:-1], st[-1])
        return matches
