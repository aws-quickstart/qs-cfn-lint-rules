# from stack.StackHelper import template_url_to_path  # pylint: disable=E0401
# from ... import BaseRuleTestCase


# class TestMissingParameter(BaseRuleTestCase):
#     """Test template parameter configurations"""
#     def setUp(self):
#         """Setup"""
#         super(TestMissingParameter, self).setUp()
#         self.collection.register(MissingParameter())
#
#     def test_file_positive(self):
#         """Test Positive"""
#         self.helper_file_positive()  # By default, a set of "correct" templates are checked
#
#     def test_file_negative(self):
#         """Test failure"""
#         self.helper_file_negative('test/fixtures/templates/bad/mynewrule.yaml', 1)  # Amount of expected matches
import unittest
import cfnlint
from qs_cfn_lint_rules.stack import StackHelper


class TestStackHelper(unittest.TestCase):
    tests = [
        {
            "input": {
                "master_template": "/mnt/c/Users/gargana/workspace/scratch/qs-code/quickstart-amazon-redshift/templates/redshift-master.template.yaml",

                "child_template": "{'Fn::Sub': ['https://${QSS3BucketName}.${QSS3Region}.amazonaws.com/${QSS3KeyPrefix}submodules/quickstart-aws-vpc/templates/aws-vpc.template', {'QSS3Region': {'Fn::If': ['GovCloudCondition', 's3-us-gov-west-1', 's3']}}]}"
            },
            "output": {
                "url_paths": ['/QSS3KeyPrefix/submodules/quickstart-aws-vpc/templates/aws-vpc.template'],
                "local_paths": ['/mnt/c/Users/gargana/workspace/scratch/qs-code/quickstart-amazon-redshift/submodules/quickstart-aws-vpc/templates/aws-vpc.template']
            }
        }
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def _load_template(template_path):
        try:
            cfn = cfnlint.decode.cfn_yaml.load(template_path)
        except Exception as e:
            print("Exception parsing: '{}'".format(template_path))
            # print(str(e))
            exit(1)
        return cfn

    # Test TemplateURL to path extraction
    def test_flatten_template_url(self):
        total = len(self.tests)
        matched = 0

        for test in self.tests:
            cfn = self._load_template(test["input"]["master_template"])
            StackHelper.mappings = cfn.get("Mappings")
            if test["output"]["url_paths"] == StackHelper.flatten_template_url(test["input"]["child_template"]):
                matched = matched + 1

        self.assertEqual(matched, total)

    # Test TemplateURL to path extraction
    def test_find_local_child_template(self):
        total = 0
        matched = 0
        for test in self.tests:
            index = 0
            for url_path in test["output"]["url_paths"]:
                total = total + 1
                master_template = test["input"]["master_template"]
                result = StackHelper.find_local_child_template(master_template, url_path)
                expected = test["output"]["local_paths"][index]
                if str(result) == str(expected):
                    matched = matched + 1
                index = index + 1

        self.assertEqual(matched, total)

    # Test all the individual functions
    def test_fn_if(self):
        self.assertEqual('true', 'false')

    def test_fn_findinmap_lookup(self):
        l_mappings = {
            "ami_lookup": {
                "us-east-1": {
                    "ami": "this_one",
                    "ami2": "that_one"
                },
                "us-east-2": {
                    "ami": "is_this_one",
                    "ami2": "is_that_one"
                },
                "us-west-1": {
                    "ami": "not_this_one",
                    "ami2": "not_that_one"
                }
            }
        }

        StackHelper.mappings = l_mappings

        mappings_map = "ami_lookup"
        first_key = "us-west-1"
        final_key = "ami2"

        result = StackHelper.find_in_map_lookup(mappings_map, first_key, final_key)

        self.assertEqual(result, 'not_that_one')

    def test_fn_sub(self):
        self.assertEqual('true', 'false')

    # Test local path Discovery
    def test_fn_if(self):
        self.assertEqual('true', 'false')