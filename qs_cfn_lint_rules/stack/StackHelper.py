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
from urllib.parse import urlparse
from pathlib import Path
import json

MAX_DEPTH = 6  # Handle at most 6 levels of nesting in TemplateURL expressions


def rewrite_vars(string, depth=1):
    """Replace the ${var} placeholders with ##var##"""
    parts = string.split("${")
    parts = parts[1].split("}")

    rep_text= "${" + parts[0] + "}"
    rep_with = "##" + parts[0] + "##"

    newtext = string.replace(rep_text, rep_with)

    if len(newtext.split("${")) > 1:
        newtext = rewrite_vars(newtext, depth=(depth+1))

    return newtext


def rewrite_sub_vars(string, depth=1):
    """Replace the '##var##' placeholders with 'var'"""
    # TODO: Allow user to inject RunTime values for these
    if "##" not in string:
        return string

    parts = string.split("##")
    parts = parts[1].split("##")

    rep_text= "##" + parts[0] + "##"
    rep_with = "" + parts[0] + ""

    newtext = string.replace(rep_text, rep_with)

    if "##" in newtext:  # Recurse if we have more variables
        newtext = rewrite_sub_vars(newtext, depth=(depth+1))

    return newtext


def rewrite_sub_vars_with_values(temp_expression, values):
    """Rewrite sub vars with actual variable values"""
    result = temp_expression
    values_dict = []

    print("rewrite Values: {}".format(values))
    # Create dictionary of values
    values_dict_string = values.replace("(", "{")
    values_dict_string = values_dict_string.replace(")", "}")
    values_dict_string = values_dict_string.replace("'", '"')
    print("rewrite Values: {}".format(values_dict_string))
    values_dict = json.loads(values_dict_string)

    # TODO: Allow user to inject RunTime values for these
    # replace each key we have a value for
    for key in values_dict:
        rep_text = "##" + key + "##"
        rep_with = "" + values_dict[key] + ""

        result = result.replace(rep_text, rep_with)


def evaluate_fn_sub(expression):
    """ Return expression with values replaced """
    results = []

    # print("Fn::Sub: '{}'".format(expression))

    # Handle Sub of form [ StringToSub, { "key" : "value", "key": "value" }]
    if "[" in expression:
        temp_expression = expression.split("[")[1].split(",")[0]
        # TODO: Fix this for more than one provided sub value
        values = expression.split("[")[1].split(",")[1].strip("]")
        rewrite_sub_vars_with_values(temp_expression, values)
    else:
        temp_expression = expression.split("': '")[1].split("'")[0]


    # We have made all of the expressions to be replaced ##VARIABLE##

    # Builtins - Fudge some defaults here since we don't have runtime info

    # ${AWS::Region} ${AWS::AccountId}

    # okay so now we look at the list at the end if there is one

    # if we still have them we just use their values (ie: Parameters)
    result = rewrite_sub_vars(temp_expression)

    results.append(result)
    # print("Fn::Sub: '{}'".format(temp_expression))

    return results


def evaluate_fn_join(expression):
    """ Return the joined stuff """
    results = []
    new_values_list = []

    temp = expression.split("[")[1]
    delimeter = temp.split(",")[0].strip("'")

    values = expression.split("[")[2]
    values = values.split("]]")[0]

    values_list = values.split(", ")
    for value in values_list:
        new_values_list.append(value.strip("'"))

    result = delimeter.join(new_values_list)
    results.append(result)

    return results


def evaluate_fn_if(expression):
    """ Return both possible parts of the expression """
    results = []

    value_true = expression.split(",")[1]
    value_false = expression.split(",")[2].strip("]")
    results.append(value_true)
    results.append(value_false)
    # print("Fn::If: {} {}".format(value_true, value_false))

    return results


def evaluate_fn_ref(expression):
    """Since this is runtime data the best we can do is the name in place"""
    # TODO: Allow user to inject RunTime values for these
    results = []

    temp = expression.split(": ")[1]
    # print("Ref: {}".format(temp))
    results.append(temp)

    return results


def evaluate_fn_findinmap(expression):
    raise Exception("Fn::FindInMap: not supported")


def evaluate_fn_getatt(expression):
    raise Exception("Fn::FindInMap: not supported")


