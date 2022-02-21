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
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from qs_cfn_lint_rules.common import (
    search_resources_for_property_value_violations as srfpvv,
)

LINT_ERROR_MESSAGE = "AWS::RDS::DBCluster must have StorageEncryption enabled"


class StorageEncryptionEnabled(CloudFormationLintRule):
    """Verify RDS Clusters have StorageEncryptionEnabled"""

    id = "ERDSStorageEncryptionEnabled"
    shortdesc = "AWS::RDS::DBCluster should have StorageEncryption enabled"
    description = "AWS::RDS::DBCluster should have StorageEncryption enabled"
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )
    tags = ["rds"]

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        for ln in srfpvv(cfn, "AWS::RDS::DBCluster", "StorageEncrypted", True):
            matches.append(RuleMatch(ln, LINT_ERROR_MESSAGE))
        return matches
