"""Module containing the Results class."""

import csv
import logging
import os
import re
import tempfile

import pandas as pd

from . import constants
from .decorators import requires_columns
from .exceptions import MalformedResultsError
from .text import FilteredWitnessText, Text


DELETE_FIELDNAME = 'delete'


class Results:

    """Class representing a set of n-gram results.

    Provides methods for manipulating those results in ways that
    maintain the same structure (CSV, same field names). Those methods
    that modify the fields do so in relatively minor ways that often
    allow for the other methods to still operate on the results.

    A method's modifications to the field names, if any, are specified
    in that method's docstring.

    """

    def __init__(self, matches, tokenizer):
        """Initialise a Results object.

        :param matches: results data
        :type matches: either filepath or buffer, or pandas DataFrame
        :param tokenizer: tokenizer used for the n-grams in the results
        :type tokenizer: `Tokenizer`

        """
        self._logger = logging.getLogger(__name__)
        if isinstance(matches, pd.DataFrame):
            self._matches = matches
        else:
            try:
                self._matches = pd.read_csv(matches, encoding='utf-8',
                                            na_filter=False)
            except UnicodeDecodeError:
                raise MalformedResultsError(
                    constants.NON_UTF8_RESULTS_FILE_ERROR.format(matches))
            # Work around a problem with CSV files produced on Windows
            # being read by pandas and creating an empty row for each
            # actual row.
            self._matches = self._matches.dropna(how='all')
        self._tokenizer = tokenizer
        if self._matches.empty:
            self._logger.info('Supplied results file is empty')
        for column in constants.STRING_FIELDNAMES:
            if column in self._matches.columns:
                self._matches = self._matches.astype({column: "string"})

    @requires_columns([constants.NGRAM_FIELDNAME, constants.WORK_FIELDNAME,
                       constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME])
    def add_label_count(self):
        """Adds to each result row a count of the number of occurrences of
        that n-gram across all works within the label.

        This count uses the highest witness count for each work.

        """
        self._logger.info('Adding label count')

        def add_label_count(df):
            # For each n-gram and label pair, we need the maximum count
            # among all witnesses to each work, and then the sum of those
            # across all works.
            work_maxima = df.groupby(constants.WORK_FIELDNAME,
                                     sort=False).max()
            df.loc[:, constants.LABEL_COUNT_FIELDNAME] = work_maxima[
                constants.COUNT_FIELDNAME].sum()
            return df

        if self._matches.empty:
            self._matches[constants.LABEL_COUNT_FIELDNAME] = 0
        else:
            self._matches.loc[:, constants.LABEL_COUNT_FIELDNAME] = 0
            self._matches = self._matches.groupby(
                [constants.LABEL_FIELDNAME, constants.NGRAM_FIELDNAME],
                sort=False).apply(add_label_count)
        self._logger.info('Finished adding label count')

    @requires_columns([constants.NGRAM_FIELDNAME, constants.WORK_FIELDNAME,
                       constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME])
    def add_label_work_count(self):
        """Adds to each result row a count of the number of works within the
        label contain that n-gram.

        This counts works that have at least one witness carrying the
        n-gram.

        This correctly handles cases where an n-gram has only zero
        counts for a given work (possible with zero-fill followed by
        filtering by maximum count).

        """
        self._logger.info('Adding label work count')

        def add_label_text_count(df):
            work_maxima = df.groupby(constants.WORK_FIELDNAME,
                                     sort=False).any()
            df.loc[:, constants.LABEL_WORK_COUNT_FIELDNAME] = work_maxima[
                constants.COUNT_FIELDNAME].sum()
            return df

        if self._matches.empty:
            self._matches[constants.LABEL_WORK_COUNT_FIELDNAME] = 0
        else:
            self._matches.loc[:, constants.LABEL_WORK_COUNT_FIELDNAME] = 0
            self._matches = self._matches.groupby(
                [constants.LABEL_FIELDNAME, constants.NGRAM_FIELDNAME],
                sort=False).apply(add_label_text_count)
        self._logger.info('Finished adding label work count')

    def _annotate_bifurcated_extend_data(self, row, smaller, larger, tokenize,
                                         join):
        """Returns `row` annotated with whether it should be deleted or not.

        An n-gram is marked for deletion if:

        * its label count is 1 and its constituent (n-1)-grams also
          have a label count of 1; or

        * there is a containing (n+1)-gram that has the same label
          count.

        :param row: row of witness n-grams to annotate
        :type row: `pandas.Series`
        :param smaller: rows of (n-1)-grams for this witness
        :type smaller: `pandas.DataFrame`
        :param larger: rows of (n+1)-grams for this witness
        :type larger: `pandas.DataFrame`
        :param tokenize: function to tokenize an n-gram
        :param join: function to join tokens
        :rtype: `pandas.Series`

        """
        lcf = constants.LABEL_COUNT_FIELDNAME
        nf = constants.NGRAM_FIELDNAME
        ngram = row[constants.NGRAM_FIELDNAME]
        label_count = row[constants.LABEL_COUNT_FIELDNAME]
        if label_count == 1 and not smaller.empty:
            # Keep a result with a label count of 1 if its
            # constituents do not also have a count of 1.
            ngram_tokens = tokenize(ngram)
            sub_ngram1 = join(ngram_tokens[:-1])
            sub_ngram2 = join(ngram_tokens[1:])
            pattern = FilteredWitnessText.get_filter_ngrams_pattern(
                [sub_ngram1, sub_ngram2])
            if smaller[smaller[constants.NGRAM_FIELDNAME].str.match(pattern)][
                    constants.LABEL_COUNT_FIELDNAME].max() == 1:
                row[DELETE_FIELDNAME] = True
        elif not larger.empty and larger[larger[nf].str.contains(
                ngram, regex=False)][lcf].max() == label_count:
            # Remove a result if the label count of a containing
            # n-gram is equal to its label count.
            row[DELETE_FIELDNAME] = True
        return row

    @requires_columns([constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME,
                       constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                       constants.LABEL_FIELDNAME])
    def bifurcated_extend(self, corpus, max_size):
        """Replaces the results with those n-grams that contain any of the
        original n-grams, and that represent points at which an n-gram
        is a constituent of multiple larger n-grams with a lower label
        count.

        :param corpus: corpus of works to which results belong
        :type corpus: `Corpus`
        :param max_size: maximum size of n-gram results to include
        :type max_size: `int`

        """
        temp_fd, temp_path = tempfile.mkstemp(text=True)
        try:
            self._prepare_bifurcated_extend_data(corpus, max_size, temp_path,
                                                 temp_fd)
        finally:
            try:
                os.remove(temp_path)
            except OSError as e:
                msg = ('Failed to remove temporary file containing unreduced '
                       'results: {}')
                self._logger.error(msg.format(e))
        self._bifurcated_extend()

    def _bifurcated_extend(self):
        if self._matches.empty:
            return
        self._matches.loc[:, DELETE_FIELDNAME] = False
        tokenize = self._tokenizer.tokenize
        join = self._tokenizer.joiner.join
        new_results = []
        group_cols = [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                      constants.SIZE_FIELDNAME]
        grouped = self._matches.groupby(group_cols, sort=False)
        for (work, siglum, size), group in grouped:
            try:
                smaller_grams = grouped.get_group((work, siglum, size - 1))
            except KeyError:
                smaller_grams = pd.DataFrame()
            try:
                larger_grams = grouped.get_group((work, siglum, size + 1))
            except KeyError:
                larger_grams = pd.DataFrame()
            group = group.apply(self._annotate_bifurcated_extend_data, axis=1,
                                args=(smaller_grams, larger_grams, tokenize,
                                      join))
            new_results.append(group[~group['delete']])
        all_cols = list(constants.QUERY_FIELDNAMES[:]) + \
            [constants.LABEL_COUNT_FIELDNAME, DELETE_FIELDNAME]
        self._matches = pd.concat(new_results, ignore_index=True,
                                  sort=False).reindex(columns=all_cols)
        del self._matches[DELETE_FIELDNAME]

    @requires_columns([constants.NGRAM_FIELDNAME, constants.WORK_FIELDNAME,
                       constants.SIGLUM_FIELDNAME, constants.COUNT_FIELDNAME])
    def collapse_witnesses(self):
        """Groups together witnesses for the same n-gram and work that has the
        same count, and outputs a single row for each group.

        This output replaces the siglum field with a sigla field that
        provides a comma separated list of the witness sigla. Due to
        this, it is not necessarily possible to run other Results
        methods on results that have had their witnesses collapsed.

        """
        # In order to allow for additional columns to be present in
        # the input data (such as label count), copy the siglum
        # information into a new final column, then put the sigla
        # information into the siglum field and finally rename it.
        #
        # This means that in merge_sigla below, the column names are
        # reversed from what would be expected.
        if self._matches.empty:
            self._matches.rename(columns={constants.SIGLUM_FIELDNAME:
                                          constants.SIGLA_FIELDNAME},
                                 inplace=True)
            return
        self._matches.loc[:, constants.SIGLA_FIELDNAME] = \
            self._matches[constants.SIGLUM_FIELDNAME]
        # This code makes the not unwarranted assumption that the same
        # n-gram means the same size and that the same work means the
        # same label.
        grouped = self._matches.groupby(
            [constants.WORK_FIELDNAME, constants.NGRAM_FIELDNAME,
             constants.COUNT_FIELDNAME], sort=False)

        def merge_sigla(df):
            # Take the first result row; only the siglum should differ
            # between them, and there may only be one row.
            merged = df[0:1]
            sigla = list(df[constants.SIGLA_FIELDNAME])
            sigla.sort()
            merged[constants.SIGLUM_FIELDNAME] = ', '.join(sigla)
            return merged

        self._matches = grouped.apply(merge_sigla)
        del self._matches[constants.SIGLA_FIELDNAME]
        self._matches.rename(columns={constants.SIGLUM_FIELDNAME:
                                      constants.SIGLA_FIELDNAME},
                             inplace=True)

    def csv(self, fh):
        """Writes the results data to `fh` in CSV format and returns `fh`.

        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        self._matches.to_csv(fh, encoding='utf-8', float_format='%d',
                             index=False)
        return fh

    @requires_columns([constants.NGRAM_FIELDNAME, constants.WORK_FIELDNAME,
                       constants.SIGLUM_FIELDNAME, constants.COUNT_FIELDNAME,
                       constants.LABEL_FIELDNAME])
    def denormalise(self, corpus, mapping):
        """Replaces n-grams with their denormalised forms.

        Keeps the normalised form in a new column.

        """
        group_cols = [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME]
        fieldnames = list(constants.QUERY_FIELDNAMES) + [
            constants.NORMALISED_FIELDNAME]

        def denormalise_ngram(row, text, work, siglum):
            """Return result rows containing all of the denormalised n-grams
            derived from the normalised n-gram in `row`.

            Note that it is possible for no rows to be returned, if
            the mapping contains multi-token entries, because the
            n-gram in `row` may not include the full entry, and thus
            not denormalise.

            :param row: result row to generate denormalised result rows from
            :type row: `tuple`
            :param text: text of the unnormalised witness (in the form
                         of tokens and separators only)
            :type text: `str`
            :param work: name of work
            :type work: `str`
            :param siglum: siglum of witness
            :type siglum: `str`
            :rtype: `list` of `dict`

            """
            normalised_ngram = row[0]
            label = row[5]
            denormalised_ngrams = mapping.denormalise(normalised_ngram)
            rows = []
            for ngram in denormalised_ngrams:
                count = len(re.findall(r'(?={})'.format(re.escape(ngram)),
                                       text))
                if count:
                    size = len(self._tokenizer.tokenize(ngram))
                    rows.append({
                        constants.NGRAM_FIELDNAME: ngram,
                        constants.SIZE_FIELDNAME: size,
                        constants.WORK_FIELDNAME: work,
                        constants.SIGLUM_FIELDNAME: siglum,
                        constants.COUNT_FIELDNAME: count,
                        constants.LABEL_FIELDNAME: label,
                        constants.NORMALISED_FIELDNAME: normalised_ngram
                    })
            return rows

        def denormalise_witness_ngrams(group):
            work, siglum = group.name
            witness = corpus.get_witness(work, siglum)
            text = witness.get_token_content()
            rows = []
            for row in group.itertuples(index=False, name=None):
                rows.extend(denormalise_ngram(row, text, work, siglum))
            return pd.DataFrame(rows, columns=fieldnames)

        matches = self._matches.groupby(group_cols, sort=False).apply(
            denormalise_witness_ngrams)
        self._matches = matches

    @requires_columns([constants.NGRAM_FIELDNAME])
    def excise(self, ngram):
        """Removes all rows whose n-gram contains `ngram`.

        This operation uses simple string containment matching. For
        tokens that consist of multiple characters, this means that
        `ngram` may be part of one or two tokens; eg, "he m" would
        match on "she may".

        :param ngram: n-gram to remove containing n-gram rows by
        :type ngram: `str`

        """
        self._logger.info('Excising results containing "{}"'.format(ngram))
        if not ngram:
            return
        self._matches = self._matches[~self._matches[
            constants.NGRAM_FIELDNAME].str.contains(ngram, regex=False)]

    @requires_columns([constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME,
                       constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                       constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME])
    def extend(self, corpus):
        """Adds rows for all longer forms of n-grams in the results that are
        present in the witnesses.

        This works with both diff and intersect results.

        :param corpus: corpus of works to which results belong
        :type corpus: `Corpus`

        """
        self._logger.info('Extending results')
        if self._matches.empty:
            return
        highest_n = self._matches[constants.SIZE_FIELDNAME].max()
        if highest_n == 1:
            self._logger.warning(
                'Extending results that contain only 1-grams is unsupported; '
                'the original results will be used')
            return
        # Determine if we are dealing with diff or intersect
        # results. In the latter case, we need to perform a reciprocal
        # remove as the final stage (since extended n-grams may exist
        # in works from more than one label). This test will think
        # that intersect results that have had all but one label
        # removed are difference results, which will cause the results
        # to be potentially incorrect.
        is_intersect = self._is_intersect_results(self._matches)
        self._extend(corpus, highest_n, is_intersect)

    def _extend(self, corpus, highest_n, is_intersect):
        def extend_ngrams(df, corpus, current_n):
            next_n = current_n + 1
            first_row = df.iloc[0]
            work = first_row[constants.WORK_FIELDNAME]
            siglum = first_row[constants.SIGLUM_FIELDNAME]
            label = first_row[constants.LABEL_FIELDNAME]
            text = corpus.get_witness(work, siglum)
            text_ngrams = next(text.get_ngrams(next_n, next_n))[1]
            max_length_ngrams = list(
                df[df[constants.SIZE_FIELDNAME] == current_n][
                    constants.NGRAM_FIELDNAME])
            ngrams = [tuple(self._tokenizer.tokenize(ngram))
                      for ngram in max_length_ngrams]
            extra_rows = []
            for base_ngram in ngrams:
                for extender_ngram in ngrams:
                    if base_ngram[1:] == extender_ngram[:-1]:
                        extended_ngram = self._tokenizer.joiner.join(
                            base_ngram + extender_ngram[-1:])
                        if extended_ngram in text_ngrams:
                            extra_rows.append({
                                constants.NGRAM_FIELDNAME: extended_ngram,
                                constants.SIZE_FIELDNAME: next_n,
                                constants.WORK_FIELDNAME: work,
                                constants.SIGLUM_FIELDNAME: siglum,
                                constants.COUNT_FIELDNAME: text_ngrams[
                                    extended_ngram],
                                constants.LABEL_FIELDNAME: label,
                            })
            extended_matches = pd.DataFrame(extra_rows)
            return pd.concat([df, extended_matches], ignore_index=True,
                             sort=False)

        num_rows = self._matches.shape[0]
        grouping_cols = [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                         constants.LABEL_FIELDNAME]
        self._logger.info("Extending to {}-grams".format(highest_n + 1))
        self._matches = self._matches.groupby(
            grouping_cols, as_index=False, group_keys=False, sort=False).apply(
                extend_ngrams, corpus=corpus, current_n=highest_n)
        if self._matches.shape[0] > num_rows:
            self._extend(corpus, highest_n + 1, is_intersect)
        else:
            if is_intersect:
                self._matches = self._reciprocal_remove(self._matches)
            self._matches.reset_index(drop=True, inplace=True)

    def _generate_filter_ngrams(self, data, min_size):
        """Returns the n-grams in `data` that do not contain any other n-gram
        in `data`.

        :param data: n-gram results data
        :type data: `pandas.DataFrame`
        :param min_size: minimum n-gram size in `data`
        :type min_size: `int`
        :rtype: `list` of `str`

        """
        max_size = data[constants.SIZE_FIELDNAME].max()
        kept_ngrams = list(data[data[constants.SIZE_FIELDNAME] == min_size][
            constants.NGRAM_FIELDNAME])
        for size in range(min_size + 1, max_size + 1):
            pattern = FilteredWitnessText.get_filter_ngrams_pattern(
                kept_ngrams)
            potential_ngrams = list(data[data[constants.SIZE_FIELDNAME] ==
                                         size][constants.NGRAM_FIELDNAME])
            kept_ngrams.extend([ngram for ngram in potential_ngrams if
                                pattern.search(ngram) is None])
        return kept_ngrams

    def _generate_substrings(self, ngram, size):
        """Returns a list of all substrings of `ngram`.

        :param ngram: n-gram to generate substrings of
        :type ngram: `str`
        :param size: size of `ngram`
        :type size: `int`
        :rtype: `list`

        """
        text = Text(ngram, self._tokenizer)
        substrings = []
        for sub_size, ngrams in text.get_ngrams(1, size - 1):
            for sub_ngram, count in ngrams.items():
                substrings.extend([sub_ngram] * count)
        return substrings

    def get_raw_data(self):
        """Returns the underlying data as a `pandas.DataFrame`.

        :rtype: `pandas.DataFrame`

        """
        return self._matches

    @requires_columns([constants.NGRAM_FIELDNAME, constants.WORK_FIELDNAME,
                       constants.SIGLUM_FIELDNAME, constants.COUNT_FIELDNAME,
                       constants.LABEL_FIELDNAME])
    def group_by_ngram(self, labels):
        """Groups result rows by n-gram and label, providing a single summary
        field giving the range of occurrences across each work's
        witnesses. Results are sorted by n-gram then by label (in the
        order given in `labels`).

        :param labels: labels to order on
        :type labels: `list` of `str`

        """
        if self._matches.empty:
            # Ensure that the right columns are used, even though the
            # results are empty.
            self._matches = pd.DataFrame(
                {}, columns=[
                    constants.NGRAM_FIELDNAME,
                    constants.SIZE_FIELDNAME,
                    constants.LABEL_FIELDNAME,
                    constants.WORK_COUNTS_FIELDNAME])
            return
        label_order_col = 'label order'

        def work_summary(group):
            match = group.iloc[0]
            work = match[constants.WORK_FIELDNAME]
            minimum = group[constants.COUNT_FIELDNAME].min()
            maximum = group[constants.COUNT_FIELDNAME].max()
            if minimum == maximum:
                work_count = '{}({})'.format(work, minimum)
            else:
                work_count = '{}({}-{})'.format(work, minimum, maximum)
            match['work count'] = work_count
            return match

        def ngram_label_summary(group):
            match = group.iloc[0]
            summary = group.groupby(constants.WORK_FIELDNAME).apply(
                work_summary)
            work_counts = ', '.join(list(summary['work count']))
            match[constants.WORK_COUNTS_FIELDNAME] = work_counts
            return match

        def add_label_order(row, labels):
            row[label_order_col] = labels.index(row[constants.LABEL_FIELDNAME])
            return row

        group_cols = [constants.NGRAM_FIELDNAME, constants.LABEL_FIELDNAME]
        matches = self._matches.groupby(group_cols, sort=False).apply(
            ngram_label_summary)
        del matches[constants.WORK_FIELDNAME]
        del matches[constants.SIGLUM_FIELDNAME]
        del matches[constants.COUNT_FIELDNAME]
        matches = matches.apply(add_label_order, axis=1, args=(labels,))
        matches.reset_index(drop=True, inplace=True)
        matches.sort_values(by=[constants.NGRAM_FIELDNAME, label_order_col],
                            ascending=True, inplace=True)
        del matches[label_order_col]
        self._matches = matches

    @requires_columns([constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME,
                       constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                       constants.COUNT_FIELDNAME])
    def group_by_witness(self):
        """Groups results by witness, providing a single summary field giving
        the n-grams found in it, a count of their number, and the count of
        their combined occurrences."""
        if self._matches.empty:
            # Ensure that the right columns are used, even though the
            # results are empty.
            self._matches = pd.DataFrame(
                {}, columns=[constants.WORK_FIELDNAME,
                             constants.SIGLUM_FIELDNAME,
                             constants.LABEL_FIELDNAME,
                             constants.NGRAMS_FIELDNAME,
                             constants.NUMBER_FIELDNAME,
                             constants.TOTAL_COUNT_FIELDNAME])
            return

        def witness_summary(group):
            matches = group.sort_values(by=[constants.NGRAM_FIELDNAME],
                                        ascending=[True])
            match = matches.iloc[0]
            ngrams = ', '.join(list(matches[constants.NGRAM_FIELDNAME]))
            match[constants.NGRAMS_FIELDNAME] = ngrams
            match[constants.NUMBER_FIELDNAME] = len(matches)
            match[constants.TOTAL_COUNT_FIELDNAME] = matches[
                constants.COUNT_FIELDNAME].sum()
            return match

        group_cols = [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME]
        # Remove zero-count results.
        self._matches = self._matches[
            self._matches[constants.COUNT_FIELDNAME] != 0]
        self._matches = self._matches.groupby(group_cols, sort=False).apply(
            witness_summary)
        del self._matches[constants.NGRAM_FIELDNAME]
        del self._matches[constants.SIZE_FIELDNAME]
        del self._matches[constants.COUNT_FIELDNAME]

    @staticmethod
    def _is_intersect_results(results):
        """Returns True if all of the n-grams in `results` exist in all of
        `results`'s labels, False otherwise.

        If there is only a single label, return False.

        :param results: results to analyze
        :type results: `pandas.DataFrame`
        :rtype: `bool`

        """
        num_labels = results[constants.LABEL_FIELDNAME].nunique()
        if num_labels == 1:
            return False
        cols = [constants.NGRAM_FIELDNAME, constants.LABEL_FIELDNAME]
        data = results[cols].drop_duplicates()
        counts = data.groupby(constants.NGRAM_FIELDNAME).count()
        return counts[counts[constants.LABEL_FIELDNAME] != num_labels].empty

    def _prepare_bifurcated_extend_data(self, corpus, max_size, temp_path,
                                        temp_fd):
        # It might be wondered why this whole derivation of n-grams
        # anew from the source text is required, when an extended set
        # of results could just be passed through to the final
        # filtering process.
        #
        # The answer is that, for diff results, the filtering done by
        # diff-reduce can remove many n-grams that are picked up in
        # this process, and which may well prove important in the
        # context of a bifurcated extend.
        self._matches.sort_values(by=[constants.SIZE_FIELDNAME],
                                  ascending=True, inplace=True)
        group_cols = [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                      constants.LABEL_FIELDNAME]
        # Output a CSV file containing the possible n-grams to include
        # in the final output.
        self._logger.debug('Writing filtered n-grams to temporary CSV file '
                           'at {}'.format(temp_path))
        with open(temp_fd, 'w', encoding='utf-8', newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(constants.QUERY_FIELDNAMES)
            for (text, siglum, label), group in self._matches.groupby(
                    group_cols, sort=False):
                min_size = group[constants.SIZE_FIELDNAME].min()
                filter_ngrams = self._generate_filter_ngrams(group, min_size)
                witness = corpus.get_witness(text, siglum, FilteredWitnessText)
                for size, ngrams in witness.get_ngrams(min_size, max_size,
                                                       filter_ngrams):
                    rows = [[ngram, size, text, siglum, count, label] for
                            ngram, count in ngrams.items()]
                    writer.writerows(rows)
        self._matches = pd.read_csv(temp_path, encoding='utf-8',
                                    na_filter=False)
        self.add_label_count()

    @requires_columns([constants.NGRAM_FIELDNAME])
    def prune_by_ngram(self, ngrams):
        """Removes results rows whose n-gram is in `ngrams`.

        :param ngrams: n-grams to remove
        :type ngrams: `list` of `str`

        """
        self._logger.info('Pruning results by n-gram')
        self._matches = self._matches[
            ~self._matches[constants.NGRAM_FIELDNAME].isin(ngrams)]

    @requires_columns([constants.NGRAM_FIELDNAME, constants.WORK_FIELDNAME,
                       constants.COUNT_FIELDNAME])
    def prune_by_ngram_count(self, minimum=None, maximum=None, label=None):
        """Removes results rows whose total n-gram count (across all
        works bearing this n-gram) is outside the range specified by
        `minimum` and `maximum`.

        For each text, the count used as part of the sum across all
        works is the maximum count across the witnesses for that work.

        If `label` is specified, the works checked are restricted to
        those associated with `label`.

        :param minimum: minimum n-gram count
        :type minimum: `int`
        :param maximum: maximum n-gram count
        :type maximum: `int`
        :param label: optional label to restrict requirement to
        :type label: `str`

        """
        self._logger.info('Pruning results by n-gram count')

        def calculate_total(group):
            work_grouped = group.groupby(constants.WORK_FIELDNAME, sort=False)
            total_count = work_grouped[constants.COUNT_FIELDNAME].max().sum()
            group['total_count'] = pd.Series([total_count] * len(group.index),
                                             index=group.index)
            return group

        # self._matches may be empty, in which case not only is there
        # no point trying to do the pruning, but it will raise an
        # exception due to referencing the column 'total_count' which
        # won't have been added. Therefore just return immediately.
        if self._matches.empty:
            return
        matches = self._matches
        if label is not None:
            matches = matches[matches[constants.LABEL_FIELDNAME] == label]
        matches = matches.groupby(
            constants.NGRAM_FIELDNAME, sort=False).apply(calculate_total)
        ngrams = None
        if minimum:
            ngrams = matches[matches['total_count'] >= minimum][
                constants.NGRAM_FIELDNAME].unique()
        if maximum:
            max_ngrams = matches[matches['total_count'] <= maximum][
                constants.NGRAM_FIELDNAME].unique()
            if ngrams is None:
                ngrams = max_ngrams
            else:
                ngrams = list(set(ngrams) & set(max_ngrams))
        self._matches = self._matches[
            self._matches[constants.NGRAM_FIELDNAME].isin(ngrams)]

    @requires_columns([constants.NGRAM_FIELDNAME, constants.COUNT_FIELDNAME])
    def prune_by_ngram_count_per_work(self, minimum=None, maximum=None,
                                      label=None):
        """Removes results rows if the n-gram count for all works bearing that
        n-gram is outside the range specified by `minimum` and
        `maximum`.

        That is, if a single witness of a single work has an n-gram
        count that falls within the specified range, all result rows
        for that n-gram are kept.

        If `label` is specified, the works checked are restricted to
        those associated with `label`.

        :param minimum: minimum n-gram count
        :type minimum: `int`
        :param maximum: maximum n-gram count
        :type maximum: `int`
        :param label: optional label to restrict requirement to
        :type label: `str`

        """
        self._logger.info('Pruning results by n-gram count per work')
        matches = self._matches
        keep_ngrams = matches[constants.NGRAM_FIELDNAME].unique()
        if label is not None:
            matches = matches[matches[constants.LABEL_FIELDNAME] == label]
        if minimum and maximum:
            keep_ngrams = matches[
                (matches[constants.COUNT_FIELDNAME] >= minimum) &
                (matches[constants.COUNT_FIELDNAME] <= maximum)][
                    constants.NGRAM_FIELDNAME].unique()
        elif minimum:
            keep_ngrams = matches[
                matches[constants.COUNT_FIELDNAME] >= minimum][
                    constants.NGRAM_FIELDNAME].unique()
        elif maximum:
            keep_ngrams = matches[
                self._matches[constants.COUNT_FIELDNAME] <= maximum][
                    constants.NGRAM_FIELDNAME].unique()
        self._matches = self._matches[self._matches[
            constants.NGRAM_FIELDNAME].isin(keep_ngrams)]

    @requires_columns([constants.SIZE_FIELDNAME])
    def prune_by_ngram_size(self, minimum=None, maximum=None):
        """Removes results rows whose n-gram size is outside the
        range specified by `minimum` and `maximum`.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`

        """
        self._logger.info('Pruning results by n-gram size')
        if minimum:
            self._matches = self._matches[
                self._matches[constants.SIZE_FIELDNAME] >= minimum]
        if maximum:
            self._matches = self._matches[
                self._matches[constants.SIZE_FIELDNAME] <= maximum]

    @requires_columns([constants.NGRAM_FIELDNAME, constants.WORK_FIELDNAME,
                       constants.COUNT_FIELDNAME])
    def prune_by_work_count(self, minimum=None, maximum=None, label=None):
        """Removes results rows for n-grams that are not attested in a
        number of works in the range specified by `minimum` and
        `maximum`.

        Work here encompasses all witnesses, so that the same n-gram
        appearing in multiple witnesses of the same work are counted
        as a single work.

        If `label` is specified, the works counted are restricted to
        those associated with `label`.

        :param minimum: minimum number of works
        :type minimum: `int`
        :param maximum: maximum number of works
        :type maximum: `int`
        :param label: optional label to restrict requirement to
        :type label: `str`

        """
        self._logger.info('Pruning results by work count')
        count_fieldname = 'tmp_count'
        matches = self._matches
        if label is not None:
            matches = matches[matches[constants.LABEL_FIELDNAME] == label]
        filtered = matches[matches[constants.COUNT_FIELDNAME] > 0]
        grouped = filtered.groupby(constants.NGRAM_FIELDNAME, sort=False)
        counts = pd.DataFrame(grouped[constants.WORK_FIELDNAME].nunique())
        counts.rename(columns={constants.WORK_FIELDNAME: count_fieldname},
                      inplace=True)
        if minimum:
            counts = counts[counts[count_fieldname] >= minimum]
        if maximum:
            counts = counts[counts[count_fieldname] <= maximum]
        self._matches = pd.merge(self._matches, counts,
                                 left_on=constants.NGRAM_FIELDNAME,
                                 right_index=True)
        del self._matches[count_fieldname]

    @requires_columns([constants.NGRAM_FIELDNAME, constants.COUNT_FIELDNAME,
                       constants.LABEL_FIELDNAME])
    def reciprocal_remove(self):
        """Removes results rows for which the n-gram is not present in
        at least one text in each labelled set of texts."""
        self._logger.info(
            'Removing n-grams that are not attested in all labels')
        self._matches = self._reciprocal_remove(self._matches)

    def _reciprocal_remove(self, matches):
        number_labels = matches[constants.LABEL_FIELDNAME].nunique()
        if number_labels == 1:
            return matches
        filtered = matches[matches[constants.COUNT_FIELDNAME] > 0]
        grouped = filtered.groupby(constants.NGRAM_FIELDNAME, sort=False)
        return grouped.filter(
            lambda x: x[constants.LABEL_FIELDNAME].nunique() == number_labels)

    @requires_columns([constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME,
                       constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                       constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME])
    def reduce(self):
        """Removes results rows whose n-grams are contained in larger
        n-grams."""
        self._logger.info('Reducing the n-grams')
        # This does not make use of any pandas functionality; it
        # probably could, and if so ought to.
        data = {}
        labels = {}
        # Derive a convenient data structure from the rows.
        for row_index, row in self._matches.iterrows():
            work = row[constants.WORK_FIELDNAME]
            siglum = row[constants.SIGLUM_FIELDNAME]
            labels[work] = row[constants.LABEL_FIELDNAME]
            witness_data = data.setdefault((work, siglum), {})
            witness_data[row[constants.NGRAM_FIELDNAME]] = {
                'count': int(row[constants.COUNT_FIELDNAME]),
                'size': int(row[constants.SIZE_FIELDNAME])}
        for witness_data in data.values():
            ngrams = list(witness_data.keys())
            ngrams.sort(key=lambda ngram: witness_data[ngram]['size'],
                        reverse=True)
            for ngram in ngrams:
                if witness_data[ngram]['count'] > 0:
                    self._reduce_by_ngram(witness_data, ngram)
        # Recreate rows from the modified data structure.
        rows = []
        for (work, siglum), witness_data in data.items():
            for ngram, ngram_data in witness_data.items():
                count = ngram_data['count']
                if count > 0:
                    rows.append(
                        {constants.NGRAM_FIELDNAME: ngram,
                         constants.SIZE_FIELDNAME: ngram_data['size'],
                         constants.WORK_FIELDNAME: work,
                         constants.SIGLUM_FIELDNAME: siglum,
                         constants.COUNT_FIELDNAME: count,
                         constants.LABEL_FIELDNAME: labels[work]})
        self._matches = pd.DataFrame(
            rows, columns=constants.QUERY_FIELDNAMES)

    def _reduce_by_ngram(self, data, ngram):
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

    @requires_columns([constants.WORK_FIELDNAME, constants.LABEL_FIELDNAME])
    def relabel(self, catalogue):
        """Relabels results rows according to `catalogue`.

        A row whose work is labelled in the catalogue will have its
        label set to the label in the catalogue. Rows whose works are
        not labelled in the catalogue will be unchanged.

        :param catalogue: mapping of work names to labels
        :type catalogue: `Catalogue`

        """
        for work, label in catalogue.items():
            self._matches.loc[self._matches[constants.WORK_FIELDNAME] == work,
                              constants.LABEL_FIELDNAME] = label

    @requires_columns([constants.LABEL_FIELDNAME])
    def remove_label(self, label):
        """Removes all results rows associated with `label`.

        :param label: label to filter results on
        :type label: `str`

        """
        self._logger.info('Removing label "{}"'.format(label))
        count = self._matches[constants.LABEL_FIELDNAME].value_counts().get(
            label, 0)
        self._matches = self._matches[
            self._matches[constants.LABEL_FIELDNAME] != label]
        self._logger.info('Removed {} labelled results'.format(count))

    @requires_columns([constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME,
                       constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                       constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME])
    def sort(self):
        """Sorts all results rows.

        Sorts by: size (descending), n-gram, count (descending), label,
        text name, siglum.

        """
        self._matches.sort_values(
            by=[constants.SIZE_FIELDNAME, constants.NGRAM_FIELDNAME,
                constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME,
                constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME],
            ascending=[False, True, False, True, True, True], inplace=True)

    @requires_columns([constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME,
                       constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
                       constants.LABEL_FIELDNAME])
    def zero_fill(self, corpus):
        """Adds rows to the results to ensure that, for every n-gram that is
        attested in at least one witness, every witness for that text
        has a row, with added rows having a count of zero.

        :param corpus: corpus containing the texts appearing in the results
        :type corpus: `Corpus`

        """
        self._logger.info('Zero-filling results')
        zero_rows = []
        work_sigla = {}
        grouping_cols = [constants.LABEL_FIELDNAME, constants.NGRAM_FIELDNAME,
                         constants.SIZE_FIELDNAME, constants.WORK_FIELDNAME]
        grouped = self._matches.groupby(grouping_cols, sort=False)
        for (label, ngram, size, work), group in grouped:
            row_data = {
                constants.NGRAM_FIELDNAME: ngram,
                constants.LABEL_FIELDNAME: label,
                constants.SIZE_FIELDNAME: size,
                constants.COUNT_FIELDNAME: 0,
                constants.WORK_FIELDNAME: work,
            }
            if work not in work_sigla:
                work_sigla[work] = corpus.get_sigla(work)
            for siglum in work_sigla[work]:
                if group[group[constants.SIGLUM_FIELDNAME] == siglum].empty:
                    row_data[constants.SIGLUM_FIELDNAME] = siglum
                    zero_rows.append(row_data)
        zero_df = pd.DataFrame(zero_rows, columns=constants.QUERY_FIELDNAMES)
        self._matches = pd.concat([self._matches, zero_df], ignore_index=True,
                                  sort=False)
