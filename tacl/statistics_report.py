"""Module containing the StatisticsReport class."""

import pandas as pd

from . import constants


class StatisticsReport:

    def __init__ (self, matches, counts):
        self._matches = pd.read_csv(matches, encoding='utf-8')
        self._counts = pd.read_csv(counts, encoding='utf-8')

    def csv (self, fh):
        self._stats.to_csv(fh, cols=constants.STATISTICS_FIELDNAMES,
                           encoding='utf-8', index=False)
        return fh

    def generate_statistics (self):
        """Replaces result rows with summary statistics about the results.

        These statistics give the filename, total matching tokens,
        percentage of matching tokens and label for each filename in
        the results.

        """
        counts = self._counts.drop_duplicates(cols=constants.FILENAME_FIELDNAME)
        del counts[constants.SIZE_FIELDNAME]
        del counts[constants.UNIQUE_NGRAMS_FIELDNAME]
        del counts[constants.TOTAL_NGRAMS_FIELDNAME]
        self._matches[constants.COUNT_TOKENS_FIELDNAME] = \
            self._matches[constants.COUNT_FIELDNAME] * \
            self._matches[constants.SIZE_FIELDNAME]
        matching_tokens = pd.DataFrame(self._matches.groupby(
            constants.FILENAME_FIELDNAME)[
                constants.COUNT_TOKENS_FIELDNAME].sum())
        self._stats = pd.merge(counts, matching_tokens, how='outer',
                               left_on=constants.FILENAME_FIELDNAME,
                               right_index=True)
        self._stats = self._stats.fillna(0)
        self._stats[constants.PERCENTAGE_FIELDNAME] = \
            self._stats[constants.COUNT_TOKENS_FIELDNAME] / \
            self._stats[constants.TOTAL_TOKENS_FIELDNAME] * 100
