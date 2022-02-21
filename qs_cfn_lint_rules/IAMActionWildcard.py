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
from qs_cfn_lint_rules.common import deep_get
import logging
import os

# policyuniverse messes with the global logger, so need to reset loglevel after it's done.
logger = logging.getLogger()
orig_level = logger.level
from policyuniverse.expander_minimizer import get_actions_from_statement
from policyuniverse import service_data

logger.setLevel(orig_level)

LINT_ERROR_MESSAGE = "IAM policy should not allow * Actions; List each required action explicitly instead"
DONT_EXPAND = ["s3:Get*", "s3:Put*", "s3:List*"]
CAMEL_CASE = {}

for sd in service_data.values():
    for k in sd["actions"].keys():
        CAMEL_CASE[f"{sd['prefix']}:{k}".lower()] = f"{sd['prefix']}:{k}"


def determine_perms(service_data):
    perms = {}
    for method_name, method_data in service_data.items():
        _r = set([k for k in method_data["resource_types"].keys() if k != ""])
        if not _r:
            continue
        perms[method_name] = _r
    return perms


custom_dict_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data/granular_permissions.json",
)
with open(custom_dict_path) as f:
    d = f.read()
_gp = json.loads(d)
GRANULAR_PERMS = determine_perms(_gp)


def expanded(action):
    return action


def is_wild(action):
    wild_actions = []
    if isinstance(action, list):
        for a in action:
            if is_wild(a):
                wild_actions.append(a)
    else:
        if action.endswith("*") and (not action in DONT_EXPAND):
            wild_actions.append(action)
    return wild_actions


def get_effect(template, keys: list):
    # raise
    k = keys.copy()
    while len(k) > 2:
        template = template[k.pop(0)]
    try:
        return template["Effect"]
    except KeyError:
        return "deny"


class IAMActionWildcard(CloudFormationLintRule):
    """Check for wildcards in IAM Action statements."""

    id = "EIAMPolicyActionWildcard"
    shortdesc = "* on Action property is a bad idea"
    description = "wildcard should not be used for Action in IAM policies"
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["iam"]
    SEARCH_PROPS = ["Action"]

    def determine_changes(self, cfn):
        substitutions = []
        for match in self.match(cfn):
            if not hasattr(match, "expanded_actions"):
                continue
            _v = deep_get(cfn.template, match.path)
            if (
                hasattr(match, "expanded_on_newline")
                and match.expanded_on_newline
            ):
                subs = (
                    match.path,
                    _v,
                    sorted(list(match.expanded_actions)),
                    {"replace": True, "newline": True},
                )
            else:
                subs = (match.path, _v, sorted(list(match.expanded_actions)))
            substitutions.append(subs)
        return substitutions

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            # if not isinstance(tm[-3], int):
            #     continue
            if get_effect(cfn.template, tm).lower() == "deny":
                continue
            if tm[-1] == "*" or ("*" in tm[-1] and isinstance(tm[-1], list)):
                violation_matches.append(
                    RuleMatch(tm[:-1], LINT_ERROR_MESSAGE)
                )
            else:
                wild_actions = is_wild(tm[-1])
                for wild_action in wild_actions:
                    expanded_actions = {
                        CAMEL_CASE.get(k, k)
                        for k in get_actions_from_statement(
                            {"Action": [wild_action]}
                        )
                    }
                    msg = f"{LINT_ERROR_MESSAGE} matching actions for {wild_action} are: {json.dumps(list(expanded_actions))}"
                    if isinstance(tm[-1], list):
                        violation_matches.append(
                            RuleMatch(
                                tm[:-1] + [tm[-1].index(wild_action)],
                                msg,
                                expanded_actions=expanded_actions,
                                expanded_on_newline=True,
                            )
                        )
                    else:
                        violation_matches.append(
                            RuleMatch(
                                tm[:-1],
                                msg,
                                expanded_actions=expanded_actions,
                                expanded_on_newline=True,
                            )
                        )
        return violation_matches
