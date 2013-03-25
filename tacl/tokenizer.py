"""Module containing the Tokenizer class."""

import re


class Tokenizer (object):

    """A tokenizer that splits a string using a regular expression.

    Based on the RegexpTokenizer from the Natural Language Toolkit.

    """

    def __init__ (self, pattern, flags=re.UNICODE | re.MULTILINE | re.DOTALL):
        try:
            self._regexp = re.compile(pattern, flags)
        except re.error as err:
            raise ValueError('Error in regular expression %r: %s' %
                             (pattern, err))

    def tokenize (self, text):
        return self._regexp.findall(text)
