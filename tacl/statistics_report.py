"""Module containing the StatisticsReport class."""

import csv

from . import constants, Report


class StatisticsReport (Report):

    def __init__ (self, results, counts):
        super().__init__(results)
        self._count_rows = [row for row in csv.DictReader(counts)]

    def csv (self, fh):
        return self._csv(fh, constants.STATISTICS_FIELDNAMES)

    def generate_statistics (self):
        """Replaces result rows with summary statistics about the results.

        These statistics give the filename, total matching tokens,
        percentage of matching tokens and label for each filename in
        the results.

        """
        stats = {}
        for row in self._count_rows:
            filename = row[constants.FILENAME_FIELDNAME]
            if filename not in stats:
                length = int(row[constants.TOTAL_NGRAMS_FIELDNAME]) + \
                         int(row[constants.SIZE_FIELDNAME]) - 1
                stats[filename] = {'label': row[constants.LABEL_FIELDNAME],
                                   'length': length, 'total_count': 0}
        for row in self._rows:
            filename = row[constants.FILENAME_FIELDNAME]
            token_count = int(row[constants.COUNT_FIELDNAME]) * \
                          int(row[constants.SIZE_FIELDNAME])
            # If the counts data does not match with the results data,
            # the following may raise a KeyError.
            stats[filename]['total_count'] += token_count
        self._rows = []
        for filename, data in stats.items():
            if data['length'] == 0:
                percentage = 0
            else:
                percentage = data['total_count'] / data['length'] * 100
            row = {constants.FILENAME_FIELDNAME: filename,
                   constants.COUNT_TOKENS_FIELDNAME: str(data['total_count']),
                   constants.TOTAL_TOKENS_FIELDNAME: str(data['length']),
                   constants.PERCENTAGE_FIELDNAME: str(percentage),
                   constants.LABEL_FIELDNAME: data['label']}
            self._rows.append(row)
