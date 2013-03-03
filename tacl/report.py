"""Module containing the Report class."""

import csv
import io
import logging

from .tokenizer import tokenizer


COUNT_INDEX = 3
FILENAME_INDEX = 2
LABEL_INDEX = 4
NGRAM_INDEX = 0
SIZE_INDEX = 1

HOMOGENOUS_KEY = 'homogenous'
FILENAMES_KEY = 'filenames'


class Report:

    def __init__ (self, results):
        self._rows = [row for row in csv.reader(results)]

    def csv (self):
        """Returns the report data in CSV format.

        :rtype: `io.StringIO`

        """
        output_fh = io.StringIO(newline='')
        writer = csv.writer(output_fh)
        for row in self._rows:
            writer.writerow(row)
        output_fh.seek(0)
        return output_fh

    def _generate_substrings (self, ngram, size):
        """Returns a list of all substrings of `ngram`.

        :param ngram: n-gram to generate substrings of
        :type ngram: `str`
        :param size: size of `ngram`
        :type size: `int`
        :rtype: `list`

        """
        substrings = []
        tokens = tokenizer.tokenize(ngram)
        for n in range(1, size):
            count = max(0, len(tokens) - n + 1)
            ngrams = [''.join(tokens[i:i+n]) for i in range(count)]
            substrings.extend(ngrams)
        return substrings

    def prune_by_ngram_count (self, minimum=None, maximum=None):
        """Removes results rows whose total n-gram count (across all
        texts bearing this n-gram) is outside the range specified by
        `minimum` and `maximum`.

        :param minimum: minimum n-gram count
        :type minimum: `int`
        :param maximum: maximum n-gram count
        :type maximum: `int`

        """
        logging.info('Pruning results by n-gram count')
        new_rows = []
        data = {}
        for row in self._rows:
            ngram = row[NGRAM_INDEX]
            count = data.setdefault(ngram, 0)
            count += int(row[COUNT_INDEX])
            data[ngram] = count
        ngrams = []
        for ngram, count in data.items():
            if minimum and count < minimum:
                continue
            if maximum and count > maximum:
                continue
            ngrams.append(ngram)
        new_rows = [row for row in self._rows if row[NGRAM_INDEX] in ngrams]
        self._rows = new_rows

    def prune_by_ngram_size (self, minimum=None, maximum=None):
        """Removes results rows whose n-gram size is outside the
        range specified by `minimum` and `maximum`.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`

        """
        logging.info('Pruning results by n-gram size')
        new_rows = []
        for row in self._rows:
            size = int(row[SIZE_INDEX])
            if minimum and size < minimum:
                continue
            if maximum and size > maximum:
                continue
            new_rows.append(row)
        self._rows = new_rows

    def prune_by_text_count (self, minimum=None, maximum=None):
        """Removes results rows for n-grams that are not attested in a
        number of texts in the range specified by `minimum` and
        `maximum`.

        :param minimum: minimum number of texts
        :type minimum: `int`
        :param maximum: maximum number of texts
        :type maximum: `int`

        """
        logging.info('Pruning results by text count')
        new_rows = []
        data = {}
        for row in self._rows:
            ngram = row[NGRAM_INDEX]
            text_count = data.setdefault(ngram, 0)
            text_count += 1
            data[ngram] = text_count
        ngrams = []
        for ngram, count in data.items():
            if minimum and count < minimum:
                continue
            if maximum and count > maximum:
                continue
            ngrams.append(ngram)
        new_rows = [row for row in self._rows if row[NGRAM_INDEX] in ngrams]
        self._rows = new_rows

    def _reduce_by_ngram (self, data, ngram):
        """Lowers the counts of all n-grams in `data` that are
        substrings of `ngram` by `ngram`\'s count.

        Modifies `data` in place.

        :param data: row data dictionary for the current text
        :type data: `dict`
        :param ngram: n-gram being reduced
        :type ngram: `str`

        """
        # Find all substrings of `ngram` and reduce their count by the
        # count of `ngram`. Substrings may not exist in `data`.
        count = data[ngram]['count']
        for substring in self._generate_substrings(ngram, data[ngram]['size']):
            try:
                substring_data = data[substring]
            except KeyError:
                continue
            else:
                substring_data['count'] -= count

    def reciprocal_remove (self):
        """Removes results rows for which the n-gram is not present in
        at least one text in each labelled set of texts."""
        logging.info('Removing n-grams that are not attested in all labels')
        labels = set()
        data = {}
        for row in self._rows:
            ngram = row[NGRAM_INDEX]
            label = row[LABEL_INDEX]
            ngram_labels = data.setdefault(ngram, set())
            ngram_labels.add(label)
            data[ngram] = ngram_labels
            labels.add(label)
        new_rows = [row for row in self._rows
                    if data[row[NGRAM_INDEX]] == labels]
        self._rows = new_rows

    def reduce (self):
        """Removes results rows whose n-grams are contained in larger
        n-grams."""
        logging.info('Reducing the n-grams')
        data = {}
        labels = {}
        # Derive a convenient data structure from the rows.
        for row in self._rows:
            filename = row[FILENAME_INDEX]
            labels[filename] = row[LABEL_INDEX]
            text_data = data.setdefault(filename, {})
            text_data[row[NGRAM_INDEX]] = {
                'count': int(row[COUNT_INDEX]),
                'size': int(row[SIZE_INDEX])}
        for filename, text_data in data.items():
            ngrams = list(text_data.keys())
            ngrams.sort(key=lambda ngram: text_data[ngram]['size'],
                        reverse=True)
            for ngram in ngrams:
                if text_data[ngram]['count'] > 0:
                    self._reduce_by_ngram(text_data, ngram)
        # Recreate rows from the modified data structure.
        self._rows = []
        for filename, text_data in data.items():
            for ngram, ngram_data in text_data.items():
                count = ngram_data['count']
                if count > 0:
                    self._rows.append(
                        [ngram, ngram_data['size'], filename, count,
                         labels[filename]])

    def remove_label (self, label):
        logging.info('Removing label "{}"'.format(label))
        new_rows = []
        count = 0
        for row in self._rows:
            if row[LABEL_INDEX] == label:
                count += 1
            else:
                new_rows.append(row)
        logging.info('Removed {} labelled results'.format(count))
        self._rows = new_rows

    def sort (self):
        self._rows.sort(key=lambda row: (
                -int(row[SIZE_INDEX]), row[NGRAM_INDEX], -int(row[COUNT_INDEX]),
                 row[LABEL_INDEX], row[FILENAME_INDEX]))
