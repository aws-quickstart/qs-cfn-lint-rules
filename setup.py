"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from setuptools import find_packages
from setuptools import setup


version = "0.0.2"


with open("README.md") as f:
    readme = f.read()

setup(
    name="qs_cfn_lint_rules",
    version=version,
    description="checks CloudFormation templates against AWS Quick Start contributors guide rules",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="aws, lint, aws-qs_cfn_lint_rules",
    author="AWS Quick Start team",
    author_email="qs_cfn_lint_rules-eng@amazon.com",
    url="https://github.com/aws-quickstart/qs-cfn-lint-rules",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "cfn-lint>=0.16.0,<1.0.0",
        "pyspellchecker>=0.4.0,<0.5.0",
        "policyuniverse>=1.3.5,<2",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    license="Apache License 2.0",
    test_suite="unittest",
    scripts=["bin/qs-experemental-remediator.py"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
