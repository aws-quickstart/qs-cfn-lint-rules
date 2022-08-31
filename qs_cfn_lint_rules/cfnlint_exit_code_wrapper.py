import pkg_resources
import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
EXIT_CODES = {
    4:0,
    8:0,
    12:0
}


def main():
    entrypoint_func = pkg_resources.get_entry_map('cfn-lint', 'console_scripts')['cfn-lint'].load()
    custom_rule_location = pkg_resources.resource_filename('qs_cfn_lint_rules', "")
    sys.argv[1:] = [f"-a={custom_rule_location}"] + sys.argv[1:]
    ec = entrypoint_func()
    logger.info(f"Returned exit code: {ec}; Translated to: {EXIT_CODES.get(ec, ec)}")
    sys.exit(EXIT_CODES.get(ec, ec))
