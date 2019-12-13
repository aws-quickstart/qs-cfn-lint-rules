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
from qs_cfn_lint_rules.stack.StackHelper import template_url_to_path


class TestStackHelper(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Test the URL parsing template_url_to_path logic
    # Parent and child in the same folder
    def test_same_path(self):
        master_template_path = "../../../fixtures/templates/good/resources/stack/master.yml"
        path_result = template_url_to_path(
            master_template_path,
            " !Sub ['https://${QSS3BucketName}.${QSS3Region}.amazonaws.com/${QSS3KeyPrefix}/templates/child.yml',"
            "{QSS3Region: !If [GovCloudCondition, s3-us-gov-west-1, s3]}]"
        )
        path_expected = "../../fixtures/templates/good/resources/stack/child.yml"

        self.assertEquals(path_result, path_expected)

    def test_nested_path(self):
        self.assertEqual('true', 'false')

    def test_sub(self):
        self.assertEqual('true', 'false')
