"""Module containing the Report class."""

import logging
import re

import pandas as pd

from . import constants
from .text import BaseText


class Report:

    def __init__ (self, matches, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._matches = pd.read_csv(matches, encoding='utf-8', na_filter=False)
        # Work around a problem with CSV files produced on Windows
        # being read by pandas and creating an empty row for each
        # actual row.
        self._matches = self._matches.dropna(how='all')
        self._tokenizer = tokenizer

    def csv (self, fh):
        """Writes the report data to `fh` in CSV format and returns it.

        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        self._matches.to_csv(fh, encoding='utf-8', float_format='%d',
                             index=False)
        return fh

    def extend (self, corpus):
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
        # in texts from more than one label). This test will think
        # that intersect results that have had all but one label
        # removed are difference results, which will cause the results
        # to be potentially incorrect.
        is_intersect = self._is_intersect_results(self._matches)
        # Supply the extender with only matches on the largest
        # n-grams.
        matches = self._matches[
            self._matches[constants.SIZE_FIELDNAME] == highest_n]
        extended_matches = pd.DataFrame()
        cols = [constants.NAME_FIELDNAME, constants.SIGLUM_FIELDNAME,
                constants.LABEL_FIELDNAME]
        for index, (text_name, siglum, label) in \
            matches[cols].drop_duplicates().iterrows():
            extended_ngrams = self._generate_extended_ngrams(
                matches, text_name, siglum, label, corpus, highest_n)
            extended_matches = pd.concat(
                [extended_matches, self._generate_extended_matches(
                    extended_ngrams, highest_n, text_name, siglum, label)])
            extended_ngrams = None
        extended_matches = extended_matches.reindex_axis(
            constants.QUERY_FIELDNAMES, axis=1)
        if is_intersect:
            extended_matches = self._reciprocal_remove(extended_matches)
        self._matches = self._matches.append(extended_matches)

    def _generate_extended_matches (self, extended_ngrams, highest_n, name,
                                    siglum, label):
        """Returns extended match data derived from `extended_ngrams`.

        This extended match data are the counts for all intermediate
        n-grams within each extended n-gram.

        :param extended_ngrams: extended n-grams
        :type extended_ngrams: `list` of `str`
        :param highest_n: the highest degree of n-grams in the original results
        :type highest_n: `int`
        :param name: name of the text bearing `extended_ngrams`
        :type name: `str`
        :param siglum: siglum of the text bearing `extended_ngrams`
        :type siglum: `str`
        :param label: label associated with the text
        :type label: `str`
        :rtype: `pandas.DataFrame`

        """
        # Add data for each n-gram within each extended n-gram. Since
        # this treats each extended piece of text separately, the same
        # n-gram may be generated more than once, so the complete set
        # of new possible matches for this filename needs to combine
        # the counts for such.
        rows_list = []
        for extended_ngram in extended_ngrams:
            text = BaseText(extended_ngram, self._tokenizer)
            for size, ngrams in text.get_ngrams(highest_n+1,
                                                len(text.get_tokens())):
                data = [{constants.NAME_FIELDNAME: name,
                         constants.SIGLUM_FIELDNAME: siglum,
                         constants.LABEL_FIELDNAME: label,
                         constants.SIZE_FIELDNAME: size,
                         constants.NGRAM_FIELDNAME: ngram,
                         constants.COUNT_FIELDNAME: count}
                        for ngram, count in ngrams.items()]
                rows_list.extend(data)
        self._logger.debug('Number of extended results: {}'.format(
            len(rows_list)))
        extended_matches = pd.DataFrame(rows_list)
        rows_list = None
        self._logger.debug('Finished generating intermediate extended matches')
        # extended_matches may be an empty DataFrame, in which case
        # manipulating it on the basis of non-existing columns is not
        # going to go well.
        groupby_fields = [constants.NGRAM_FIELDNAME, constants.NAME_FIELDNAME,
                          constants.SIGLUM_FIELDNAME, constants.SIZE_FIELDNAME,
                          constants.LABEL_FIELDNAME]
        if constants.NGRAM_FIELDNAME in extended_matches:
            extended_matches = extended_matches.groupby(
                groupby_fields).sum().reset_index()
        return extended_matches

    def _generate_extended_ngrams (self, matches, name, siglum, label, corpus,
                                   highest_n):
        """Returns the n-grams of the largest size that exist in `siglum`
        witness to `name` text under `label`, generated from adding
        together overlapping n-grams in `matches`.

        :param matches: n-gram matches
        :type matches: `pandas.DataFrame`
        :param name: name of text whose results are being processed
        :type name: `str`
        :param siglum: siglum of witness whose results are being processed
        :type siglum: `str`
        :param label: label of witness whose results are being processed
        :type label: `str`
        :param corpus: corpus to which `filename` belongs
        :type corpus: `Corpus`
        :param highest_n: highest degree of n-gram in `matches`
        :type highest_n: `int`
        :rtype: `list` of `str`

        """
        # For large result sets, this method may involve a lot of
        # processing within the for loop, so optimise even small
        # things, such as aliasing dotted calls here and below.
        t_join = self._tokenizer.joiner.join
        witness_matches = matches[
            (matches[constants.NAME_FIELDNAME] == name) &
            (matches[constants.SIGLUM_FIELDNAME] == siglum) &
            (matches[constants.LABEL_FIELDNAME] == label)]
        text = corpus.get_text(name, siglum).get_token_content()
        ngrams = [tuple(self._tokenizer.tokenize(ngram)) for ngram in
                  list(witness_matches[constants.NGRAM_FIELDNAME])]
        # Go through the list of n-grams, and create a list of
        # extended n-grams by joining two n-grams together that
        # overlap (a[-overlap:] == b[:-1]) and checking that the result
        # occurs in text.
        working_ngrams = ngrams[:]
        extended_ngrams = set(ngrams)
        new_working_ngrams = []
        overlap = highest_n - 1
        # Create an index of n-grams by their overlapping portion,
        # pointing to the non-overlapping token.
        ngram_index = {}
        for ngram in ngrams:
            values = ngram_index.setdefault(ngram[:-1], [])
            values.append(ngram[-1:])
        extended_add = extended_ngrams.add
        new_working_append = new_working_ngrams.append
        ngram_size = highest_n
        while working_ngrams:
            removals = set()
            ngram_size += 1
            self._logger.debug(
                'Iterating over {} n-grams to produce {}-grams'.format(
                    len(working_ngrams), ngram_size))
            for base in working_ngrams:
                remove_base = False
                base_overlap = base[-overlap:]
                for next_token in ngram_index.get(base_overlap, []):
                    extension = base + next_token
                    if t_join(extension) in text:
                        extended_add(extension)
                        new_working_append(extension)
                        remove_base = True
                if remove_base:
                    # Remove base from extended_ngrams, because it is
                    # now encompassed by extension.
                    removals.add(base)
            extended_ngrams -= removals
            working_ngrams = new_working_ngrams[:]
            new_working_ngrams = []
            new_working_append = new_working_ngrams.append
        extended_ngrams = sorted(extended_ngrams, key=len, reverse=True)
        extended_ngrams = [t_join(ngram) for ngram in extended_ngrams]
        self._logger.debug('Generated {} extended n-grams'.format(
            len(extended_ngrams)))
        self._logger.debug('Longest generated n-gram: {}'.format(
            extended_ngrams[0]))
        # In order to get the counts correct in the next step of the
        # process, these n-grams must be overlaid over the text and
        # repeated as many times as there are matches. N-grams that do
        # not match (and they may not match on previously matched
        # parts of the text) are discarded.
        ngrams = []
        for ngram in extended_ngrams:
            # Remove from the text those parts that match. Replace
            # them with a double space, which should prevent any
            # incorrect match on the text from each side of the match
            # that is now contiguous.
            text, count = re.subn(re.escape(ngram), '  ', text)
            ngrams.extend([ngram] * count)
        self._logger.debug('Aligned extended n-grams with the text; '
                           '{} distinct n-grams exist'.format(len(ngrams)))
        return ngrams

    def _generate_substrings (self, ngram, size):
        """Returns a list of all substrings of `ngram`.

        :param ngram: n-gram to generate substrings of
        :type ngram: `str`
        :param size: size of `ngram`
        :type size: `int`
        :rtype: `list`

        """
        text = BaseText(ngram, self._tokenizer)
        substrings = []
        for sub_size, ngrams in text.get_ngrams(1, size-1):
            for sub_ngram, count in ngrams.items():
                substrings.extend([sub_ngram] * count)
        return substrings

    @staticmethod
    def _is_intersect_results (results):
        """Returns False if `results` has an n-gram that exists in only one
        label, True otherwise.

        :param results: results to analyze
        :type results: `pandas.DataFrame`
        :rtype: `bool`

        """
        sample = results.iloc[0]
        ngram = sample[constants.NGRAM_FIELDNAME]
        label = sample[constants.LABEL_FIELDNAME]
        return not(results[(results[constants.NGRAM_FIELDNAME] == ngram) &
                           (results[constants.LABEL_FIELDNAME] != label)].empty)

    def prune_by_ngram_count (self, minimum=None, maximum=None):
        """Removes results rows whose total n-gram count (across all
        texts bearing this n-gram) is outside the range specified by
        `minimum` and `maximum`.

        :param minimum: minimum n-gram count
        :type minimum: `int`
        :param maximum: maximum n-gram count
        :type maximum: `int`

        """
        self._logger.info('Pruning results by n-gram count')
        counts = pd.DataFrame(self._matches.groupby(constants.NGRAM_FIELDNAME)[
            constants.COUNT_FIELDNAME].sum())
        counts.rename(columns={constants.COUNT_FIELDNAME: 'tmp_count'},
                      inplace=True)
        if minimum:
            counts = counts[counts['tmp_count'] >= minimum]
        if maximum:
            counts = counts[counts['tmp_count'] <= maximum]
        self._matches = pd.merge(self._matches, counts,
                                 left_on=constants.NGRAM_FIELDNAME,
                                 right_index=True)
        del self._matches['tmp_count']

    def prune_by_ngram_size (self, minimum=None, maximum=None):
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

    def prune_by_text_count (self, minimum=None, maximum=None):
        """Removes results rows for n-grams that are not attested in a
        number of texts in the range specified by `minimum` and
        `maximum`.

        Text here encompasses all witnesses, so that the same n-gram
        appearing in multiple witnesses of the same text are counted
        as a single text.

        :param minimum: minimum number of texts
        :type minimum: `int`
        :param maximum: maximum number of texts
        :type maximum: `int`

        """
        self._logger.info('Pruning results by text count')
        count_fieldname = 'tmp_count'
        filtered = self._matches[self._matches[constants.COUNT_FIELDNAME] > 0]
        grouped = filtered.groupby(constants.NGRAM_FIELDNAME)
        counts = pd.DataFrame(grouped[constants.NAME_FIELDNAME].nunique())
        counts.rename(columns={constants.NAME_FIELDNAME: count_fieldname},
                      inplace=True)
        if minimum:
            counts = counts[counts[count_fieldname] >= minimum]
        if maximum:
            counts = counts[counts[count_fieldname] <= maximum]
        self._matches = pd.merge(self._matches, counts,
                                 left_on=constants.NGRAM_FIELDNAME,
                                 right_index=True)
        del self._matches[count_fieldname]

    def reciprocal_remove (self):
        """Removes results rows for which the n-gram is not present in
        at least one text in each labelled set of texts."""
        self._logger.info(
            'Removing n-grams that are not attested in all labels')
        self._matches = self._reciprocal_remove(self._matches)

    def _reciprocal_remove (self, matches):
        number_labels = matches[constants.LABEL_FIELDNAME].nunique()
        filtered = matches[matches[constants.COUNT_FIELDNAME] > 0]
        grouped = filtered.groupby(constants.NGRAM_FIELDNAME)
        return grouped.filter(
            lambda x: x[constants.LABEL_FIELDNAME].nunique() == number_labels)

    def reduce (self):
        """Removes results rows whose n-grams are contained in larger
        n-grams."""
        self._logger.info('Reducing the n-grams')
        # This does not make use of any pandas functionality; it
        # probably could, and if so ought to.
        data = {}
        labels = {}
        # Derive a convenient data structure from the rows.
        for row_index, row in self._matches.iterrows():
            name = row[constants.NAME_FIELDNAME]
            siglum = row[constants.SIGLUM_FIELDNAME]
            labels[name] = row[constants.LABEL_FIELDNAME]
            text_data = data.setdefault((name, siglum), {})
            text_data[row[constants.NGRAM_FIELDNAME]] = {
                'count': int(row[constants.COUNT_FIELDNAME]),
                'size': int(row[constants.SIZE_FIELDNAME])}
        for text_data in data.values():
            ngrams = list(text_data.keys())
            ngrams.sort(key=lambda ngram: text_data[ngram]['size'],
                        reverse=True)
            for ngram in ngrams:
                if text_data[ngram]['count'] > 0:
                    self._reduce_by_ngram(text_data, ngram)
        # Recreate rows from the modified data structure.
        rows = []
        for (name, siglum), text_data in data.items():
            for ngram, ngram_data in text_data.items():
                count = ngram_data['count']
                if count > 0:
                    rows.append(
                        {constants.NGRAM_FIELDNAME: ngram,
                         constants.SIZE_FIELDNAME: ngram_data['size'],
                         constants.NAME_FIELDNAME: name,
                         constants.SIGLUM_FIELDNAME: siglum,
                         constants.COUNT_FIELDNAME: count,
                         constants.LABEL_FIELDNAME: labels[name]})
        if rows:
            self._matches = pd.DataFrame(
                rows, columns=constants.QUERY_FIELDNAMES)
        else:
            self._matches = pd.DataFrame()

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

    def remove_label (self, label):
        self._logger.info('Removing label "{}"'.format(label))
        count = self._matches[constants.LABEL_FIELDNAME].value_counts()[label]
        self._matches = self._matches[
            self._matches[constants.LABEL_FIELDNAME] != label]
        self._logger.info('Removed {} labelled results'.format(count))

    def sort (self):
        self._matches.sort_values(
            by=[constants.SIZE_FIELDNAME, constants.NGRAM_FIELDNAME,
                constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME,
                constants.NAME_FIELDNAME, constants.SIGLUM_FIELDNAME],
            ascending=[False, True, False, True, True, True], inplace=True)

    def zero_fill (self, corpus, catalogue):
        """Adds rows to the results to ensure that, for every n-gram that is
        attested in at least one witness, every witness for that text
        has a row, with added rows having a count of zero.

        :param corpus: corpus containing the texts appearing in the results
        :type corpus: `Corpus`
        :param catalogue: catalogue used in the generation of the results
        :type catalogue: `Catalogue`

        """
        zero_rows = []
        # Get all of the texts, and their witnesses, for each label.
        data = {}
        for text, label in iter(catalogue.items()):
            data.setdefault(label, {})[text] = []
            for siglum in corpus.get_sigla(text):
                data[label][text].append(siglum)
        grouping_cols = [constants.LABEL_FIELDNAME, constants.NGRAM_FIELDNAME,
                         constants.SIZE_FIELDNAME, constants.NAME_FIELDNAME]
        grouped = self._matches.groupby(grouping_cols, sort=False)
        for (label, ngram, size, text), group in grouped:
            row_data = {
                constants.NGRAM_FIELDNAME: ngram,
                constants.LABEL_FIELDNAME: label,
                constants.SIZE_FIELDNAME: size,
                constants.COUNT_FIELDNAME: 0,
                constants.NAME_FIELDNAME: text,
            }
            for siglum in data[label][text]:
                if group[group[constants.SIGLUM_FIELDNAME] == siglum].empty:
                    row_data[constants.SIGLUM_FIELDNAME] = siglum
                    zero_rows.append(row_data)
        zero_df = pd.DataFrame(zero_rows, columns=constants.QUERY_FIELDNAMES)
        self._matches = pd.concat([self._matches, zero_df])
