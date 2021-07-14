import inspect
import unittest
import sys
from qs_cfn_lint_rules.NoDefaultAndEcho import *
from ... import BaseRuleTestCase



class SingleRuleTest:

    def configure(self, parent_cls):
        # Dynamically creating these to ensure MRO inheritence is how we want it.
        def dynamic_init(self):
            super(BaseRuleTestCase, self).__init__()
            super(parent_cls, self).__init__()
        def is_enabled(self, *args, **kwargs):
            return True
        dynamic_class = type(
            f"Dynamic_{parent_cls.__name__}",
            (parent_cls, BaseRuleTestCase, object),{
                '__init__': dynamic_init,
                'is_enabled': is_enabled
            })
        dc = dynamic_class()
        dc.setUp()
        dc.collection.register(dc)
        self._parent_instance = dc

    def test_file_positive(self):
        """Test Positive"""
        self._parent_instance.helper_file_positive()  # By default, a set of "correct" templates are checked

    def test_file_negative(self, expected_errors):
        """Test failure"""
        prefix = 'fixtures/templates/bad/resources/cfnnag/'
        self._parent_instance.helper_file_negative(f"{prefix}{self._parent_instance.id}.json", expected_errors)

    @property
    def parent(self):
        return self._parent_instance


class DynamicRuleTesting(BaseRuleTestCase):
    subobjs = {}
    testobjs = {}

    def test_file_positive(self):
        for cn, to in self.testobjs.items():
            with self.subTest(f"Testing {cn} file positive"):
                to.test_file_positive()

    def test_file_negative(self):
        for cn, to in self.testobjs.items():
            with self.subTest(f"Testing {cn} file negative"):
                to.test_file_negative(len(to.parent.property_names))

    def setUp(self):
        for name, obj in inspect.getmembers(sys.modules['qs_cfn_lint_rules.NoDefaultAndEcho']):
            if inspect.isclass(obj):
                if hasattr(obj, 'property_names'):
                    self.subobjs[name] = obj
        for n, o in self.subobjs.items():
            _single_rule_test = SingleRuleTest()
            _single_rule_test.configure(o)
            self.testobjs[n] = _single_rule_test