def evaluate_fn_split(expression):
    raise Exception("Fn::FindInMap: not supported")


def evaluate_expression_controller(expression):
    """Figure out what type of expression and pass off to handler"""
    results = []

    if "Fn::If" in expression:
        results = evaluate_fn_if(expression)

    elif "Fn::Sub" in expression:
        results = evaluate_fn_sub(expression)

    elif "Fn::Join" in expression:
        results = evaluate_fn_join(expression)

    elif "Ref" in expression:
        results = evaluate_fn_ref(expression)

    elif "Fn::FindInMap" in expression:
        results = evaluate_fn_findinmap(expression)

    elif "Fn::GettAtt" in expression:
        results = evaluate_fn_getatt(expression)

    elif "Fn::Split" in expression:
        results = evaluate_fn_split(expression)

    else:
        # This is a NON expression replace the { and } with ( and ) to not recursively evaluate this
        results.append("(" + expression + ")")

    return results


def evaluate_string(template_url, depth=0):
    """Recursively find expressions in the URL and send them to be evaluated"""
    # Recursion bail out
    if depth > MAX_DEPTH:
        raise Exception("Template URL contains more than {} levels or nesting".format(MAX_DEPTH))

    template_urls = []
    # Evaluate expressions
    if "{" in template_url:
        parts = template_url.split("{")
        parts = parts[-1].split("}")  # Last open bracket

        # This function will handle Fn::Sub Fn::If etc.
        replacements = evaluate_expression_controller(parts[0])  # First closed bracket after

        for replacement in replacements:
            template_url_temp = template_url
            # print("evaluate_string: (before) {}".format(template_url))
            # print("expression: {}".format(parts[0]))
            # print("replacement: {}".format(replacement))
            template_url_temp = template_url_temp.replace("{" + parts[0] + "}", replacement)
            # print("evaluate_string: (after) {}".format(template_url_temp))

            evaluated_strings = evaluate_string(template_url_temp, depth=(depth+1))
            for evaluated_string in evaluated_strings:
                template_urls.append(evaluated_string)
    else:
        template_urls.append(template_url)

    return template_urls


def _flatten_template_controller(template_url):
    """ Recursively evaluate subs/ifs"""
    url_list = []

    # Replace ${SOMEVAR} with ##SOMEVAR## so finding actual "expressions" is easier
    template_url_string = str(template_url)

    parts = template_url_string.split("${")
    if len(parts) > 1:
        template_url_string = rewrite_vars(template_url_string)

    # Evaluate expressions recursively
    if "{" in template_url_string:
        replacements = evaluate_string(template_url_string)  # first closed bracket
        for replacement in replacements:
            url_list.append(replacement)

    else:
        url_list.append(template_url)

    return url_list


def flatten_template_url(template_url):
    """Flatten template_url and return all permutations"""
    path_list = []
    url_list = _flatten_template_controller(template_url)

    print(url_list)
    # Extract the path portion from the URL
    for url in url_list:
        print("url: {}".format(str(url)))
        o = urlparse(str(url))
        path_list.append(o.path)

    return path_list


def find_local_child_template(parent_template_path, child_template_path):
    # Start where the Parent template is
    project_root = Path(
        os.path.dirname(parent_template_path)
    )

    # Try current template dir
    child_template_file = child_template_path.split("/")[-1]
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
            [str(project_root), str(child_template_path)]
        )
    )

    if final_template_path.exists() and final_template_path.is_file():
        return final_template_path

    # Try one directory up
    project_root = Path(
        os.path.normpath(
            os.path.dirname(parent_template_path) + "/../"
        )
    )

    final_template_path = Path(
        "/".join(
            [str(project_root), str(child_template_path)]
        )
    )

    if final_template_path.exists() and final_template_path.is_file():
        return final_template_path

    message = "Failed to discover local path for %s."
    raise Exception(message % child_template_path)


def template_url_to_pathv2(current_template_path, template_url):
    child_local_paths = []
    child_template_paths = flatten_template_url(template_url)

    for child_template_path in child_template_paths:
        child_local_paths.append(find_local_child_template(current_template_path, child_template_path))

    return child_local_paths

#
# Replace this stuff
#


def template_url_to_path(current_template_path, template_url):
    """extract a file path from a CFN Stack Resource TemplateURL property"""
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
