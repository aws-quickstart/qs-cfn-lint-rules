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
from cfnlint.rules import CloudFormationLintRule  # pylint: disable=E0401
from cfnlint.rules import RuleMatch

import os
import yaml


from pathlib import Path
from collections import OrderedDict


class MyTemplateParser(object):
    """Handles the loading and dumping of CloudFormation YAML templates."""

    def __init__(self, logger=None, loglevel='error', botolevel='error'):
        pass

    @staticmethod
    def ordered_safe_load(stream, object_pairs_hook=OrderedDict):
        class OrderedSafeLoader(yaml.SafeLoader):
            pass

        def _construct_int_without_octals(loader, node):
            value = str(loader.construct_scalar(node)).replace('_', '')
            try:
                return int(value, 10)
            except ValueError:
                return loader.construct_yaml_int(node)

        def _construct_mapping(loader, node):
            loader.construct_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))

        def _construct_cfn_tag(loader, tag_suffix, node):
            tag_suffix = u'!{}'.format(tag_suffix)
            if isinstance(node, yaml.ScalarNode):
                # Check if block literal. Inject for later use in the YAML dumps.
                if node.style == '|':
                    return u'{0} {1} {2}'.format(tag_suffix, '|', node.value)
                else:
                    return u'{0} {1}'.format(tag_suffix, node.value)
            elif isinstance(node, yaml.SequenceNode):
                constructor = loader.construct_sequence
            elif isinstance(node, yaml.MappingNode):
                constructor = loader.construct_mapping
            else:
                raise BaseException('[ERROR] Unknown tag_suffix: {}'.format(tag_suffix))

            return OrderedDict([(tag_suffix, constructor(node))])

        OrderedSafeLoader.add_constructor(u'tag:yaml.org,2002:int', _construct_int_without_octals)
        OrderedSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)
        OrderedSafeLoader.add_multi_constructor('!', _construct_cfn_tag)

        return yaml.load(stream, OrderedSafeLoader)

    def my_load_yaml_function(self, template_file):
        template_data = self.ordered_safe_load(
            open(template_file, 'rU'), object_pairs_hook=OrderedDict)

        return template_data

    @staticmethod
    def template_url_to_path(current_template_path, template_url):

        template_path = ""

        # Strip away CFN builtins around this
        if isinstance(template_url, dict):  # URL is a dictionary
            if "Fn::Sub" in template_url.keys():  # There is a !Sub
                # TODO: Explain what we are doing and why
                if isinstance(template_url["Fn::Sub"], str):
                    template_path = template_url["Fn::Sub"].split("}")[-1]
                else:
                    template_path = template_url["Fn::Sub"][0].split("}")[-1]
            elif "Fn::Join" in list(template_url.keys())[0]:
                # TODO: Explain what we are doing/why
                template_path = template_url["Fn::Join"][1][-1]
            elif "Fn::If" in list(template_url.keys())[0]:
                # TODO: Eval an If ...
                # Potentially check either or both if it is single level
                message = "Unable to evaluate Fn::If in TemplateURL: %s"
                raise Exception(message % (template_url))
            else:
                message = "Unable to parse template_path from TemplateURL: %s"
                raise Exception(message % (template_url))
        elif isinstance(template_url, str):
            template_path = "/".join(template_url.split("/")[-2:])

        # Try current template dir
        project_root = Path(
            os.path.dirname(current_template_path)
        )

        child_template_file = template_path.split("/")[-1]
        final_template_path = Path(
            "/".join(
                [str(project_root), str(child_template_file)]
            )
        )

        if final_template_path.exists():
            return final_template_path

        # Try current template dir + prefix
        final_template_path = Path(
            "/".join(
                [str(project_root), str(template_path)]
            )
        )

        if final_template_path.exists():
            return final_template_path

        # Try one directory up
        project_root = Path(
            os.path.normpath(
                os.path.dirname(current_template_path) + "/../"
            )
        )

        final_template_path = Path(
            "/".join(
                [str(project_root), str(template_path)]
            )
        )

        if final_template_path.exists():
            return final_template_path

        message = "Failed to discover path for %s, path %s does not exist"
        raise Exception(message % (template_url, template_path))


