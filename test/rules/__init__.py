"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import inspect
import sys
import cfnlint.config
from cfnlint import Runner
from cfnlint.rules import RulesCollection
from testlib.testcase import BaseTestCase


class BaseRuleTestCase(BaseTestCase):
    """Used for Testing Rules"""

    success_templates = []

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection(
            include_rules=["I"], include_experimental=True
        )

    def helper_file_positive(self):
        """Success test"""
        for filename in self.success_templates:
            template = self.load_template(filename)
            good_runner = Runner(
                self.collection, filename, template, ["us-east-1"], []
            )
            good_runner.transform()
            failures = good_runner.run()
            assert [] == failures, "Got failures {} on {}".format(
                failures, filename
            )

    def helper_file_rule_config(self, filename, config, err_count):
        """Success test with rule config included"""
        template = self.load_template(filename)
        self.collection.rules[0].configure(config)
        good_runner = Runner(
            self.collection, filename, template, ["us-east-1"], []
        )
        good_runner.transform()
        failures = good_runner.run()
        self.assertEqual(
            err_count,
            len(failures),
            "Expected {} failures but got {} on {}".format(
                err_count, failures, filename
            ),
        )
        self.collection.rules[0].configure(config)

    def helper_file_positive_template(self, filename):
        """Success test with template parameter"""
        template = self.load_template(filename)
        good_runner = Runner(
            self.collection, filename, template, ["us-east-1"], []
        )
        good_runner.transform()
        self.assertEqual([], good_runner.run())

    def helper_file_negative(self, filename, err_count, regions=None):
        """Failure test"""
        regions = regions or ["us-east-1"]
        template = self.load_template(filename)
        bad_runner = Runner(self.collection, filename, template, regions, [])
        bad_runner.transform()
        errs = bad_runner.run()
        self.assertEqual(err_count, len(errs))


class DynamicRuleTesting:
    def test_file_positive(self):
        for cn, to in self.testobjs.items():
            with self.subTest(
                f"Testing {cn} file positive", file=cn, rule=to.parent.id
            ):
                to.test_file_positive()

    def test_file_negative(self):
        for cn, to in self.testobjs.items():
            with self.subTest(
                f"Testing {cn} file negative", file=cn, rule=to.parent.id
            ):
                to.test_file_negative(len(to.parent.property_names))

    def setUp(self):
        self.subobjs = {}
        self.testobjs = {}
        for name, obj in inspect.getmembers(sys.modules[self.imported_module]):
            if inspect.isclass(obj):
                if hasattr(obj, self.module_attr):
                    self.subobjs[name] = obj
        for n, o in self.subobjs.items():
            _single_rule_test = SingleRuleTest()
            _single_rule_test.configure(o)
            self.testobjs[n] = _single_rule_test


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
            (parent_cls, BaseRuleTestCase, object),
            {"__init__": dynamic_init, "is_enabled": is_enabled},
        )
        dc = dynamic_class()
        dc.setUp()
        dc.collection.register(dc)
        self._parent_instance = dc

    def test_file_positive(self):
        """Test Positive"""
        self._parent_instance.helper_file_positive()  # By default, a set of "correct" templates are checked

    def test_file_negative(self, expected_errors):
        """Test failure"""
        prefix = "test/fixtures/templates/bad/resources/cfnnag/"
        self._parent_instance.helper_file_negative(
            f"{prefix}{self._parent_instance.id}.json", expected_errors
        )

    @property
    def parent(self):
        return self._parent_instance
