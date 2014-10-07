"""Module containing the Corpus class."""

import logging
import os.path

from .text import Text


class Corpus:

    """A Corpus represents a collection of `Text`\s.

    A Corpus is built from a directory that contains the text files
    that become `Text` objects.

    """

    def __init__ (self, path, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._path = os.path.abspath(path)
        self._tokenizer = tokenizer

    def get_text (self, filename):
        """Returns a `Text` representing the file at `filename`.

        :param filename: filename (absent path) of text
        :type filename: `str`
        :rtype: `Text`

        """
        self._logger.debug('Creating Text object from {}'.format(filename))
        with open(os.path.join(self._path, filename), encoding='utf-8') as text:
            content = text.read()
        return Text(filename, content, self._tokenizer)

    def get_texts (self):
        """Returns a generator supplying `Text` objects for each file
        in the corpus.

        :rtype: `generator`

        """
        for filename in os.listdir(self._path):
            if os.path.isfile(os.path.join(self._path, filename)):
                yield self.get_text(filename)
