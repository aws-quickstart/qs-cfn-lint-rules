from qs_cfn_lint_rules.RequiredResourceProperties import *
from ... import BaseRuleTestCase, DynamicRuleTesting


class DynamicRequiredResourceProperties(DynamicRuleTesting, BaseRuleTestCase):
    imported_module = 'qs_cfn_lint_rules.RequiredResourceProperties'
    module_attr = 'property_name'

    def test_file_negative(self):
        for cn, to in self.testobjs.items():
            with self.subTest(f"Testing {cn} file negative", file=f"{to.parent.id}.json", rule=to.parent.id):
                to.test_file_negative(2)