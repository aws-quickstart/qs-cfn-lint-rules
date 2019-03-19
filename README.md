# AWS Quick Start cfn-lint rules

This repo provides CloudFormation linting rules specific to the AWS Quick Start programs guidelines, for more 
information see the [Contributors Guide](https://aws-quickstart.github.io).

## Installation and Usage

```bash
# Requires cfn-python-lint
pip install cfn-python-lint
cd ~/
git clone https://github.com/aws-quickstart/qs-cfn-lint-rules.git
```

To add the rules when running on the command line use the `-a` flag to add the additional rules:

```bash
cfn-lint -a ~/qs-cfn-lint-rules/quickstart/ my-cfn-template.yaml
```

To use in your IDE install the relevant [cfn-lint plugin](qs-cfn-lint-rules) and add the rules to your cfn-lint config 
file (`~/.cfnlintrc`) as follows:

```yaml
append_rules:
- ~/qs-cfn-lint-rules/quickstart/
```