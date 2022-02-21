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

LINT_ERROR_MESSAGE = "IAM policy should not allow * resource; This method in this in this policy support granular permissions"

custom_dict_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/iam_methods.json"
)
with open(custom_dict_path) as f:
    d = f.read()
resource_only = json.loads(d)


def determine_perms():
    custom_dict_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/granular_permissions.json",
    )
    with open(custom_dict_path) as f:
        _gp = json.load(f)
    perms = {}
    for method_name, method_data in _gp.items():
        _r = set(
            [
                f"{method_name.split(':')[0]}/{k}"
                for k in method_data["resource_types"].keys()
                if k != ""
            ]
        )
        if not _r:
            continue
        perms[method_name] = _r
    return perms


def determine_wildcard_resource_violations(cfn, policy_path):
    def _determine_if_safe(iam_method):
        if iam_method.endswith("*"):
            return True
        return resource_only.get(iam_method, False)

    violating_methods = []
    policy = deep_get(cfn.template, policy_path, [])

    if policy["Effect"] == "Deny":
        return violating_methods

    if policy.get("Condition"):
        return violating_methods

    if isinstance(policy["Action"], six.string_types):
        if not _determine_if_safe(policy["Action"]):
            violating_methods.append(policy_path + ["Action"])

    if isinstance(policy["Action"], list):
        for idx, iam_method in enumerate(policy["Action"]):
            if isinstance(iam_method, list):
                for idxx, ia in enumerate(iam_method):
                    if not _determine_if_safe(ia):
                        violating_methods.append(
                            policy_path + ["Action", idxx]
                        )
            elif not _determine_if_safe(iam_method):
                violating_methods.append(policy_path + ["Action", idx])
    return violating_methods


class IAMResourceWildcard(CloudFormationLintRule):
    """Check ARN for partition agnostics."""

    id = "EIAMPolicyWildcardResource"
    shortdesc = "* on Resource property is a bad idea"
    description = "Making sure wildcard resources are only used where no other option exists"
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["iam"]
    SEARCH_PROPS = ["Resource"]

    def determine_changes(self, cfn):
        PERMS = determine_perms()
        subs = []
        # raise
        _policy_paths = []
        for match in self.match(cfn):
            if match.policy_path in _policy_paths:
                continue
            _policy_paths.append(match.policy_path)
        for _ppath in _policy_paths:
            m2a = {}
            _new_policies = []
            policy = deep_get(cfn.template, _ppath, [])
            # raise
            for a in policy["Action"]:
                if isinstance(a, list) and (len(a) == 1):
                    a = a[0]
                if PERMS.get(a):
                    for m in PERMS[a]:
                        if m2a.get(m):
                            m2a[m].add(a)
                        else:
                            m2a[m] = {a}
            ignore = []
            mod_policy = []
            for _p1 in policy["Action"]:
                if isinstance(_p1, list):
                    for _p2 in _p1:
                        mod_policy.append(_p2)
                else:
                    mod_policy.append(_p1)
            for rn in sorted(m2a, key=lambda k: len(m2a[k])):
                _al = [k for k in m2a[rn] if k not in ignore]
                if _al:
                    _new_policies.append(
                        {
                            "Effect": "Allow",
                            "Action": _al,
                            "Resource": {"Fn::Ref": rn},
                        }
                    )
                ignore += _al
            subs.append(
                (_ppath, policy, _new_policies, {"append_after": True})
            )
            for a in ignore:
                subs.append(
                    RuleMatch(
                        _ppath + ["Action", mod_policy.index(a)],
                        "WHATEVER",
                        delete_lines=True,
                    )
                )
        # raise
        return subs

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            if tm[-1] not in ["*", ["*"]]:
                continue
            violating_methods = determine_wildcard_resource_violations(
                cfn, tm[:-2]
            )
            for ln in violating_methods:
                violation_matches.append(
                    RuleMatch(ln, LINT_ERROR_MESSAGE, policy_path=tm[:-2])
                )
        return violation_matches