class MissingParameter(CloudFormationLintRule):
    """Check Nested Stack Parameters"""
    id = 'E9199'
    shortdesc = 'Parameters missing for nested stack'
    description = 'Check to make sure parameters for nested stack are correct'
    source_url = 'https://github.com/qs-cfn-lint-rules/qs_cfn_lint_rules'
    tags = ['case']

    @staticmethod
    def parameter_mismatch(
        current_template_path,
        parameters,
        child_template_url
    ):
        missing_parameters = []
        template_parser = MyTemplateParser()

        # Hack out the QS bits and get the file_name
        template_file = str(MyTemplateParser.template_url_to_path(
            current_template_path=current_template_path,
            template_url=child_template_url
        ))

        # Load child stack
        template_parsed = template_parser.my_load_yaml_function(
            template_file=template_file
        )

        # Iterate over Child Stack parameters and
        # make sure we have all the ones that are not Defaults
        # TODO: How should we deal with 'Defaults'
        child_template_parameters = template_parsed.get("Parameters")
        if child_template_parameters is None:
            child_template_parameters = {}

        for parameter in child_template_parameters:
            properties = child_template_parameters.get(parameter)
            if properties is None:
                properties = {}

            if 'Default' in properties.keys():
                continue

            if parameter not in parameters.keys():
                missing_parameters.append(parameter)

            # TODO: Add matching of types if known
            # TODO: What about TaskCat parameters
        if not len(missing_parameters) == 0:
            return str(missing_parameters)
        else:
            return None

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        # try:
        resources = cfn.get_resources(
            resource_type=['AWS::CloudFormation::Stack']
        )

        for r_name, r_values in resources.items():
            properties = r_values.get('Properties')
            child_template_url = properties.get('TemplateURL')

            child_template_parameters = properties.get('Parameters')
            if child_template_parameters is None:
                child_template_parameters = {}

            missing_parameters = self.parameter_mismatch(
                current_template_path=os.path.abspath(cfn.filename),
                parameters=child_template_parameters,
                child_template_url=child_template_url
            )

            if missing_parameters:
                path = ['Resources', r_name]
                message = 'Missing Child Stack parameters. {} {}'.format(
                        r_name,
                        missing_parameters
                    )
                matches.append(RuleMatch(path, message))
        return matches


class DefaultParameterRule(CloudFormationLintRule):
    """Check Nested Stack Parameters"""
    id = 'W9198'
    shortdesc = 'Parameters missing for nested stack'
    description = 'Check to make sure parameters for nested stack are correct'
    source_url = 'https://github.com/qs-cfn-lint-rules/qs_cfn_lint_rules'
    tags = ['case']

    @staticmethod
    def default_parameter_check(
        current_template_path,
        parameters,
        child_template_url
    ):
        missing_parameters = []
        template_parser = MyTemplateParser()

        # Hack out the QS bits and get the file_name
        template_file = str(MyTemplateParser.template_url_to_path(
            current_template_path=current_template_path,
            template_url=child_template_url
        ))

        # Load child stack
        template_parsed = template_parser.my_load_yaml_function(
            template_file=template_file
        )

        # Iterate over Child Stack parameters and
        # make sure we have all the ones that are not Defaults
        # TODO: How should we deal with 'Defaults'
        child_template_parameters = template_parsed.get("Parameters")
        if child_template_parameters is None:
            child_template_parameters = {}

        for parameter in child_template_parameters:
            properties = child_template_parameters.get(parameter)
            if ('Default' in properties.keys()) and (parameter not in parameters.keys()):
                missing_parameters.append(parameter)

            # TODO: Add matching of types if known
            # TODO: What about TaskCat parameters
        if not len(missing_parameters) == 0:
            return str(missing_parameters)
        else:
            return None

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        # try:
        resources = cfn.get_resources(
            resource_type=['AWS::CloudFormation::Stack']
        )

        for r_name, r_values in resources.items():
            properties = r_values.get('Properties')
            child_template_url = properties.get('TemplateURL')

            child_template_parameters = properties.get('Parameters')
            if child_template_parameters is None:
                child_template_parameters = {}

            default_parameters = self.default_parameter_check(
                current_template_path=os.path.abspath(cfn.filename),
                parameters=child_template_parameters,
                child_template_url=child_template_url
            )

            if default_parameters:
                path = ['Resources', r_name]
                message = 'Default parameters used,' \
                    ' please be explicit and pass the default value ' \
                    'if you wish to use that. {} {}'.format(
                        r_name,
                        default_parameters
                    )
                matches.append(RuleMatch(path, message))
        return matches


