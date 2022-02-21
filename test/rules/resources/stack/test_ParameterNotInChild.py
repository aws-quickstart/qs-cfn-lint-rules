from qs_cfn_lint_rules.stack.ParameterNotInChild import (
    ParameterNotInChild,
)  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestParameterNotInChild(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestParameterNotInChild, self).setUp()
        self.collection.register(ParameterNotInChild())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()  # By default, a set of "correct" templates are checked

    def test_file_negative(self):
        """Test failure"""
        prefix = "test/fixtures/templates/bad/resources/stack/"
        self.helper_file_negative(
            "{}{}.yml".format(prefix, "ParameterNotInChild"), 1
        )  # Amount of expected matches
