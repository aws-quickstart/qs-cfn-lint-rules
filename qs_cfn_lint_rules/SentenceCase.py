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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
from spellchecker import SpellChecker
import re
import os


custom_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_dict.txt")


class Base(CloudFormationLintRule):
    """Check Parameter descriptions and labels are sentence case"""
    id = 'W9006'
    shortdesc = 'Parameter descriptions should be sentence case'
    description = 'Parameter descriptions should be sentence case'
    source_url = 'https://github.com/qs_cfn_lint_rules/qs_cfn_lint_rules'
    tags = ['parameters']

    @staticmethod
    def get_custom_dict(filepath=custom_dict_path):
        with open(filepath, 'r') as f:
            wordlist = [l.replace("\n", "") for l in f.readlines()]
        return set(wordlist)

    @staticmethod
    def get_errors(description, spell, custom_dict):
        dict_words = set([])
        title_errors = set([])
        # Remove items from the custom dict from the string
        for pn in custom_dict:
            description = description.replace(pn, "")
        for sentence in description.split("."):
            word_no = 0
            # [OPTIONAL] prefix should not be considered as part of the string, as it is stripped from
            # the deployment guide
            if sentence.startswith('[OPTIONAL] '):
                sentence = sentence.replace('[OPTIONAL] ', '')
            for pn in custom_dict:
                # if sentence starts with a proper noun then we don't need to check for sentence case
                if sentence.startswith(pn):
                    word_no += 1
                sentence = sentence.replace(pn, "")
            if len(sentence.strip()) > 1:
                # Check that first letter of first word is UPPER
                if sentence[0].upper() != sentence[0]:
                    title_errors.add(sentence.split()[0])
                else:
                    for word in re.split('[^a-zA-Z]', sentence):
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
        title_message = 'Parameter {0} Description is not sentence case: {1}'
        spell_message = 'Parameter {0} contains spelling error(s): {1}'

        if "Parameters" not in cfn.template.keys():
            return matches
        else:
            custom_dict = self.get_custom_dict()
            spell = SpellChecker()
            if "Metadata" in cfn.template.keys():
                if "LintSpellExclude" in cfn.template["Metadata"].keys():
                    # add any proper nouns defined in template metadata
                    custom_dict = custom_dict.union(set(cfn.template["Metadata"]["LintSpellExclude"]))
            for x in cfn.template["Parameters"]:
                if "Description" in cfn.template["Parameters"][x].keys():
                    location = ["Parameters", x, "Description"]
                    description = cfn.template["Parameters"][x]["Description"]
                    spell_errors, title_errors = self.get_errors(description, spell, custom_dict)
                    if title_errors:
                        matches.append(RuleMatch(location, title_message.format(x, title_errors)))
                    if spell_errors:
                        matches.append(RuleMatch(location, spell_message.format(x, spell_errors)))
        return matches
