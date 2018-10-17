"""Module containing the Corpus class."""

import glob
import logging
import os.path

from .text import WitnessText


class Corpus:

    """A Corpus represents a collection of `WitnessText`s.

    A Corpus is built from a directory that contains the text files
    that become `WitnessText` objects.

    """

    def __init__(self, path, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._path = os.path.abspath(path)
        self._tokenizer = tokenizer

    def get_sigla(self, work):
        """Returns a list of all of the sigla for `work`.

        :param work: name of work
        :type work: `str`
        :rtype: `list` of `str`

        """
        return [os.path.splitext(os.path.basename(path))[0]
                for path in glob.glob(os.path.join(self._path, work, '*.txt'))]

    def get_witness(self, work, siglum, text_class=WitnessText):
        """Returns a `WitnessText` representing the file associated with
        `work` and `siglum`.

        Combined, `work` and `siglum` form the basis of a filename for
        retrieving the text.

        :param work: name of work
        :type work: `str`
        :param siglum: siglum of witness
        :type siglum: `str`
        :rtype: `WitnessText`

        """
        filename = os.path.join(work, siglum + '.txt')
        self._logger.debug('Creating WitnessText object from {}'.format(
            filename))
        with open(os.path.join(self._path, filename), encoding='utf-8') \
                as fh:
            content = fh.read()
        return text_class(work, siglum, content, self._tokenizer)

    def get_witnesses(self, name='*'):
        """Returns a generator supplying `WitnessText` objects for each work
        in the corpus.

        :rtype: `generator` of `WitnessText`

        """
        for filepath in glob.glob(os.path.join(self._path, name, '*.txt')):
            if os.path.isfile(filepath):
                name = os.path.split(os.path.split(filepath)[0])[1]
                siglum = os.path.splitext(os.path.basename(filepath))[0]
                yield self.get_witness(name, siglum)

    def get_works(self):
        """Returns a list of the names of all works in the corpus.

        :rtype: `list` of `str`

        """
        return [os.path.split(filepath)[1] for filepath in
                glob.glob(os.path.join(self._path, '*'))
                if os.path.isdir(filepath)]
