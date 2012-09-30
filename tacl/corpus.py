import logging
import os

from text import Text


class Corpus (object):

    """A Corpus represents a collection of `Text`\s.

    A Corpus is built from a directory that contains the text files
    that become `Text` objects.

    """

    def __init__ (self, path, manager):
        self._path = os.path.abspath(path)
        self._manager = manager

    def _load_texts (self, catalogue):
        """Returns a list of `Text`\s in this corpus.

        :param catalogue: catalogue of texts with labels
        :type catalogue: `Catalogue`
        :rtype: `list`

        """
        logging.debug('Loading the texts for the corpus')
        catalogue = catalogue or {}
        texts = []
        for filename in os.listdir(self._path):
            label = catalogue.get(filename, '')
            texts.append(Text(filename, self._path, self._manager, label))
        return texts

    def diff (self, catalogue, minimum, maximum, occurrences):
        """Returns the n-gram data for the differences between the
        sets of texts in `catalogue`.

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :param occurrences: minimum number of occurrences for an n-gram to be reported
        :type occurrences: `int`
        :rtype: `list` of `sqlite3.Row`

        """
        self.generate_ngrams(minimum, maximum, catalogue)
        labels = catalogue.labels()
        return self._manager.diff(labels, minimum, maximum, occurrences)

    def generate_ngrams (self, minimum, maximum, catalogue=None):
        """Generates the n-grams (`minimum` <= n <= `maximum`) for
        this corpus.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`

        """
        logging.debug('Generating n-grams (%d <= n <= %d) for the corpus' %
                      (minimum, maximum))
        for text in self._load_texts(catalogue):
            text.generate_ngrams(minimum, maximum)

    def intersection (self, catalogue, minimum, maximum, occurrences):
        """Returns the n-gram data for the intersection between the
        sets of texts in `catalogue`.

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :param occurrences: minimum number of occurrences for an n-gram to be reported
        :type occurrences: `int`
        :rtype: `list` of `sqlite3.Row`

        """
        self.generate_ngrams(minimum, maximum, catalogue)
