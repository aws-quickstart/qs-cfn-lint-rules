from qs_cfn_lint_rules.common import (
    RequiredPropertyEnabledBase,
    inherit_doc_string,
)
from cfnlint.rules import CloudFormationLintRule


@inherit_doc_string
class CFNNAGF25(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::ElastiCache::ReplicationGroup"
    property_name = "AtRestEncryptionEnabled"
    property_value = True
    CFN_NAG_RULES = ["F25"]


@inherit_doc_string
class CFNNAGF28(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::Redshift::Cluster"
    property_name = "Encrypted"
    property_value = True
    CFN_NAG_RULES = ["F28"]


@inherit_doc_string
class CFNNAGF29p1(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::Workspaces::Workspace"
    property_name = "RootVolumeEncryptionEnabled"
    property_value = True
    CFN_NAG_RULES = ["F29"]


@inherit_doc_string
class CFNNAGF30(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::Neptune::DBCluster"
    property_name = "StorageEncrypted"
    property_value = True
    CFN_NAG_RULES = ["F30"]


@inherit_doc_string
class CFNNAGF32(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::EFS::Filesystem"
    property_name = "Encrypted"
    property_value = True
    CFN_NAG_RULES = ["F32"]


@inherit_doc_string
class CFNNAGF33(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::Neptune::DBCluster"
    property_name = "StorageEncrypted"
    property_value = True
    CFN_NAG_RULES = ["F33"]


@inherit_doc_string
class CFNNAGF103(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::KMS::Key"
    property_name = "EnableKeyRotation"
    property_value = True
    CFN_NAG_RULES = ["F103"]


@inherit_doc_string
class CFNNAGF22(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::RDS::DBInstance"
    property_name = "PubliclyAccessible"
    property_value = False
    CFN_NAG_RULES = ["F22"]


@inherit_doc_string
class CFNNAGF78(RequiredPropertyEnabledBase, CloudFormationLintRule):
    resource_type = "AWS::Cognito::UserPool"
    property_name = "MfaConfiguration"
    property_value = ["OPTIONAL", "ON"]
    CFN_NAG_RULES = ["F78"]


# 'AWS::RDS::DBCluster', 'StorageEncryptionEnabled', True
