"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import os
from pathlib import Path


def template_url_to_path(current_template_path, template_url):

    template_path = ""

    # Strip away CFN builtins around this
    if isinstance(template_url, dict):  # URL is a dictionary
        if "Fn::Sub" in template_url.keys():  # There is a !Sub
            # TODO: Explain what we are doing and why
            if isinstance(template_url["Fn::Sub"], str):
                template_path = template_url["Fn::Sub"].split("}")[-1]
            else:
                template_path = template_url["Fn::Sub"][0].split("}")[-1]
        elif "Fn::Join" in list(template_url.keys())[0]:
            # TODO: Explain what we are doing/why
            template_path = template_url["Fn::Join"][1][-1]
        elif "Fn::If" in list(template_url.keys())[0]:
            # TODO: Eval an If ...
            # Potentially check either or both if it is single level
            message = "Unable to evaluate Fn::If in TemplateURL: %s"
            raise Exception(message % (template_url))
        else:
            message = "Unable to parse template_path from TemplateURL: %s"
            raise Exception(message % (template_url))
    elif isinstance(template_url, str):
        template_path = "/".join(template_url.split("/")[-2:])

    # Try current template dir
    project_root = Path(
        os.path.dirname(current_template_path)
    )

    child_template_file = template_path.split("/")[-1]
    final_template_path = Path(
        "/".join(
            [str(project_root), str(child_template_file)]
        )
    )

    if final_template_path.exists() and final_template_path.is_file():
        return final_template_path

    # Try current template dir + prefix
    final_template_path = Path(
        "/".join(
            [str(project_root), str(template_path)]
        )
    )

    if final_template_path.exists() and final_template_path.is_file():
        return final_template_path

    # Try one directory up
    project_root = Path(
        os.path.normpath(
            os.path.dirname(current_template_path) + "/../"
        )
    )

    final_template_path = Path(
        "/".join(
            [str(project_root), str(template_path)]
        )
    )

    if final_template_path.exists() and final_template_path.is_file():
        return final_template_path

    message = "Failed to discover path for %s, path %s does not exist"
    raise Exception(message % (template_url, template_path))
