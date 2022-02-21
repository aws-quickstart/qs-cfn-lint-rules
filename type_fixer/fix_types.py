import cfnlint.core
from taskcat._cfn.template import Template
import argparse
import re


def cfnlint_deep_get(template_obj, matchobj_path):
    x = template_obj[matchobj_path[0]]
    for k in matchobj_path[1:]:
        if isinstance(k, str):
            x = x.get(k, None)
        if isinstance(k, int):
            x = x[k]
    return x


def write_template_modifications(modified_lines, tc_template):
    line_array = tc_template.linesplit
    for line_stanza in modified_lines:
        line_number = line_stanza[0]
        template_line = line_array[line_number]
        new_line = re.sub(template_line, line_stanza[1], template_line)
        line_array[line_number] = new_line
    tc_template.raw_template = "\n".join(line_array)
    tc_template.write()


def _str_to_bool(line, *args, **kwargs):
    if re.search('"true"|"false"', line):
        line = re.sub('"true"', "true", line)
        line = re.sub('"false"', "false", line)
        return line
    if re.search("'true'|'false'", line):
        line = re.sub("'true'", "true", line)
        line = re.sub("'false'", "false", line)
        return line


def _bool_to_str(line, *args, **kwargs):
    if re.search("true", line):
        line = re.sub("true", '"true"', line)
        return line
    if re.search("false", line):
        line = re.sub("false", '"false"', line)
        return line


def _str_to_int(line, matchobj, tc_template):
    str_value = cfnlint_deep_get(tc_template.template, matchobj.path)
    if re.search(f"{int(str_value)}", line):
        line = re.sub(f'"{int(str_value)}"', f"{int(str_value)}", line)
        return line
    if re.search(f"{int(str_value)}", line):
        line = re.sub(f"'{int(str_value)}'", "{int(str_value)}", line)
        return line


type_to_func = {
    ("str_node", "bool"): _str_to_bool,
    ("str_node", "int"): _str_to_int,
    ("bool", "str_node"): _bool_to_str,
}


def fix_E3012(tc_template, match):
    result = ()
    try:
        new_line = type_to_func[(match.actual_type, match.expected_type)](
            tc_template.linesplit[match.linenumber - 1], match, tc_template
        )
        result = (match.linenumber - 1, new_line)
    except KeyError:
        print(
            f"Missing function for {match.actual_type} -> {match.expected_type}. Please edit line {match.linenumber} manually!"
        )
    return result


rule_id_to_func = {"E3012": fix_E3012}


def find_rule_matches(tc_template):
    cfnlint.core.configure_logging(None)
    rules = cfnlint.core.get_rules([], [], [], [], False, [])
    regions = ["us-east-1"]
    matches = cfnlint.core.run_checks(
        tc_template.template_path, tc_template.template, rules, regions
    )
    return matches


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Fix type-errors from cfnlint"
    )
    parser.add_argument("--file", type=str)
    args = parser.parse_args()
    tc_template = Template(template_path=args.file)
    x = find_rule_matches(tc_template)
    modified_lines = set()
    for match in x:
        try:
            result = rule_id_to_func[match.rule.id](tc_template, match)
            if result:
                modified_lines.add(result)
        except KeyError:
            continue

    write_template_modifications(modified_lines, tc_template)
