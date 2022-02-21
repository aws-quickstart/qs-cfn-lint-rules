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
    """Check Name Casing"""

    id = "W9001"
    shortdesc = "Name casing should be PascalCase"
    description = "Making sure all names are PascalCase"
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["case"]

    def match(self, cfn):
        """Basic Matching"""
        matches = []

        for x in cfn.template:
            if x in ["Parameters", "Outputs", "Resources"]:
                for i in cfn.template[x]:
                    if i[0] != i[0].upper():
                        message = "{0} names should be PascalCase"
                        matches.append(
                            RuleMatch([x, i], message.format(x.rstrip("s")))
                        )
        return matches
