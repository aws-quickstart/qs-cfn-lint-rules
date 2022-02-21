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


LINT_ERROR_MESSAGE = "IAM policy exclusions must provide exclusion reason eg.: {Metadata: {cfn-lint: {config: {ignore_reasons: {EIAMPolicyActionWildcard: this is the justification for the exclude}}}}"


class IAMExcludeReason(CloudFormationLintRule):
    """Check that IAM exclusions have a reason specified."""

    id = "E-IAM-IGNORE-JUSTIFICATION"
    shortdesc = "excluding IAM best practices requires justification"
    description = (
        "when excluding an IAM policy rule, you must provide a justification"
    )
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["iam"]
    SEARCH_PROPS = ["cfn-lint"]

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        term_matches = []
        for prop in self.SEARCH_PROPS:
            term_matches += cfn.search_deep_keys(prop)
        for tm in term_matches:
            config = tm[-1]
            if "ignore_checks" not in config:
                continue
            if "EIAMPolicyResourceWildcard" in config["ignore_checks"]:
                if "ignore_reasons" not in config:
                    violation_matches.append(RuleMatch(tm, LINT_ERROR_MESSAGE))
                elif (
                    "EIAMPolicyResourceWildcard"
                    not in config["ignore_reasons"]
                ):
                    violation_matches.append(RuleMatch(tm, LINT_ERROR_MESSAGE))
                elif (
                    len(config["ignore_reasons"]["EIAMPolicyResourceWildcard"])
                    < 1
                ):
                    violation_matches.append(RuleMatch(tm, LINT_ERROR_MESSAGE))
            if "EIAMPolicyActionWildcard" in config["ignore_checks"]:
                if "ignore_reasons" not in config:
                    violation_matches.append(RuleMatch(tm, LINT_ERROR_MESSAGE))
                elif (
                    "EIAMPolicyActionWildcard" not in config["ignore_reasons"]
                ):
                    violation_matches.append(RuleMatch(tm, LINT_ERROR_MESSAGE))
                elif (
                    len(config["ignore_reasons"]["EIAMPolicyActionWildcard"])
                    < 1
                ):
                    violation_matches.append(RuleMatch(tm, LINT_ERROR_MESSAGE))
        return violation_matches
