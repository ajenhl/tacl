import csv
import io
import logging


COUNT_INDEX = 3
FILENAME_INDEX = 2
LABEL_INDEX = 4
NGRAM_INDEX = 0
SIZE_INDEX = 1


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

    def prune (self, minimum=None, maximum=None):
        pass

    def _reduce_ngram (self, data, ngram, size):
        """Lowers the counts of `ngram` in `data` if it forms part of
        a larger n-gram.

        Modifies `data` in place.

        :param data: row data dictionary
        :type data: `dict`
        :param ngram: n-gram being reduced
        :type ngram: `str`
        :param size: size of `ngram`
        :type size: `int`

        """
        larger_size = size + 1
        for larger_ngram in data.get(larger_size, []):
            if ngram in larger_ngram:
                for filename, count in data[larger_size][larger_ngram].items():
                    data[size][ngram][filename] -= count

    def reduce (self):
        """Removes from `ngrams_data` those n-grams that are contained
        in larger n-grams."""
        logging.info('Reducing the n-grams')
        data = {}
        labels = {}
        # Derive a convenient data structure from the rows.
        for row in self._rows:
            size = data.setdefault(int(row[SIZE_INDEX]), {})
            ngram = size.setdefault(row[NGRAM_INDEX], {})
            filename = row[FILENAME_INDEX]
            ngram[filename] = int(row[COUNT_INDEX])
            labels[filename] = row[LABEL_INDEX]
        sizes = list(data.keys())
        sizes.sort()
        for size in sizes:
            for ngram in data[size]:
                self._reduce_ngram(data, ngram, size)
        # Recreate rows from the modified data structure.
        self._rows = []
        for size, ngrams in data.items():
            for ngram, filenames in ngrams.items():
                for filename, count in filenames.items():
                    if count > 0:
                        self._rows.append(
                            [ngram, size, filename, count, labels[filename]])

    def remove_label (self, label):
        logging.info('Removing label "{}"'.format(label))
        new_rows = []
        count = 0
        for row in self._rows:
            if row[LABEL_INDEX] == label:
                count += 1
            else:
                new_rows.append(row)
        logging.info('Removed {} results'.format(count))
        self._rows = new_rows

    def sort (self):
        self._rows.sort(key=lambda row: (
                -int(row[SIZE_INDEX]), row[NGRAM_INDEX], -int(row[COUNT_INDEX]),
                 row[LABEL_INDEX], row[FILENAME_INDEX]))
