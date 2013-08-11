"""Module containing the Highlighter class."""

import csv
import re

from . import constants


class Highlighter:

    def __init__ (self, corpus, results):
        self._corpus = corpus
        self._results = [row for row in csv.DictReader(results)]

    @staticmethod
    def _get_regexp_pattern (ngram):
        """Returns a regular expression pattern for matching on `ngram`.

        The individual tokens in `ngram` may, in the text the pattern
        is to match on, be mixed in with any number of non-tokens.

        :param ngram: n-gram to create a pattern for
        :type ngram: `str`
        :rtype: `str`

        """
        interchar_pattern = r'\W*'
        pattern = interchar_pattern.join([char for char in ngram])
        return r'({})'.format(pattern)

    @staticmethod
    def _get_text_results (results, filename):
        """Returns members of `results` associated with `filename`,
        sorted in descending order of size.

        :param results: rows of results
        :type results: `list`
        :param filename: filename to restrict results to
        :type filename: `str`
        :rtype: `list`

        """
        results = [row for row in results \
                   if row[constants.FILENAME_FIELDNAME] == filename]
        results.sort(key=lambda row: row[constants.SIZE_FIELDNAME],
                     reverse=True)
        return results

    def highlight (self, base_filename, results_filename):
        """Returns the text of `base_filename` with the results tokens
        for `results_filename` highlighted.

        :param base_filename: filename of text to highlight
        :type base_filename: `str`
        :param results_filename: filename of text whose tokens are highlighted
        :type: results_filename: `str`
        :rtype: `str`

        """
        text = self._corpus.get_text(base_filename).get_content().strip()
        results = self._get_text_results(self._results, results_filename)
        text = self._highlight(text, results)
        text = re.sub(r'\n', r'<br>\n', text)
        text_data = {'base_filename': base_filename,
                     'results_filename': results_filename,
                     'text': text}
        return constants.HIGHLIGHT_TEMPLATE.format(**text_data)

    def _highlight (self, text, results):
        """Returns `text` with all n-grams in `results` highlighted.

        :param text: text to highlight
        :type text: `str`
        :param results: results to be highlighted
        :type results: `list`
        :rtype: `str`

        """
        for result in results:
            ngram = result[constants.NGRAM_FIELDNAME]
            pattern = self._get_regexp_pattern(ngram)
            text = re.sub(pattern, r'<span class="highlight">\1</span>', text)
        return text
