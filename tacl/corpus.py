"""Module containing the Corpus class."""

import csv
import logging
import os

from . import constants
from .text import Text


class Corpus (object):

    """A Corpus represents a collection of `Text`\s.

    A Corpus is built from a directory that contains the text files
    that become `Text` objects.

    """

    def __init__ (self, path, manager):
        self._path = os.path.abspath(path)
        self._manager = manager

    def counts (self, catalogue, fh):
        """Writes the n-gram totals by size and text for the labelled
        texts in `catalogue` to `fh` and returns it.

        The CSV format has the columns:

            filename
            size (of n-gram)
            total (number of unique n-grams of this size)
            count (number of individual n-grams of this size)
            label

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        self._manager.clear_labels()
        labels = self._set_labels(catalogue)
        return self._csv(self._manager.counts(labels),
                         constants.COUNTS_FIELDNAMES, fh)

    def _csv (self, cursor, fieldnames, fh):
        """Writes the rows of `cursor` in CSV format to `fh` and
        returns it.

        :param cursor: database cursor containing data to be be output
        :type cursor: `sqlite3.Cursor`
        :param fieldnames: row headings
        :type fieldnames: `list`
        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        logging.info('Finished query; outputting results in CSV format')
        writer = csv.writer(fh)
        writer.writerow(fieldnames)
        for row in cursor:
            writer.writerow([row[fieldname] for fieldname in fieldnames])
        return fh

    def diff (self, catalogue, fh):
        """Writes the n-gram data for the differences between the sets
        of texts in `catalogue` to `fh` and returns it.

        The CSV format has the columns:

            n-gram
            size (of n-gram)
            filename
            count (of instances of n-gram)
            label

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        self._manager.clear_labels()
        labels = self._set_labels(catalogue)
        return self._csv(self._manager.diff(labels),
                         constants.QUERY_FIELDNAMES, fh)

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

    def intersection (self, catalogue, fh):
        """Writes the n-gram data for the intersection between the
        sets of texts in `catalogue` to `fh`.

        The CSV format has the columns:

            n-gram
            size (of n-gram)
            filename
            count (of instances of n-gram)
            label

        :param catalogue: association of texts with labels
        :type catalogue: `Catalogue`
        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        self._manager.clear_labels()
        labels = self._set_labels(catalogue)
        return self._csv(self._manager.intersection(labels),
                         constants.QUERY_FIELDNAMES, fh)

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
        self._manager.analyse('Text')
        return list(labels)
