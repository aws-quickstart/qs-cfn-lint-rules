import pkg_resources
import sys

EXIT_CODES = {
    4:0,
    8:0,
    12:0
}


def main():
    entrypoint_func = pkg_resources.get_entry_map('cfn-lint', 'console_scripts')['cfn-lint'].load()
    ec = entrypoint_func()
    sys.exit(EXIT_CODES.get(ec, ec))
