import cfnlint.core
from qs_cfn_lint_rules import IAMPartition

fn = "test/fixtures/templates/E9007/E9007.1.template.yaml"


def return_rule_line_matches(filename):
    t = cfnlint.decode.decode(fn, False)
    cfn = cfnlint.Template(fn, t[0])
    (_, rules, __) = cfnlint.core.get_template_rules(fn, cfnlint.config.ConfigMixIn([]))
    rule_matches = cfnlint.core.run_checks(fn, cfn.template, rules, ["us-east-1"])
    matches_dict = {}
    for match in rule_matches:
        try:
            matches_dict[match.rule.id].append(match.linenumber)
        except KeyError:
            matches_dict[match.rule.id] = [match.linenumber]
    return matches_dict


# x = IAMPartition.IAMPartition()
# x.match(cfn)
