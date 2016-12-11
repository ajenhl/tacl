"""Module containing the StatisticsReport class."""

import re

import pandas as pd

from . import constants
from .text import Text


class StatisticsReport:

    def __init__(self, corpus, tokenizer, matches):
        self._corpus = corpus
        self._tokenizer = tokenizer
        self._matches = pd.read_csv(matches, encoding='utf-8', na_filter=False)
        self._stats = pd.DataFrame()

    def csv(self, fh):
        """Writes the report data to `fh` in CSV format and returns it.

        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        self._stats.to_csv(fh, encoding='utf-8', index=False)
        return fh

    def generate_statistics(self):
        """Replaces result rows with summary statistics about the results.

        These statistics give the filename, total matching tokens,
        percentage of matching tokens and label for each witness in
        the results.

        """
        matches = self._matches
        witness_fields = [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                          constants.LABEL_FIELDNAME]
        witnesses = matches[witness_fields].drop_duplicates()
        rows = []
        for index, (work, siglum, label) in witnesses.iterrows():
            witness = self._corpus.get_witness(work, siglum)
            witness_matches = matches[
                (matches[constants.WORK_FIELDNAME] == work) &
                (matches[constants.SIGLUM_FIELDNAME] == siglum)]
            total_count, matching_count = self._process_witness(
                witness, witness_matches)
            percentage = matching_count / total_count * 100
            rows.append({constants.WORK_FIELDNAME: work,
                         constants.SIGLUM_FIELDNAME: siglum,
                         constants.COUNT_TOKENS_FIELDNAME: matching_count,
                         constants.TOTAL_TOKENS_FIELDNAME: total_count,
                         constants.PERCENTAGE_FIELDNAME: percentage,
                         constants.LABEL_FIELDNAME: label})
        self._stats = pd.DataFrame(
            rows, columns=constants.STATISTICS_FIELDNAMES)

    def _generate_text_from_slices(self, full_text, slices):
        """Return a single string consisting of the parts specified in
        `slices` joined together by the tokenizer's joining string.

        :param full_text: the text to be sliced
        :type full_text: `str`
        :param slices: list of slice indices to apply to `full_text`
        :type slices: `list` of `list`\s
        :rtype: `str`

        """
        sliced_text = []
        for start, end in slices:
            sliced_text.append(full_text[start:end])
        return self._tokenizer.joiner.join(sliced_text)

    @staticmethod
    def _merge_slices(match_slices):
        """Return a list of slice indices lists derived from `match_slices`
        with no overlaps."""
        # Sort by earliest range, then by largest range.
        match_slices.sort(key=lambda x: (x[0], -x[1]))
        merged_slices = [match_slices.pop(0)]
        for slice_indices in match_slices:
            last_end = merged_slices[-1][1]
            if slice_indices[0] <= last_end:
                if slice_indices[1] > last_end:
                    merged_slices[-1][1] = slice_indices[1]
            else:
                merged_slices.append(slice_indices)
        return merged_slices

    def _process_witness(self, witness, matches):
        """Return the counts of total tokens and matching tokens in `witness`.

        :param witness: witness text
        :type witness: `tacl.WitnessText`
        :param matches: n-gram matches
        :type matches: `pandas.DataFrame`
        :rtype: `tuple` of `int`

        """
        # In order to provide a correct count of matched tokens,
        # avoiding the twin dangers of counting the same token
        # multiple times due to being part of multiple n-grams (which
        # can happen even in reduced results) and not counting tokens
        # due to an n-gram overlapping with itself or another n-gram,
        # a bit of work is required.
        #
        # Using regular expressions, get the slice indices for all
        # matches (including overlapping ones) for all matching
        # n-grams. Merge these slices together (without overlap) and
        # create a Text using that text, which can then be tokenised
        # and the tokens counted.
        tokens = witness.get_tokens()
        full_text = witness.get_token_content()
        fields = [constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME]
        match_slices = []
        for index, (ngram, size) in matches[fields].iterrows():
            pattern = re.compile(re.escape(ngram))
            # Because the same n-gram may overlap itself ("heh" in the
            # string "heheh"), re.findall cannot be used.
            start = 0
            while True:
                match = pattern.search(full_text, start)
                if match is None:
                    break
                match_slices.append([match.start(), match.end()])
                start = match.start() + 1
        merged_slices = self._merge_slices(match_slices)
        match_content = self._generate_text_from_slices(
            full_text, merged_slices)
        match_text = Text(match_content, self._tokenizer)
        return len(tokens), len(match_text.get_tokens())
