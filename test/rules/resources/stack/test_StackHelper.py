import unittest
import cfnlint
import json
from qs_cfn_lint_rules.stack import StackHelper


class TestStackHelper(unittest.TestCase):

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
        with open("test/fixtures/templates/stackhelper/test.json") as test_file:
            self.tests = json.load(test_file)
            self.tests = self.tests['tests']

        total = len(self.tests)
        matched = 0

        for test in self.tests:
            cfn = self._load_template(test["input"]["master_template"])
            StackHelper.mappings = cfn.get("Mappings")
            if test["output"]["url_paths"] == StackHelper.flatten_template_url(test["input"]["child_template"]):
                matched = matched + 1
        # print("matched {} total {}".format(matched, total))
        self.assertEqual(matched, total)

    def test_flatten_template_url_exceptions_split(self):
        with self.assertRaises(Exception) as context:
            StackHelper.flatten_template_url("{'Fn::Split'}")

        self.assertTrue('Fn::Split: not supported' in str(context.exception))

    def test_flatten_template_url_exceptions_getatt(self):
        with self.assertRaises(Exception) as context:
            StackHelper.flatten_template_url("{'Fn::GetAtt'}")

        self.assertTrue('Fn::GetAtt: not supported' in str(context.exception))

    def test_flatten_template_url_maxdepth(self):
        with self.assertRaises(Exception) as context:
            StackHelper.flatten_template_url("{ one { two } { two { three { four { five { six { seven { eight { nine {ten {11 {12 {13 {14 {15 {16 {17 {18 {19 {20 {21}}}}}}}}}}}}} }}}}} }}")

        self.assertTrue('Template URL contains more than' in str(context.exception))

    def test_find_local_child_template(self):
        self.assertEqual(True, False)

    # Test TemplateURL to path extraction
    def test_find_local_child_template(self):
        with open("test/fixtures/templates/stackhelper/test.json") as test_file:
            self.tests = json.load(test_file)
            self.tests = self.tests['tests']

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

        # print("matched {} total {}".format(matched, total))
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
        self.assertEqual(True, False)

    # Test local path Discovery
    def test_fn_if(self):
        self.assertEqual(True, False)
