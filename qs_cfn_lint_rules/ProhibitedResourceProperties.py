from qs_cfn_lint_rules.common import (
    ProhibitedResourceProperty,
    inherit_doc_string,
)
from cfnlint.rules import CloudFormationLintRule


@inherit_doc_string
class WAFV2NoDefaultAllow(ProhibitedResourceProperty, CloudFormationLintRule):
    resource_type = "AWS::WAFv2::WebACL"
    property_name = "DefaultAction.Allow"
