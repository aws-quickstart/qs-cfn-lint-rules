import sys
import cfnlint
import six

master_template_path = sys.argv[1]

try:
    cfn = cfnlint.decode.cfn_yaml.load(master_template_path)
except Exception as e:
    print("Exception parsing: '{}'".format(master_template_path))
    # print(str(e))
    exit(1)

# print(cfn)


def get_resources(template, resource_type=[]):
    """
    Get Resources
    Filter on type when specified
    """
    resources = template.get("Resources", {})
    if not isinstance(resources, dict):
        return {}
    if isinstance(resource_type, six.string_types):
        resource_type = [resource_type]

    results = {}
    for k, v in resources.items():
        if isinstance(v, dict):
            if (v.get("Type", None) in resource_type) or (
                not resource_type and v.get("Type") is not None
            ):
                results[k] = v

    return results


try:
    cfn_resources = get_resources(
        cfn, resource_type=["AWS::CloudFormation::Stack"]
    )
except Exception as a:
    print("Exception parsing: '{}'".format(master_template_path))
    # print(str(e))
    exit(2)


printed = False
for r_name, r_values in cfn_resources.items():
    properties = r_values.get("Properties")
    child_template_url = properties.get("TemplateURL")
    if not printed:
        printed = True
        print(master_template_path)
    print(child_template_url)
