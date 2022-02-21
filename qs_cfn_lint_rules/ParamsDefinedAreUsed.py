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
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.rules.parameters.Used import Used


class Base(CloudFormationLintRule):
    """Wrapper for W2001 - we need it as an error."""

    id = "E9010"
    shortdesc = "Parameters defined in the template must be used."
    description = "Making sure parameters are used."
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["params"]

    def determine_changes(self, cfn):
        delete_lines = []
        for match in self.match(cfn):
            setattr(match, "delete_lines", True)
            delete_lines.append(match)
        return delete_lines

    def match(self, cfn):
        converted_matches = []
        for m in Used.match(self, cfn):
            converted_matches.append(RuleMatch(m.path, self.shortdesc))
        return converted_matches
