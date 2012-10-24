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
        keep_unlabelled = True
        if catalogue:
            keep_unlabelled = False
        texts = []
        for filename in os.listdir(self._path):
            label = catalogue.get(filename, '')
            if label or keep_unlabelled:
                texts.append(Text(filename, self._path, self._manager, label))
        return texts

    def diff (self, catalogue, minimum, maximum, occurrences, individual):
        """Returns the n-gram data for the differences between the
        sets of texts in `catalogue`.

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :param occurrences: minimum number of occurrences for an
            n-gram to be reported
        :type occurrences: `int`
        :param individual: whether to report on individual text results
        :type individual: `bool`
        :rtype: `list` of `sqlite3.Row`

        """
        self.generate_ngrams(minimum, maximum, catalogue)
        labels = catalogue.labels()
        if individual:
            return self._manager.diff_text(labels, minimum, maximum,
                                           occurrences)
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
        texts = self._load_texts(catalogue)
        total = len(texts)
        count = 1
        for text in texts:
            logging.debug('Operating on text %d of %d' % (count, total))
            text.generate_ngrams(minimum, maximum)
            count = count + 1
        self._manager.add_indices()
        if catalogue is None:
            self._manager.vacuum()
        self._manager.analyse()

    def intersection (self, catalogue, minimum, maximum, occurrences,
                      individual):
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
        :param individual: whether to report on individual text results
        :type individual: `bool`
        :rtype: `list` of `sqlite3.Row`

        """
        self.generate_ngrams(minimum, maximum, catalogue)
        labels = catalogue.labels()
        if individual:
            return self._manager.intersection_text(labels, minimum, maximum,
                                                   occurrences)
        return self._manager.intersection(labels, minimum, maximum, occurrences)
