import re
from cfnlint.decode import decode
import argparse
import sys
from pathlib import Path

TYPE_REGEX = r"([A-Za-z0-9]+::){2}([A-Za-z0-9]+)"


def is_cfn(inputs):
    if not inputs:
        return False

    if not issubclass(type(inputs), dict):
        return False

    if "AWSTemplateFormatVersion" in inputs.keys():
        return True

    if not "Resources" in inputs.keys():
        return False

    for k, v in input["Resources"].items():
        if not v.get("Type"):
            return False
        if re.match(v["Type"], TYPE_REGEX):
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inverse-exit-code", action="store_true")
    parser.add_argument("filenames", nargs="+")
    args = parser.parse_args()
    cfn = []
    not_cfn = []
    for file in args.filenames:
        x = decode(Path(file).expanduser().resolve())
        if is_cfn(x[0]):
            cfn.append(file)
        else:
            not_cfn.append(file)

    if args.inverse_exit_code:
        return int(len(cfn) > 0)
    else:
        return int(not len(cfn) > 0)
