from qs_cfn_lint_rules.NoDefaultAndEcho import *
from ... import BaseRuleTestCase, DynamicRuleTesting


class DynamicNoDefaultAndEcho(DynamicRuleTesting, BaseRuleTestCase):
    imported_module = 'qs_cfn_lint_rules.NoDefaultAndEcho'
    module_attr = 'property_names'

    def test_file_negative(self):
        for cn, to in self.testobjs.items():
            with self.subTest(f"Testing {cn} file negative", file=f"{to.parent.id}.json", rule=to.parent.id):
                to.test_file_negative(len(to.parent.property_names))