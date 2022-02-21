from qs_cfn_lint_rules.common import ProhibitedResource, inherit_doc_string
from cfnlint.rules import CloudFormationLintRule


@inherit_doc_string
class NoSimpleDBDomain(ProhibitedResource, CloudFormationLintRule):
    resource_type = "AWS::SimpleDB::Domain"
    CFN_NAG_RULES = ["F77"]
