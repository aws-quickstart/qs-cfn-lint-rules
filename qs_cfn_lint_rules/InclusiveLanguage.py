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

deny_list = [
    ["abort", '"stop"'],
    ["blacklist", '"deny list"'],
    ["^execute", '"start" or "run"'],
    ["^hang", '"stop responding"'],
    ["kill", '"end" or "stop"'],
    ["master", '"primary", "main", or "leader"'],
    ["slave", '"replica", "secondary", or "standby"'],
    ["whitelist", '"allow list"'],
]


def match(s):
    for w in deny_list:
        if w[0] in s.lower():
            return w
    return None


class Base(CloudFormationLintRule):
    """Check for non-inclusive terms"""

    id = "E9101"
    shortdesc = "Use welcoming and inclusive language"
    description = "Checks that text is welcoming and inclusive as per Amazon Open Source Code of Conduct https://aws.github.io/code-of-conduct"
    source_url = "https://github.com/qs_cfn_lint_rules/qs_cfn_lint_rules"
    tags = ["language"]

    def match(self, cfn):
        """Find all strings and match a deny list of sub strings"""
        message = '"{0}" may be interpreted as a biased term. Consider a more inclusive alternative, such as {1}'
        matches = []

        def recurse_template(item, path=None):
            if path is None:
                path = []
            if isinstance(item, dict):
                for k, v in item.items():
                    p = path.copy()
                    p.append(k)
                    # recurse_template(k, p)
                    recurse_template(v, p)
            if isinstance(item, list):
                for i in range(len(item) - 1):
                    p = path.copy()
                    p.append(i)
                    recurse_template(item[i], p)
            if isinstance(item, str):
                t = match(item)
                if t:
                    matches.append(RuleMatch(path, message.format(t[0], t[1])))
            return matches

        recurse_template(cfn.template)
        return matches

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
                    "ParameterGroups"
                    in cfn.template["Metadata"][
                        "AWS::CloudFormation::Interface"
                    ].keys()
                ):
                    for x in cfn.template["Metadata"][
                        "AWS::CloudFormation::Interface"
                    ]["ParameterGroups"]:
                        labels += x["Parameters"]

        if "Parameters" not in cfn.template.keys():
            return matches
        else:
            for x in cfn.template["Parameters"]:
                if str(x) not in labels:
                    matches.append(
                        RuleMatch(["Parameters", x], message.format(x))
                    )
        return matches
