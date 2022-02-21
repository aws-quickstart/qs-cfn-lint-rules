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
from qs_cfn_lint_rules.common import deep_get

LINT_ERROR_MESSAGE = "Combining Action and NotAction is a bad idea."
CFN_NAG_RULES = ["W14", "W15", "W16", "W17", "W18", "W19", "W20"]


def determine_action_notaction_violation(cfn, policy_path):
    policy = deep_get(cfn.template, policy_path, [])
    return all(x in policy.keys() for x in ["Action", "NotAction"])


class IAMResourceWildcard(CloudFormationLintRule):
    """Check ARN for partition agnostics."""

    id = "EIAMPolicyActionNotAction"
    shortdesc = "Combining Action and NotAction is a bad idea."
    description = "Making sure Action and NotAction are not used in an IAM statement together"
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["iam"]
    SEARCH_PROPS = ["Resource"]

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            violating_policy = determine_action_notaction_violation(
                cfn, tm[:-2]
            )
            if violating_policy:
                violation_matches.append(
                    RuleMatch(tm[:-2] + ["NotAction"], LINT_ERROR_MESSAGE)
                )
        return violation_matches
