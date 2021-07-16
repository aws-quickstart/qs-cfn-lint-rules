from qs_cfn_lint_rules.ProhibitedResources import *
from ... import BaseRuleTestCase, DynamicRuleTesting


class DynamicProhibitedResourceProperties(DynamicRuleTesting, BaseRuleTestCase):
    imported_module = 'qs_cfn_lint_rules.ProhibitedResources'
    module_attr = 'resource_type'

    def test_file_negative(self):
        for cn, to in self.testobjs.items():
            with self.subTest(f"Testing {cn} file negative", file=f"{to.parent.id}.json", rule=to.parent.id):
                to.test_file_negative(1)