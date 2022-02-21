#!/usr/bin/env/python
import cfnlint
import cfnlint.core
import cfnlint.decode
import cfnlint.template
from cfn_flip import flip, to_yaml, to_json, load
import json
import argparse
import re
import sys


def deep_get(source_dict, list_of_keys, default_value=None):
    x = source_dict
    for k in list_of_keys:
        if isinstance(k, int):
            x = x[k]
        else:
            x = x.get(k, {})
    if not x:
        return default_value
    return x


class Remediator:
    def __init__(self, input_fn, output_fn):
        self.filename = input_fn
        self.output = output_fn
        self._delete_paths = []
        self._changes = {}
        self._indentation_map = {}
        self._per_rule_logic = {"E3012": self._E3012_logic}
        self._rules = []
        self._linenumber_map = {1: {"start": 0}}
        self._conflicting_rules = False
        with open(input_fn) as f:
            self.buffer = f.read()
        self._format = load(self.buffer)[1]
        self._reload_buffer_to_template()

    def _generate_linenumber_and_indentation_map(self):
        for idx, line in enumerate(self.buffer.splitlines()):
            indentation = re.search("\S", line)
            if not indentation:
                continue
            self._indentation_map[idx + 1] = indentation.start()
        i = 1
        for match in re.finditer("\n", self.buffer):
            loc = match.span()
            self._linenumber_map[i + 1] = {
                "start": loc[1],
                "end": len(self.buffer) - 1,
            }
            self._linenumber_map[i]["end"] = loc[0]
            i = i + 1

    def _reload_buffer_to_template(self):
        self._changes = {}
        _x = cfnlint.decode.cfn_yaml.loads(self.buffer)
        self.cfn = cfnlint.template.Template(self.filename, _x)
        self._generate_linenumber_and_indentation_map()

    @property
    def rules(self):
        if self._rules:
            return self._rules

        config = cfnlint.config.ConfigMixIn({})
        rules = cfnlint.core.get_rules(
            config.append_rules,
            config.ignore_checks,
            config.include_checks,
            config.configure_rules,
            config.mandatory_checks,
        )
        self._rules = rules
        return rules

    @property
    def changes(self):
        return self._changes

    @property
    def indentation(self):
        return self._indentation_map

    @property
    def format(self):
        return self._format

    @property
    def delete_paths(self):
        return self._delete_paths

    def delete_lines(self):
        self._reload_buffer_to_template()
        new_buffer = []
        x = {}
        for idx, line in enumerate(self.buffer.splitlines()):
            x[idx] = line
        for path in self._delete_paths:
            g = deep_get(self.cfn.template, path)
            for ln in range(g.start_mark.line - 1, g.end_mark.line - 1):
                x[ln] = None
        for k, v in x.items():
            if v == None:
                continue
            new_buffer.append(v)
        self.buffer = "\n".join(new_buffer)

    def _save_modbuffer_to_changes(self, changes):
        for data in changes:
            if isinstance(data, cfnlint.rules.RuleMatch):
                if hasattr(data, "delete_lines"):
                    if data.delete_lines:
                        self._delete_paths.append(data.path)
                        continue
            CONFLICT = False
            for sm in self._changes.keys():
                if data[1].start_mark.index < sm[0] < data[1].end_mark.index:
                    CONFLICT = True
                    self._conflicting_rules = True
                    continue
            if not CONFLICT:
                NL = False
                opts = {}
                try:
                    opts = data[3]
                except IndexError:
                    pass
                try:
                    NL = opts["line"] + 1
                except KeyError:
                    pass
                changed_value = self._new_sauce(
                    data[0], data[2], data[1].start_mark.line, opts
                )
                _k = (data[1].start_mark.index, data[1].end_mark.index)
                if NL:
                    _k = (
                        self._linenumber_map[NL]["end"] + 1,
                        self._linenumber_map[NL]["end"] + 1,
                    )
                    changed_value += "\n"
                if opts.get("append_after"):
                    _cl = data[1].end_mark.line
                    _k = (
                        self._linenumber_map[_cl]["end"] + 1,
                        self._linenumber_map[_cl]["end"] + 1,
                    )
                    changed_value += "\n"
                if changed_value[0] == self.buffer[_k[0] - 2]:
                    _k = (_k[0] - 2, _k[1])
                if _k[0] == _k[1]:
                    if self.buffer[_k[0] - 1] != "\n":
                        changed_value = "\n" + changed_value
                self._changes[_k] = changed_value

    def _determine_changes(self):
        for rule in self.rules:
            if hasattr(rule, "determine_changes"):
                x = rule.determine_changes(self.cfn)
                # raise
                if x and type(x[0]) == cfnlint.rules.Match:
                    try:
                        func = self._per_rule_logic[rule.id]
                        x = func(x)
                    except KeyError:
                        continue
                self._save_modbuffer_to_changes(x)

    def write_changes_to_json(self):
        def _dl(start):
            for ln, d in self._linenumber_map.items():
                if d["start"] < start < d["end"]:
                    return (ln, d["start"], d["end"])

        js_safe = {}
        self._determine_changes()

        for k, v in self._changes.items():
            ln, line_start, line_end = _dl(k[0])
            js_safe[ln] = (
                self.buffer[line_start : k[0]]
                + v
                + self.buffer[k[1] : line_end]
            )

        with open(self.output, "w") as f:
            f.write(json.dumps(js_safe))

    def _changes_to_buffer(self):
        for k in sorted(self._changes, reverse=True):
            start, end = k
            self.buffer = (
                self.buffer[0:start] + self._changes[k] + self.buffer[end:]
            )

    def write(self):
        with open(self.output, "w") as f:
            f.write(self.buffer)

    def fix_stuff(self):
        _nb = False
        self._determine_changes()
        while self._conflicting_rules:
            self._conflicting_rules = False
            self._reload_buffer_to_template()
            self._determine_changes()
            self._changes_to_buffer()
            _nb = True
        if not _nb:
            self._changes_to_buffer()
        self.write()

    def _indent_list_elements(self, list_data, indent, to_nl_str=False):
        l = ["{0}{1}".format(" " * (indent), i) for i in list_data]
        if to_nl_str:
            return "\n".join(l)
        return l

    def _new_sauce(self, path, new, line_number, opts):
        indent = self.indentation.get(line_number + 1)
        # raise
        if isinstance(path[-1], int) and isinstance(new, list):
            if indent:
                xx = json.dumps(new)
                if self.format == "yaml":
                    nv = self._to_yaml_list(xx)
                if self.format == "json":
                    nv = self._to_json_list(xx)
                xx1 = nv.splitlines()
                if xx1[0] == "":
                    del xx1[0]
                if opts.get("append_after"):
                    # raise
                    spaced_data = self._indent_list_elements(xx1, indent)
                else:
                    spaced_data = [xx1[0]] + self._indent_list_elements(
                        xx1[1:], indent
                    )
                spaced_txt = "\n".join(spaced_data)
                # raise
                return spaced_txt

        new1 = json.dumps(new)
        if self.format == "yaml":
            nv = to_yaml(new1, clean_up=True)
        if self.format == "json":
            nv = self._to_json_clean(new1)

        if opts.get("newline"):
            if isinstance(new, list):
                ni = indent + 2
            nv = "\n" + self._indent_list_elements(
                nv.splitlines(), ni if ni else indent, True
            )
        if opts.get("append_after"):
            nv = "{0}{1}".format(" " * (indent), nv)

        if nv.endswith("\n"):
            if nv[-5:] == "\n...\n":
                return nv[:-5]
            return nv[:-1]
        return nv

    def _to_yaml_list(self, json_serialized):
        nv = to_yaml(json_serialized, clean_up=True)[:-1]
        return nv

    def _to_json_list(self, json_serialized):
        nv = to_json(json_serialized, clean_up=True)[:-1]
        return nv

    def _to_json_clean(self, new):
        nv = to_json(new, clean_up=True)
        nv = re.sub("\n", "", nv)
        nv = re.sub(" +", " ", nv)
        return nv

    def _str_to_bool(self, line):
        if "false" in line:
            return False
        if "true" in line:
            return True

    def _bool_to_str(self, line):
        if re.search("true", line):
            return str(True)
        if re.search("false", line):
            return str(False)

    def _str_to_int(self, line):
        if re.search('"', line):
            line = re.sub('"', "", line)
            return int(line)
        if re.search("'", line):
            line = re.sub(f"'", "", line)
            return int(line)

    def _E3012_logic(self, rules):
        changes = []
        _type_to_func = {
            ("str_node", "bool"): self._str_to_bool,
            ("str_node", "int"): self._str_to_int,
            ("bool", "str_node"): self._bool_to_str,
        }

        for rule in rules:
            try:
                func = _type_to_func[(rule.actual_type, rule.expected_type)]
            except TypeError:
                if isinstance(rule.expected_type, list):
                    for o in rule.expected_type:
                        try:
                            func = _type_to_func[(rule.actual_type, o)]
                            break
                        except KeyError:
                            continue
                    if not func:
                        continue
            except KeyError:
                continue

            obj = deep_get(self.cfn.template, rule.path)
            ov = self.buffer[obj.start_mark.index : obj.end_mark.index]
            nv = func(ov)
            changes.append((rule.path, obj, nv))

        return changes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--template")
    parser.add_argument("-j", "--json-output", action="store_true")
    parser.add_argument("-d", "--delete", action="store_true")
    args = parser.parse_args()
    if not args.template:
        raise Exception("Need: -t/--template")
    remediator = Remediator(args.template, f"{args.template}.output")
    if args.json_output:
        remediator.write_changes_to_json()
        sys.exit(0)
    remediator.fix_stuff()
    if args.delete:
        remediator.delete_lines()
        remediator.write()
