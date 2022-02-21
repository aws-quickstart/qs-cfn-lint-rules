import re
import inspect
from cfnlint.rules import RuleMatch


def inherit_doc_string(cls):
    for base in inspect.getmro(cls):
        if base.__doc__ is not None:
            cls.__doc__ = base.__doc__
            break
    return cls


def deep_get(source_dict, list_of_keys, default_value=None):
    x = source_dict
    for k in list_of_keys:
        if isinstance(k, int):
            x = x[k]
        else:
            x = x.get(k, {})
    if not x:
        return default_value
    return x


def parameter_violating_default_noecho(parameter):
    if not parameter:
        return False
    if parameter["Type"] == "String":
        if not parameter.get("NoEcho"):
            return True
    #            if parameter.get('Default'):
    #                return True
    return False


def search_resources_for_disallowed_property_values(
    cfn, resource_type, prop_name
) -> []:
    """
    Searches all resources of resource type, to ensure property value (or nested value) is not present
    returns a list of paths to violating lines.
    Example use case: AWS::WAFv2::WebACL DefaultAction.Allow cannot be present
    """
    results = []
    for resource_name, resource_values in cfn.get_resources(
        [resource_type]
    ).items():
        path = ["Resources", resource_name, "Properties"]
        properties = resource_values.get("Properties", {})
        prop_value = deep_get(properties, prop_name.split("."))
        if not prop_value:
            return results
        results.append(path + prop_name.split("."))
    return results


def search_resources_for_property_value_violations(
    cfn, resource_type, prop_name, expected_prop_value
) -> []:
    """
    Searches all resources of resource type, to ensure property is expected value
    returns a list of paths to violating lines.
    """
    results = []
    for resource_name, resource_values in cfn.get_resources(
        [resource_type]
    ).items():
        path = ["Resources", resource_name, "Properties"]
        properties = resource_values.get("Properties", {})

        if prop_name not in properties.keys():
            results.append(path)
            return results

        if type(expected_prop_value) is list:
            if properties[prop_name] not in expected_prop_value:
                results.append(path + [prop_name])
        else:
            if properties[prop_name] is not expected_prop_value:
                results.append(path + [prop_name])
    return results


class StubRuleCommon:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _lint_error_message(self):
        return f"{self.resource_type} must have {self.property_name} configured {str(self.property_value)}"

    @property
    def _r_suffix(self):
        return "".join(self.resource_type.split(":")[1:])

    @property
    def id(self):
        return f"E{self._r_suffix}{self.property_name}"

    @property
    def shortdesc(self):
        return f"{self.resource_type} should have {self.property_name} enabled"

    @property
    def description(self):
        return f"{self.resource_type} should have {self.property_name} enabled"

    @property
    def __doc__(self):
        return f"""Verify {self.resource_type} resource types have {self.property_name}"""

    @property
    def tags(self):
        return [self.resource_type.split("::")[1].lower()]


class RequiredPropertyEnabledBase(StubRuleCommon):
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        for ln in search_resources_for_property_value_violations(
            cfn, self.resource_type, self.property_name, self.property_value
        ):
            matches.append(RuleMatch(ln, self._lint_error_message))
        return matches

    @property
    def __doc__(self):
        if hasattr(self, "property_value"):
            if not self.property_value:
                return f"""Verify {self.resource_type} resource types do not have property {self.property_name} enabled"""
        return f"""Verify {self.resource_type} resource types have property {self.property_name} enabled"""


class ProhibitedResource(StubRuleCommon):
    source_url = (
        "https://github.com/qs_cfn_lint_rules/qs-cfn-python-lint-rules"
    )

    def __init__(self, *args, **kwargs):
        super(StubRuleCommon, self).__init__(*args, **kwargs)

    @property
    def _lint_error_message(self):
        return f"{self.resource_type} is prohibited"

    @property
    def id(self):
        return f"E{self._r_suffix}Prohibited"

    @property
    def shortdesc(self):
        return f"{self.resource_type} is prohibited"

    @property
    def description(self):
        return f"{self.resource_type} is prohibited"

    def match(self, cfn):
        """Basic Matching"""
        results = []
        for resource_name in cfn.get_resources([self.resource_type]).keys():
            path = ["Resources", resource_name]
            results.append(RuleMatch(path, self._lint_error_message))
        return results


class ProhibitedResourceProperty(StubRuleCommon):
    @property
    def _lint_error_message(self):
        return f"{self.resource_type} must have not have {self.property_name} configured"

    @property
    def id(self):
        return (
            f"E{self._r_suffix}{re.sub('.','',self.property_name)}Prohibited"
        )

    @property
    def shortdesc(self):
        return f"{self.resource_type} should not have {self.property_name} enabled"

    @property
    def description(self):
        return f"{self.resource_type} should not have {self.property_name} enabled"

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        for ln in search_resources_for_disallowed_property_values(
            cfn, self.resource_type, self.property_name
        ):
            matches.append(RuleMatch(ln, self._lint_error_message))
        return matches


class ParameterNoEchoDefault(StubRuleCommon):
    @property
    def _lint_error_message(self):
        if type(self.property_names) == list:
            return f"{self.resource_type} properties cannot be a plaintext string, or reference a parameter with NoEcho false and a default value"
        else:
            return f"{self.resource_type}/{self.property_name} cannot be a plaintext string, or reference a parameter with NoEcho false and a default value"

    @property
    def _r_suffix(self):
        return "".join(self.resource_type.split(":")[1:])

    @property
    def id(self):
        if type(self.property_names) == list:
            return f"E{self._r_suffix}DefaultNoEcho"
        else:
            return f"E{self._r_suffix}{self.property_names}DefaultNoEcho"

    @property
    def _condensed_doc(self):
        if type(self.property_names) == list:
            return (
                f"{self.resource_type} properties should not be easily exposed"
            )
        else:
            return f"{self.resource_type}/{self.property_names} should not be easily exposed"

    @property
    def shortdesc(self):
        return self._condensed_doc

    @property
    def description(self):
        return self._condensed_doc

    @property
    def __doc__(self):
        return self._condensed_doc

    @property
    def tags(self):
        return [self.resource_type.split("::")[1].lower()]

    def _iterate_properties(
        self, resource_name, resource_data, parameters, property_list
    ):
        for property_name in property_list:
            path = ["Resources", resource_name]
            prop_value = deep_get(
                resource_data.get("Properties", {}), property_name.split(".")
            )
            if type(prop_value) == str:
                yield RuleMatch(
                    path + ["Properties", property_name],
                    self._lint_error_message,
                )
            if issubclass(type(prop_value), dict):
                if prop_value.get("Ref"):
                    pn = prop_value["Ref"]
                    if parameter_violating_default_noecho(parameters.get(pn)):
                        yield RuleMatch(
                            path + ["Properties"] + property_name.split("."),
                            self._lint_error_message,
                        )

    def match(self, cfn):
        """Basic Matching"""
        results = []
        if not type(self.property_names) == list:
            property_list = [self.property_names]
        else:
            property_list = self.property_names
        parameters = cfn.get_parameters()
        for resource_name, resource_data in cfn.get_resources(
            [self.resource_type]
        ).items():
            for match in self._iterate_properties(
                resource_name, resource_data, parameters, property_list
            ):
                results.append(match)
        return results
