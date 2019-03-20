# AWS Quick Start cfn-lint rules

This repo provides CloudFormation linting rules specific to [AWS Quick Start](https://aws.amazon.com/quickstart/) 
guidelines, for more information see the [Contributors Guide](https://aws-quickstart.github.io).

## Installation and Usage

```bash
cd ~/
git clone https://github.com/aws-quickstart/qs-cfn-lint-rules.git
pip install -e .
```

To add the rules when running on the command line use the `-a` flag to add the additional rules:

```bash
cfn-lint -a ~/qs-cfn-lint-rules/qs-cfn-lint-rules/ my-cfn-template.yaml
```

To use in your IDE install the relevant 
[cfn-lint plugin](https://github.com/aws-cloudformation/cfn-python-lint#editor-plugins) and add the rules to your 
cfn-lint config file (`~/.cfnlintrc`) as follows:

```yaml
append_rules:
- ~/qs-cfn-lint-rules/qs-cfn-lint-rules/
```
