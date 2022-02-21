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
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from qs_cfn_lint_rules.common import deep_get

LINT_ERROR_MESSAGE = (
    "EIAM* rules must not be excluded globally. only at the resource level"
)


class ValidateRuleExclusions(CloudFormationLintRule):
    """Check ARN for partition agnostics."""

    id = "EValidateIAMRuleExclusions"
    shortdesc = "* on Resource property is a bad idea"
    description = "Making sure wildcard resources are only used where no other option exists"
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["iam"]
    SEARCH_PROPS = ["Resource"]

    def match(self, cfn):
        """Basic Matching"""
        violation_matches = []
        for idx, exclude in enumerate(
            deep_get(
                cfn.template,
                ["Metadata", "cfn-lint", "config", "ignore_checks"],
                [],
            )
        ):
            if exclude.startswith("EIAM"):
                violation_matches.append(
                    RuleMatch(
                        [
                            "Metadata",
                            "cfn-lint",
                            "config",
                            "ignore_checks",
                            idx,
                        ],
                        LINT_ERROR_MESSAGE,
                    )
                )
        return violation_matches
