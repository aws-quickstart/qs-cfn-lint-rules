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


class Base(CloudFormationLintRule):
    """Check Parameter Labels Exist"""

    id = "W9002"
    shortdesc = "Each parameter should have a label"
    description = "AWS::CloudFormation::Interface should contain ParameterLabels for each parameter"
    source_url = "https://github.com/qs_cfn_lint_rules/qs_cfn_lint_rules"
    tags = ["parameters"]

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        message = "Parameter {0} is missing ParameterLabel"
        labels = []

        if self.id in cfn.template.get("Metadata", {}).get("QSLint", {}).get(
            "Exclusions", []
        ):
            return matches
        if "Metadata" in cfn.template.keys():
            if (
                "AWS::CloudFormation::Interface"
                in cfn.template["Metadata"].keys()
            ):
                if (
                    "ParameterLabels"
                    in cfn.template["Metadata"][
                        "AWS::CloudFormation::Interface"
                    ].keys()
                ):
                    for x in cfn.template["Metadata"][
                        "AWS::CloudFormation::Interface"
                    ]["ParameterLabels"]:
                        labels.append(str(x))

        if "Parameters" not in cfn.template.keys():
            return matches
        else:
            for x in cfn.template["Parameters"]:
                if str(x) not in labels:
                    matches.append(
                        RuleMatch(["Parameters", x], message.format(x))
                    )
        return matches
