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
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from spellchecker import SpellChecker
import re
import os


custom_dict_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/custom_dict.txt"
)


def strip_urls(s):
    for w in s.split(" "):
        if "://" in w:
            s = s.replace(w, "")
    return s


class Base(CloudFormationLintRule):
    """Check Parameter descriptions and labels are sentence case"""

    id = "W9006"
    shortdesc = "Parameter descriptions should be sentence case"
    description = "Parameter descriptions should be sentence case"
    source_url = "https://github.com/qs_cfn_lint_rules/qs_cfn_lint_rules"
    tags = ["parameters"]

    @staticmethod
    def get_custom_dict(filepath=custom_dict_path):
        with open(filepath, "r") as f:
            wordlist = [l.replace("\n", "") for l in f.readlines()]
        return set(wordlist)

    @staticmethod
    def get_errors(description, spell, custom_dict, sentence_case_exclude):
        dict_words = set([])
        title_errors = set([])
        # [OPTIONAL] prefix should not be considered as part of the string, as it is stripped from
        # the deployment guide
        description = re.sub(r"^[\[\(]OPTIONAL[\]\)] ", "", description, flags=re.IGNORECASE)
        # Remove example resource IDs
        description = re.sub(r"\b[a-z]+-(?:[0-9a-f]{8}|[0-9a-f]{17})\b", "", description)
        # Remove example ARNs
        description = re.sub(r"\barn:\S+\b", "", description)
        # Remove items from the custom dictionary or the sentence case exclusions from the string
        for pn in custom_dict.union(sentence_case_exclude):
            description = re.sub(r"\b" + re.escape(pn) + r"\b", "", description)
        for sentence in description.split("."):
            word_no = 0
            for pn in custom_dict:
                # if sentence starts with a proper noun then we don't need to check for sentence case
                if sentence.startswith(pn):
                    word_no += 1
                sentence = re.sub(r"\b" + re.escape(pn) + r"\b", "", sentence, flags=re.IGNORECASE)
            if len(sentence.strip()) > 1:
                # Check that first letter of first word is UPPER
                if sentence[0].upper() != sentence[0]:
                    title_errors.add(sentence.split()[0])
                else:
                    for word in re.split("[^a-zA-Z]", sentence):
                        # ignore 0 length words
                        if word:
                            # Fully uppercase words are considered abbreviations
                            if word_no == 0 and word != word.upper():
                                dict_words.add(word)
                            elif word != word.upper():
                                dict_words.add(word)
                                if word[0].isupper():
                                    title_errors.add(word)
                            word_no += 1
        spell_errors = spell.unknown(list(dict_words))
        for s in list(title_errors):
            if s.lower() in spell_errors:
                title_errors.remove(s)
                spell_errors.remove(s.lower())
        return spell_errors, title_errors

    def match(self, cfn):
        """Basic Matching"""
        matches = []
        title_message = "Parameter {0} Description is not sentence case: {1}"
        spell_message = "Parameter {0} contains spelling error(s): {1}"
        stop_message = 'Parameter {0} must end in a full stop "."'

        # Ignore templates that are not entry points
        if not cfn.template.get("Metadata", {}).get("QuickStartDocumentation"):
            return matches

        if self.id in cfn.template.get("Metadata", {}).get("QSLint", {}).get(
            "Exclusions", []
        ):
            return matches
        if "Parameters" not in cfn.template.keys():
            return matches
        else:
            custom_dict = self.get_custom_dict()
            sentence_case_exclude = cfn.template.get("Metadata", {}).get("SentenceCaseExclude", [])
            spell = SpellChecker()
            if "Metadata" in cfn.template.keys():
                if "LintSpellExclude" in cfn.template["Metadata"].keys():
                    # add any proper nouns defined in template metadata
                    custom_dict = custom_dict.union(
                        set(cfn.template["Metadata"]["LintSpellExclude"])
                    )
            for x in cfn.template["Parameters"]:
                if "Description" in cfn.template["Parameters"][x].keys():
                    location = ["Parameters", x, "Description"]
                    description = cfn.template["Parameters"][x]["Description"]
                    stop_error = not (
                        description.strip()[-1] == "."
                        or description.strip()[-2:] == '."'
                    )
                    description = strip_urls(description)
                    spell_errors, title_errors = self.get_errors(
                        description, spell, custom_dict, sentence_case_exclude,
                    )
                    if stop_error:
                        matches.append(
                            RuleMatch(location, stop_message.format(x))
                        )
                    if title_errors:
                        matches.append(
                            RuleMatch(
                                location, title_message.format(x, title_errors)
                            )
                        )
                    if spell_errors:
                        matches.append(
                            RuleMatch(
                                location, spell_message.format(x, spell_errors)
                            )
                        )
            if "Metadata" not in cfn.template.keys():
                matches.append(
                    RuleMatch(
                        ["Parameters"],
                        "Template is missing Parameter labels and groups",
                    )
                )
            elif (
                "AWS::CloudFormation::Interface"
                not in cfn.template["Metadata"].keys()
            ):
                matches.append(
                    RuleMatch(
                        ["Metadata"],
                        "Template is missing Parameter labels and groups",
                    )
                )
            elif (
                "ParameterGroups"
                not in cfn.template["Metadata"][
                    "AWS::CloudFormation::Interface"
                ].keys()
            ):
                matches.append(
                    RuleMatch(
                        ["Metadata", "AWS::CloudFormation::Interface"],
                        "Template is missing Parameter groups",
                    )
                )
            elif (
                "ParameterLabels"
                not in cfn.template["Metadata"][
                    "AWS::CloudFormation::Interface"
                ].keys()
            ):
                matches.append(
                    RuleMatch(
                        ["Metadata", "AWS::CloudFormation::Interface"],
                        "Template is missing Parameter labels",
                    )
                )
            else:
                count = 0
                for x in cfn.template["Metadata"][
                    "AWS::CloudFormation::Interface"
                ]["ParameterGroups"]:
                    title_message = (
                        'Parameter Group name "{0}" is not sentence case: {1}'
                    )
                    spell_message = 'Parameter Group name "{0}" contains spelling error(s): {1}'
                    if "Label" not in x.keys():
                        matches.append(
                            RuleMatch(
                                [
                                    "Metadata",
                                    "AWS::CloudFormation::Interface",
                                    "ParameterGroups",
                                    x,
                                ],
                                "Template is missing Parameter groups",
                            )
                        )
                    elif "default" not in x["Label"].keys():
                        matches.append(
                            RuleMatch(
                                [
                                    "Metadata",
                                    "AWS::CloudFormation::Interface",
                                    "ParameterGroups",
                                    x,
                                ],
                                "Template is missing Parameter groups",
                            )
                        )
                    else:
                        location = [
                            "Metadata",
                            "AWS::CloudFormation::Interface",
                            "ParameterGroups",
                            count,
                            "Label",
                            "default",
                        ]
                        description = x["Label"]["default"]
                        spell_errors, title_errors = self.get_errors(
                            description, spell, custom_dict, sentence_case_exclude,
                        )
                        if title_errors:
                            matches.append(
                                RuleMatch(
                                    location,
                                    title_message.format(
                                        x["Label"]["default"], title_errors
                                    ),
                                )
                            )
                        if spell_errors:
                            matches.append(
                                RuleMatch(
                                    location,
                                    spell_message.format(
                                        x["Label"]["default"], spell_errors
                                    ),
                                )
                            )
                    count += 1
                for x in cfn.template["Metadata"][
                    "AWS::CloudFormation::Interface"
                ]["ParameterLabels"]:
                    title_message = "Parameter Label is not sentence case: {0}"
                    spell_message = (
                        "Parameter Label contains spelling error(s): {0}"
                    )
                    if (
                        "default"
                        not in cfn.template["Metadata"][
                            "AWS::CloudFormation::Interface"
                        ]["ParameterLabels"][x].keys()
                    ):
                        matches.append(
                            RuleMatch(
                                [
                                    "Metadata",
                                    "AWS::CloudFormation::Interface",
                                    "ParameterLabels",
                                    x,
                                ],
                                "Template is missing Parameter labels",
                            )
                        )
                    else:
                        location = [
                            "Metadata",
                            "AWS::CloudFormation::Interface",
                            "ParameterLabels",
                            x,
                            "default",
                        ]
                        description = cfn.template["Metadata"][
                            "AWS::CloudFormation::Interface"
                        ]["ParameterLabels"][x]["default"]
                        spell_errors, title_errors = self.get_errors(
                            description, spell, custom_dict, sentence_case_exclude,
                        )
                        if title_errors:
                            matches.append(
                                RuleMatch(
                                    location,
                                    title_message.format(title_errors),
                                )
                            )
                        if spell_errors:
                            matches.append(
                                RuleMatch(
                                    location,
                                    spell_message.format(spell_errors),
                                )
                            )
                    count += 1
        return matches
