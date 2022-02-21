from qs_cfn_lint_rules.common import ParameterNoEchoDefault, inherit_doc_string
from cfnlint.rules import CloudFormationLintRule


@inherit_doc_string
class RDSDBInstanceNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::RDS::DBInstance"
    property_names = [
        # 'MasterUsername', F24
        "MasterUserPassword"
    ]
    CFN_NAG_RULES = ["F23"]


@inherit_doc_string
class SimpleADPasswordNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::DirectoryService::SimpleAD"
    property_names = ["Password"]
    CFN_NAG_RULES = ["F31"]


@inherit_doc_string
class RDSDBInstanceNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::RDS::DBCluster"
    property_names = ["MasterUserPassword"]
    CFN_NAG_RULES = ["F34"]


@inherit_doc_string
class RedshiftClusterNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::Redshift::DBCluster"
    property_names = ["MasterUserPassword"]
    CFN_NAG_RULES = ["F35"]


@inherit_doc_string
class SimpleADPasswordNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::DirectoryService::MicrosoftAD"
    property_names = ["Password"]
    CFN_NAG_RULES = ["F36"]


@inherit_doc_string
class DMSEndpointNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::DMS::Endpoint"
    property_names = ["Password", "MongoDbSettings.Password"]
    CFN_NAG_RULES = ["F37", "F55"]


@inherit_doc_string
class AmplifyAppNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::Amplify::App"
    property_names = ["AccessToken", "BasicAuthConfig", "OauthToken"]
    CFN_NAG_RULES = ["F41", "F50", "F58"]


@inherit_doc_string
class AmplifyBranchNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::Amplify::Branch"
    property_names = ["BasicAuthConfig.Password"]
    CFN_NAG_RULES = ["F60"]


@inherit_doc_string
class PinpointAPNSanboxNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::Pinpoint::APNSandbox"
    property_names = ["PrivateKey", "TokenKey"]
    CFN_NAG_RULES = ["F42", "F43"]


@inherit_doc_string
class ElastiCacheReplicationGroupNoEcho(
    ParameterNoEchoDefault, CloudFormationLintRule
):
    resource_type = "AWS::ElastiCache::ReplicationGroup"
    property_names = ["AuthToken"]
    CFN_NAG_RULES = ["F44"]


@inherit_doc_string
class LambdaPermissionNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::Lambda::Permission"
    property_names = ["EventSourceToken"]
    CFN_NAG_RULES = ["F45"]


@inherit_doc_string
class PinpointAPNSVoipSandboxChannelNoEcho(
    ParameterNoEchoDefault, CloudFormationLintRule
):
    resource_type = "AWS::Pinpoint::APNSVoipSandboxChannel"
    property_names = ["PrivateKey", "TokenKey"]
    CFN_NAG_RULES = ["F46", "F47"]


@inherit_doc_string
class PinpointAPNSChannelNoEcho(
    ParameterNoEchoDefault, CloudFormationLintRule
):
    resource_type = "AWS::Pinpoint::APNSChannel"
    property_names = ["PrivateKey", "TokenKey"]
    CFN_NAG_RULES = ["F56", "F57"]


@inherit_doc_string
class PinpointAPNSVoipChannelNoEcho(
    ParameterNoEchoDefault, CloudFormationLintRule
):
    resource_type = "AWS::Pinpoint::APNSVoipChannel"
    property_names = ["PrivateKey", "TokenKey"]
    CFN_NAG_RULES = ["F48", "F49"]


@inherit_doc_string
class IAMUserLoginProfileNoEcho(
    ParameterNoEchoDefault, CloudFormationLintRule
):
    resource_type = "AWS::IAM::User"
    property_names = ["LoginProfile.Password"]
    CFN_NAG_RULES = ["F51"]


# @inherit_doc_string
# class AmazonMQBrokerNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
#     resource_type = 'AWS::AmazonMQ::Broker'
#     property_names = ''
#     CFN_NAG_RULES = ['F51']


@inherit_doc_string
class AppStreamDirectoryConfigNoEcho(
    ParameterNoEchoDefault, CloudFormationLintRule
):
    resource_type = "AWS::AppStream::DirectoryConfig"
    property_names = ["ServiceAccountCredentials.AccountPassword"]
    CFN_NAG_RULES = ["F53"]


@inherit_doc_string
class OpsWorksStackNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::OpsWorks::Stack"
    property_names = [
        "RDSDbInstance.DbPassword",
        "CustomCookbooksSource.Password",
    ]
    CFN_NAG_RULES = ["F54", "F62"]


@inherit_doc_string
class OpsWorksAppNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::OpsWorks::App"
    property_names = ["SslConfiguration.PrivateKey", "AppSource.Password"]
    CFN_NAG_RULES = ["F54", "F67"]


@inherit_doc_string
class EMRClusterNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::EMR::Cluster"
    property_names = [
        "KerberosAttributes.CrossRealmTrustPrincipal.Password",
        "KerberosAttributes.ADDomain.JoinPassword",
        "KerberosAttributes.KdcAdmin.Password",
    ]
    CFN_NAG_RULES = ["F63", "F64", "F65"]


@inherit_doc_string
class KinesisFirehoseDeliveryStreamNoEcho(
    ParameterNoEchoDefault, CloudFormationLintRule
):
    resource_type = "AWS::KinesisFirehose::DeliveryStream"
    property_names = [
        "RedshiftDestinationConfiguration.Password",
        "SplunkDestinationConfig.HECToken",
    ]
    CFN_NAG_RULES = ["F66", "F68"]


@inherit_doc_string
class DocDBDBClusterNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::DocDB::DBCluster"
    property_names = ["MasterUserPassword"]
    CFN_NAG_RULES = ["F70"]


@inherit_doc_string
class DocDBDBClusterNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "AWS::ManagedBlockchain::Member"
    property_names = ["MemberFabricConfiguration.AdminPasswordRule"]
    CFN_NAG_RULES = ["F71"]


@inherit_doc_string
class ASKSkillNoEcho(ParameterNoEchoDefault, CloudFormationLintRule):
    resource_type = "Alexa::ASK::Skill"
    property_names = [
        "AuthenticationConfiguration.ClientSecret",
        "AuthenticationConfiguration.RefreshToken",
    ]
    CFN_NAG_RULES = ["F74", "F75"]