class MatchingParameterNotPassed(CloudFormationLintRule):
    """Check Nested Stack Parameters"""
    id = 'E9197'
    shortdesc = 'Parameters in master not passed to child'
    description = 'A parameter with the same name exists in master ' \
                  'and child. It is not passed to the child'
    source_url = 'https://github.com/qs-cfn-lint-rules/qs_cfn_lint_rules'
    tags = ['case']

    @staticmethod
    def matching_but_not_used_check(
        current_template_path,
        parent_parameters,
        resource_parameters,
        child_template_url
    ):
        missing_parameters = []
        template_parser = MyTemplateParser()

        # Hack out the QS bits and get the file_name
        template_file = str(MyTemplateParser.template_url_to_path(
            current_template_path=current_template_path,
            template_url=child_template_url
        ))

        # Load child stack
        template_parsed = template_parser.my_load_yaml_function(
            template_file=template_file
        )

        child_parameters = template_parsed.get("Parameters")
        if child_parameters is None:
            child_parameters = {}

        for parameter in child_parameters:
            # We have a parameter in the parent matching the child
            if parameter in parent_parameters.keys():
                if parameter in resource_parameters.keys():
                    # The Parents value not being passed to the child
                    if parameter not in str(resource_parameters.get(parameter)):
                        # TODO: test for !Ref or the name of the Parameter in the value
                        print("parameter:{} value: {} ".format(parameter, str(resource_parameters.get(parameter))))
                        missing_parameters.append("{}\ {{}\}".format(parameter, str(resource_parameters.get(parameter))))

        if not len(missing_parameters) == 0:
            return str(missing_parameters)
        else:
            return None

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        # try:
        resources = cfn.get_resources(
            resource_type=['AWS::CloudFormation::Stack']
        )

        parent_parameters = cfn.get_parameters()
        if type(parent_parameters) is None:
            parent_parameters = {}

        for r_name, r_values in resources.items():
            properties = r_values.get('Properties')
            child_template_url = properties.get('TemplateURL')

            child_template_parameters = properties.get('Parameters')
            if child_template_parameters is None:
                child_template_parameters = {}

            not_passed_to_child = self.matching_but_not_used_check(
                current_template_path=os.path.abspath(cfn.filename),
                parent_parameters=parent_parameters,
                resource_parameters=child_template_parameters,
                child_template_url=child_template_url
            )

            if not_passed_to_child:
                path = ['Resources', r_name]
                message = 'Parameter defined in Parent with same name as child,' \
                    ' however this value is never passed to child. {} {}'.format(
                        r_name,
                        not_passed_to_child
                    )
                matches.append(RuleMatch(path, message))
        return matches


class ParameterPassedButNotDefinedInChild(CloudFormationLintRule):
    """Check Nested Stack Parameters"""
    id = 'E9196'
    shortdesc = 'Parameters in passed to stack resource but not defined in child'
    description = 'A parameter defined in template stack resource but not ' \
                  'defined in the child template'
    source_url = 'https://github.com/qs-cfn-lint-rules/qs_cfn_lint_rules'
    tags = ['case']

    @staticmethod
    def missing_in_child_check(
        current_template_path,
        resource_parameters,
        child_template_url
    ):
        missing_parameters = []
        template_parser = MyTemplateParser()

        # Hack out the QS bits and get the file_name
        template_file = str(MyTemplateParser.template_url_to_path(
            current_template_path=current_template_path,
            template_url=child_template_url
        ))

        # Load child stack
        template_parsed = template_parser.my_load_yaml_function(
            template_file=template_file
        )

        # Iterate over template resource parameters and check they exist
        # In the child template
        child_parameters = template_parsed.get("Parameters")
        if child_parameters is None:
            child_parameters = {}

        for parameter in resource_parameters.keys():

            # We have a parameter in the parent matching the child
            if parameter not in child_parameters.keys():
                missing_parameters.append(parameter)

        if not len(missing_parameters) == 0:
            return str(missing_parameters)
        else:
            return None

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        # try:
        resources = cfn.get_resources(
            resource_type=['AWS::CloudFormation::Stack']
        )

        for r_name, r_values in resources.items():
            properties = r_values.get('Properties')
            child_template_url = properties.get('TemplateURL')

            child_template_parameters = properties.get('Parameters')
            if child_template_parameters is None:
                child_template_parameters = {}

            not_passed_to_child = self.missing_in_child_check(
                current_template_path=os.path.abspath(cfn.filename),
                resource_parameters=child_template_parameters,
                child_template_url=child_template_url
            )

            if not_passed_to_child:
                path = ['Resources', r_name]
                message = 'Parameter defined in Stack resource not present in' \
                    ' child template {} {}'.format(
                        r_name,
                        not_passed_to_child
                    )
                matches.append(RuleMatch(path, message))
        return matches
