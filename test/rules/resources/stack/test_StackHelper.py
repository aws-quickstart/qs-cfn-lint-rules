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
