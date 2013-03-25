"""Module containing the Corpus class."""

import os

from .text import Text


class Corpus (object):

    """A Corpus represents a collection of `Text`\s.

    A Corpus is built from a directory that contains the text files
    that become `Text` objects.

    """

    def __init__ (self, path):
        self._path = os.path.abspath(path)

    def get_text (self, filename):
        """Returns a `Text` representing the file at `filename`.

        :param filename: filename (absent path) of text
        :type filename: `str`
        :rtype: `Text`

        """
        with open(os.path.join(self._path, filename), encoding='utf-8') as text:
            content = text.read()
        return Text(filename, content)

    def get_texts (self):
        """Returns a generator supplying `Text` objects for each file
        in the corpus.

        :rtype: `generator`

        """
        for filename in os.listdir(self._path):
            yield self.get_text(filename)
