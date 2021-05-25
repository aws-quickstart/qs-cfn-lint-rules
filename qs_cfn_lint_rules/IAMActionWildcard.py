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
from policyuniverse import service_data
logger.setLevel(orig_level)

LINT_ERROR_MESSAGE = "IAM policy should not allow * Actions; List each required action explicitly instead"

CAMEL_CASE = {}
for sd in service_data.values():
    for k in sd['actions'].keys():
        CAMEL_CASE[f"{sd['prefix']}:{k}".lower()] = f"{sd['prefix']}:{k}"

def expanded(action):
    return action

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


def get_effect(template, keys: list):
    k = keys.copy()
    while len(k) > 2:
        template = template[k.pop(0)]
    return template['Effect']


class IAMActionWildcard(CloudFormationLintRule):
    """Check for wildcards in IAM Action statements."""
    id = 'EIAMPolicyActionWildcard'
    shortdesc = '* on Action property is a bad idea'
    description = 'wildcard should not be used for Action in IAM policies'
    source_url = 'https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules'
    tags = ['iam']
    SEARCH_PROPS = ['Action']

    def determine_changes(self, cfn):
        substitutions = {}
        for match in self.match(cfn):
            if not hasattr(match, 'expanded_actions'):
                return {}
            _v = deep_get(cfn.template, match.path)
            substitutions[_v.start_mark.index] = (
                _v.end_mark.index,
                match.path,
                sorted(list(match.expanded_actions)),
                _v.start_mark.line
            )
        return substitutions

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            if not isinstance(tm[-3], int):
                continue
            if get_effect(cfn.template, tm).lower() == 'deny':
                continue
            if tm[-1] == "*" or ("*" in tm[-1] and isinstance(tm[-1], list)):
                violation_matches.append(RuleMatch(tm[:-1], LINT_ERROR_MESSAGE))
            else:
                wild_actions = is_wild(tm[-1])
                for wild_action in wild_actions:
                    expanded_actions = {CAMEL_CASE.get(k) for k in get_actions_from_statement({"Action": [wild_action]})}
                    violation_matches.append(RuleMatch(tm[:-1]+[tm[-1].index(wild_action)], f"{LINT_ERROR_MESSAGE} matching actions for {wild_action} are: {json.dumps(list(expanded_actions))}", expanded_actions=expanded_actions))
        return violation_matches
