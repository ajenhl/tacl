"""Module containing the Report class."""

import logging

from lxml import etree
import pandas as pd

from . import constants
from .highlighter import Highlighter
from .text import BaseText


class Report:

    def __init__ (self, matches, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._matches = pd.read_csv(matches, encoding='utf-8')
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
        # Get the XML base text for each text in the results and
        # derive a count of all the n-grams that make it up.
        hl = Highlighter(corpus, self._tokenizer)
        highest_n = self._matches[constants.SIZE_FIELDNAME].max()
        # Supply the highlighter with only matches on the largest
        # n-grams.
        matches = self._matches[
            self._matches[constants.SIZE_FIELDNAME] == highest_n]
        transform = etree.XSLT(etree.XML(EXTEND_XSLT))
        extended_matches = pd.DataFrame()
        cols = [constants.FILENAME_FIELDNAME, constants.LABEL_FIELDNAME]
        for index, (filename, label) in \
            matches[cols].drop_duplicates().iterrows():
            base = hl.generate_base(matches, filename, False)
            # Apply XSLT to get chained matches.
            extended = transform(base, joiner="'{}'".format(
                self._tokenizer.joiner))
            extended_matches = extended_matches.append(
                self._generate_extended_matches(
                    extended, highest_n, filename, label), ignore_index=True)
        extended_matches = extended_matches.reindex_axis(
            constants.QUERY_FIELDNAMES, axis=1)
        extended_matches = self._reciprocal_remove(extended_matches)
        self._matches = self._matches.append(extended_matches)

    def _generate_extended_matches (self, extended, highest_n, filename, label):
        extended_matches = pd.DataFrame()
        extended_ngrams = extended.xpath('//ngram')
        # Add data for each n-gram within each extended n-gram. Since
        # this treats each extended piece of text separately, the same
        # n-gram may be generated more than once, so the complete set
        # of new possible matches for this filename needs to combine
        # the counts for such.
        for extended_ngram in extended_ngrams:
            content = extended_ngram.text
            if len(content) == highest_n:
                continue
            text = BaseText(content, self._tokenizer)
            for size, ngrams in text.get_ngrams(
                    highest_n+1, len(extended_ngram.text)):
                data = [{constants.FILENAME_FIELDNAME: filename,
                         constants.LABEL_FIELDNAME: label,
                         constants.SIZE_FIELDNAME: size,
                         constants.NGRAM_FIELDNAME: ngram,
                         constants.COUNT_FIELDNAME: count}
                        for ngram, count in ngrams.items()]
                extended_matches = extended_matches.append(
                    pd.DataFrame(data), ignore_index=True)
        # extended_matches may be an empty DataFrame, in which case
        # manipulating it on the basis of non-existing columns is not
        # going to go well.
        groupby_fields = [constants.NGRAM_FIELDNAME,
                          constants.FILENAME_FIELDNAME,
                          constants.SIZE_FIELDNAME, constants.LABEL_FIELDNAME]
        if constants.NGRAM_FIELDNAME in extended_matches:
            extended_matches = extended_matches.groupby(
                groupby_fields).sum().reset_index()
        return extended_matches

    def _generate_substrings (self, ngram, size):
        """Returns a list of all substrings of `ngram`.

        :param ngram: n-gram to generate substrings of
        :type ngram: `str`
        :param size: size of `ngram`
        :type size: `int`
        :rtype: `list`

        """
        substrings = []
        tokens = self._tokenizer.tokenize(ngram)
        for n in range(1, size):
            count = max(0, len(tokens) - n + 1)
            ngrams = [self._tokenizer.joiner.join(tokens[i:i+n]) for i in range(count)]
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

        :param minimum: minimum number of texts
        :type minimum: `int`
        :param maximum: maximum number of texts
        :type maximum: `int`

        """
        self._logger.info('Pruning results by text count')
        counts = pd.DataFrame(self._matches.groupby(
            constants.NGRAM_FIELDNAME)[constants.FILENAME_FIELDNAME].count())
        if minimum:
            counts = counts[counts[0] >= minimum]
        if maximum:
            counts = counts[counts[0] <= maximum]
        self._matches = pd.merge(self._matches, counts,
                                 left_on=constants.NGRAM_FIELDNAME,
                                 right_index=True)
        del self._matches[0]

    def reciprocal_remove (self):
        """Removes results rows for which the n-gram is not present in
        at least one text in each labelled set of texts."""
        self._logger.info(
            'Removing n-grams that are not attested in all labels')
        self._matches = self._reciprocal_remove(self._matches)

    def _reciprocal_remove (self, matches):
        number_labels = matches[constants.LABEL_FIELDNAME].nunique()
        grouped = matches.groupby(constants.NGRAM_FIELDNAME)
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
            filename = row[constants.FILENAME_FIELDNAME]
            labels[filename] = row[constants.LABEL_FIELDNAME]
            text_data = data.setdefault(filename, {})
            text_data[row[constants.NGRAM_FIELDNAME]] = {
                'count': int(row[constants.COUNT_FIELDNAME]),
                'size': int(row[constants.SIZE_FIELDNAME])}
        for filename, text_data in data.items():
            ngrams = list(text_data.keys())
            ngrams.sort(key=lambda ngram: text_data[ngram]['size'],
                        reverse=True)
            for ngram in ngrams:
                if text_data[ngram]['count'] > 0:
                    self._reduce_by_ngram(text_data, ngram)
        # Recreate rows from the modified data structure.
        rows = []
        for filename, text_data in data.items():
            for ngram, ngram_data in text_data.items():
                count = ngram_data['count']
                if count > 0:
                    rows.append(
                        {constants.NGRAM_FIELDNAME: ngram,
                         constants.SIZE_FIELDNAME: ngram_data['size'],
                         constants.FILENAME_FIELDNAME: filename,
                         constants.COUNT_FIELDNAME: count,
                         constants.LABEL_FIELDNAME: labels[filename]})
        if rows:
            self._matches = pd.DataFrame(rows, columns=constants.QUERY_FIELDNAMES)
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
        self._matches.sort_index(
            by=[constants.SIZE_FIELDNAME, constants.NGRAM_FIELDNAME,
                constants.COUNT_FIELDNAME, constants.LABEL_FIELDNAME,
                constants.FILENAME_FIELDNAME],
            ascending=[False, True, False, True, True], inplace=True)


EXTEND_XSLT = '''<xsl:stylesheet version="2.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:param name="joiner" />

  <xsl:template match="div">
    <xsl:copy>
      <xsl:apply-templates />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="span[@data-base-match]">
    <xsl:if test="not(preceding-sibling::*[1][@data-base-match])">
      <ngram>
        <xsl:apply-templates mode="ngram" select="." />
      </ngram>
    </xsl:if>
  </xsl:template>

  <xsl:template match="span" />

  <xsl:template match="span" mode="ngram">
    <xsl:value-of select="$joiner" />
    <xsl:value-of select="." />
    <xsl:if test="following-sibling::*[1][@data-base-match]">
      <xsl:apply-templates mode="ngram"
                           select="following-sibling::*[1]" />
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>'''
