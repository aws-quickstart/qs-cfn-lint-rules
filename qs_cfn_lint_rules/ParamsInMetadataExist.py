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
from cfnlint.rules.metadata.InterfaceParameterExists import (
    InterfaceParameterExists as I,
)


class Base(CloudFormationLintRule):
    """Wrapper for W4001 - we need it as an error."""

    id = "E9009"
    shortdesc = "Parameters referenced in metadata must exist in the template."
    description = "Making sure parameters in metadataexist within the template"
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["label"]

    def match(self, cfn):
        """Basic Matching"""
        converted_matches = []
        for m in I.match(self, cfn):
            converted_matches.append(RuleMatch(m.path, self.shortdesc))
        return converted_matches
