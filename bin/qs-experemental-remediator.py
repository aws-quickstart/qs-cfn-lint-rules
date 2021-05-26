#!/usr/bin/env/python
import cfnlint
import cfnlint.core
import cfnlint.decode
import cfnlint.template
from cfn_flip import flip, to_yaml, to_json, load
import json
import argparse
import re

changes = {}

def get_rules():
    config = cfnlint.config.ConfigMixIn({})
    rules = cfnlint.core.get_rules(
        config.append_rules,
        config.ignore_checks,
        config.include_checks,
        config.configure_rules,
        config.mandatory_checks,
    )
    return rules

def generate_template(fn):
    indentation_map = {}
    linenumber_map = {1:{'start':0}}
    with open(fn) as f:
        buffer = f.read()
    for idx, line in enumerate(buffer.splitlines()):
        indentation = re.search('\S', line)
        if not indentation:
            continue
        indentation_map[idx+1] = indentation.start()
    i=1
    for match in re.finditer('\n', buffer):
        loc = match.span()
        linenumber_map[i+1] = {'start':loc[1]}
        linenumber_map[i]['end'] = loc[0]
        i=i+1

    tt = cfnlint.decode.decode(fn)
    T = cfnlint.template.Template(fn, tt[0])
    _, format = load(buffer)
    return format, T, buffer, indentation_map, linenumber_map

def new_sauce(path, format, new, indentation, line_number):
    if (isinstance(path[-1], int) and isinstance(new, list)):
        indent = indentation.get(line_number+1)
        if indent:
            xx = json.dumps(new)
            if format == 'yaml':
                nv = to_yaml(xx, clean_up=True)[2:-1]
            if format == 'json':
                nv = to_json(xx, clean_up=True)[1:-1]
            xx1 = nv.splitlines()
            if xx1[0] == '':
                del xx1[0]
            spaced_data = [xx1[0]]+["{0}{1}".format(" "*(indent), i) for i in xx1[1:]]
            spaced_txt = "\n".join(spaced_data)
            return spaced_txt
    new = json.dumps(new)
    if format == 'yaml':
        nv = to_yaml(new, clean_up=True)
    if format == 'json':
        nv = to_json(new, clean_up=True)
        nv = re.sub('\n', '', nv)
        nv = re.sub(' +', ' ', nv)
    if nv.endswith('\n'):
        if nv[-5:] == '\n...\n':
            return nv[:-5]
        return nv[:-1]
    return nv

def fix_stuff(fn, on):
    format, T, tb, indentation, lnm = generate_template(fn)
    rules = get_rules()
    for rule in rules:
        if hasattr(rule, 'determine_changes'):
            x = rule.determine_changes(T)
            for start_mark, data in x.items():
                CONFLICT=False
                for sm in changes.keys():
                    if start_mark < sm < data[0]:
                        CONFLICT=True
                        continue
                if not CONFLICT:
                    changes[start_mark] = data

    for k in sorted(changes, reverse=True):
        end_index, path, nv, ln = changes[k]
        final_value = new_sauce(path, format, nv, indentation, ln)
        tb = tb[0:k] + final_value + tb[end_index:]

    with open(on, 'w') as f:
        f.write(tb)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--template')
    args = parser.parse_args()
    if (not args.template):
        raise Exception("Need: -t/--template")
    fix_stuff(args.template, f"{args.template}.output")
