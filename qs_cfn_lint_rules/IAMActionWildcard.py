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

import json
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import logging

# policyuniverse messes with the global logger, so need to reset loglevel after it's done.
logger = logging.getLogger()
orig_level = logger.level
from policyuniverse.expander_minimizer import get_actions_from_statement
logger.setLevel(orig_level)

LINT_ERROR_MESSAGE = "IAM policy should not allow * Actions; List each required action explicitly instead"


def expanded(action):
    return action


def is_wild(action):
    wild_actions = []
    if isinstance(action, list):
        for a in action:
            if is_wild(a):
                wild_actions.append(a)
    else:
        if action.endswith("*"):
            wild_actions.append(action)
    return wild_actions


class IAMActionWildcard(CloudFormationLintRule):
    """Check for wildcards in IAM Action statements."""
    id = 'E-IAM-POLICY-ACTION-WILDCARD'
    shortdesc = '* on Action property is a bad idea'
    description = 'wildcard should not be used for Action in IAM policies'
    source_url = 'https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules'
    tags = ['iam']
    SEARCH_PROPS = ['Action']

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            if tm[-1] == "*" or ("*" in tm[-1] and isinstance(tm[-1], list)):
                violation_matches.append(RuleMatch(tm, LINT_ERROR_MESSAGE))
            else:
                wild_actions = is_wild(tm[-1])
                for wild_action in wild_actions:
                    expanded_actions = get_actions_from_statement({"Action": [wild_action]})
                    violation_matches.append(RuleMatch(tm, f"{LINT_ERROR_MESSAGE} matching actions for {wild_action} are: {json.dumps(list(expanded_actions))}"))
        return violation_matches
