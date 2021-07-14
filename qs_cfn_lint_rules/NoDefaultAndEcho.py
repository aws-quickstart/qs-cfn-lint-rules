from qs_cfn_lint_rules.common import ParameterNoEchoDefault, inherit_doc_string
from cfnlint.rules import CloudFormationLintRule

@inherit_doc_string
class RDSDBInstanceNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = 'AWS::RDS::DBInstance'
    property_name = [
        'MasterUsername',
        'MasterUserPassword'
    ]
    CFN_NAG_RULES = ['F23', 'F24']

@inherit_doc_string
class SimpleADPasswordNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = 'AWS::DirectoryService::SimpleAD'
    property_name = 'Password'
    CFN_NAG_RULES = ['F31']

@inherit_doc_string
class RDSDBInstanceNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = 'AWS::RDS::DBCluster'
    property_name = [
        'MasterUsername',
        'MasterUserPassword'
    ]
    CFN_NAG_RULES = ['F34', 'F35']

@inherit_doc_string
class SimpleADPasswordNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = 'AWS::DirectoryService::MicrosoftAD'
    property_name = 'Password'
    CFN_NAG_RULES = ['F36']

@inherit_doc_string
class DMSEndpointNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = 'AWS::DMS::Endpoint'
    property_name = 'Password'
    CFN_NAG_RULES = ['F37']

@inherit_doc_string
class AmplifyAppNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = 'AWS::Amplify::App'
    property_name = 'AccessToken'
    CFN_NAG_RULES = ['F41']

@inherit_doc_string
class PinpointAPNSanboxNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = 'AWS::Pinpoint::APNSandbox'
    property_name = [
        'PrivateKey',
        'TokenKey'
    ]
    CFN_NAG_RULES = ['F42', 'F43']

