"""Module containing the Corpus class."""

import glob
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

    def get_sigla (self, name):
        """Returns a list of all of the sigla for the named text.

        :param name: name of text
        :type name: `str`
        :rtype: `list` of `str`

        """
        return [os.path.splitext(os.path.basename(path))[0]
                for path in glob.glob(os.path.join(self._path, name, '*.txt'))]

    def get_text (self, name, siglum):
        """Returns a `Text` representing the file associated with `name` and
        `siglum`.

        Combined, `name` and `siglum` form the basis of a filename for
        retrieving the text.

        :param name: name of text
        :type name: `str`
        :param siglum: siglum (variant name) of text
        :type siglum: `str`
        :rtype: `Text`

        """
        filename = os.path.join(name, siglum + '.txt')
        self._logger.debug('Creating Text object from {}'.format(filename))
        with open(os.path.join(self._path, filename), encoding='utf-8') as text:
            content = text.read()
        return Text(name, siglum, content, self._tokenizer)

    def get_texts (self, name='*'):
        """Returns a generator supplying `Text` objects for each file
        in the corpus.

        :rtype: `generator`

        """
        for filepath in glob.glob(os.path.join(self._path, name, '*.txt')):
            if os.path.isfile(filepath):
                name = os.path.split(os.path.split(filepath)[0])[1]
                siglum = os.path.splitext(os.path.basename(filepath))[0]
                yield self.get_text(name, siglum)
