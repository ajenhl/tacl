"""Module containing the Highlighter class."""

import csv
import re

from lxml import etree

from . import constants


class Highlighter:

    def __init__ (self, corpus, results):
        self._corpus = corpus
        self._results = [row for row in csv.DictReader(results)]

    @staticmethod
    def _generate_text_list (results, base_filename):
        text_list = set()
        for row in results:
            text_list.add(row[constants.FILENAME_FIELDNAME])
        text_list.discard(base_filename)
        text_list = list(text_list)
        text_list.sort()
        return text_list

    @staticmethod
    def _generate_text_list_html (text_list):
        widgets = []
        for text in text_list:
            widgets.append('<li><input type="checkbox" name="text" value="{0}"> {0}'.format(text))
        html = '<form><ul>{}</ul></form>'.format(''.join(widgets))
        return html

    @staticmethod
    def _get_multi_regexp_pattern (ngram):
        interchar_pattern = r'</span>\W*<span[^>]*>'
        pattern = interchar_pattern.join([re.escape(char) for char in ngram])
        return r'(<span[^>]*>{}</span>)'.format(pattern)

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
        pattern = interchar_pattern.join([re.escape(char) for char in ngram])
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

    def multi_highlight (self, base_filename):
        text = self._corpus.get_text(base_filename).get_content().strip()
        text = self._prepare_multi_text(text)
        text = self._multi_highlight(text, self._results)
        text = re.sub(r'\n', r'<br>\n', text)
        text = re.sub(r'<span data-texts=" ">([^<]*)</span>', r'\1', text)
        text_list = self._generate_text_list(self._results, base_filename)
        text_list_html = self._generate_text_list_html(text_list)
        text_data = {'base_filename': base_filename, 'text': text,
                     'text_list': text_list_html}
        return constants.HIGHLIGHT_MULTI_TEMPLATE.format(**text_data)

    def _multi_highlight (self, text, results):
        for result in results:
            ngram = result[constants.NGRAM_FIELDNAME]
            self._match_source = result[constants.FILENAME_FIELDNAME]
            pattern = self._get_multi_regexp_pattern(ngram)
            text = re.sub(pattern, self._sub_multi, text)
        return text

    @staticmethod
    def _prepare_multi_text (text):
        return re.sub(r'(\w)', r'<span data-count="0" data-texts=" ">\1</span>',
                      text)

    def _sub_multi (self, match_obj):
        match = match_obj.group(0)
        # Add the filename associated with this match to the
        # data-texts attribute.
        root = etree.fromstring('<div>{}</div>'.format(match))
        for span in root.xpath('//span'):
            texts = span.get('data-texts')
            if ' {} '.format(self._match_source) not in texts:
                new_value = '{}{} '.format(texts, self._match_source)
                span.set('data-texts', new_value)
        return etree.tostring(root, encoding='utf-8').decode('utf-8')[5:-6]
