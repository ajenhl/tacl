"""Module containing the Corpus class."""

import logging
import os

from .text import Text


class Corpus (object):

    """A Corpus represents a collection of `Text`\s.

    A Corpus is built from a directory that contains the text files
    that become `Text` objects.

    """

    def __init__ (self, path, manager):
        self._path = os.path.abspath(path)
        self._manager = manager

    def counts (self, catalogue):
        """Returns the n-gram totals by size and text for the labelled
        texts in `catalogue`.

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :rtype: `sqlite3.Cursor`

        """
        self._manager.clear_labels()
        labels = self._set_labels(catalogue)
        return self._manager.counts(labels)

    def diff (self, catalogue):
        """Returns the n-gram data for the differences between the
        sets of texts in `catalogue`.

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :rtype: `sqlite3.Cursor`

        """
        self._manager.clear_labels()
        labels = self._set_labels(catalogue)
        return self._manager.diff(labels)

    def generate_ngrams (self, minimum, maximum, index):
        """Generates the n-grams (`minimum` <= n <= `maximum`) for
        this corpus.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :param index: whether to drop indices before adding n-grams
        :type index: `bool`

        """
        logging.info('Generating n-grams ({} <= n <= {}) for the corpus'.format(
                minimum, maximum))
        filenames = os.listdir(self._path)
        total = len(filenames)
        count = 1
        if index and filenames:
            self._manager.drop_indices()
        for filename in filenames:
            logging.info('Operating on text {} of {}'.format(count, total))
            text = self._open_text(filename)
            text.generate_ngrams(minimum, maximum)
            count = count + 1
        self._manager.add_indices()
        self._manager.analyse()
        self._manager.vacuum()

    def intersection (self, catalogue):
        """Returns the n-gram data for the intersection between the
        sets of texts in `catalogue`.

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :rtype: `sqlite3.Cursor`

        """
        self._manager.clear_labels()
        labels = self._set_labels(catalogue)
        return self._manager.intersection(labels)

    def _open_text (self, filename):
        """Returns a `Text` object for `filename`.

        :rtype: `tacl.Text`

        """
        path = os.path.join(self._path, filename)
        try:
            content = open(path, 'rb').read()
            text = Text(filename, content, self._manager)
        except IOError:
            logging.error('Text {} does not exist in the corpus'.format(
                    filename))
            raise
        return text

    def _set_labels (self, catalogue):
        """Returns the labels from `catalogue`, and sets them in the
        database.

        :rtype: `list`

        """
        labels = set()
        for filename, label in catalogue.items():
            if label != '':
                labels.add(label)
                text = self._open_text(filename)
                text.add_label(label)
        return list(labels)
