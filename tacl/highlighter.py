"""Module containing the Highlighter class."""

import logging
import re

from lxml import etree
import pandas as pd

from . import constants


class Highlighter:

    def __init__ (self, corpus, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus
        self._tokenizer = tokenizer

    def _annotate_tokens (self, match_obj):
        match = match_obj.group(0)
        root = etree.fromstring('<div>{}</div>'.format(match))
        for span in root.xpath('//span'):
            # The resuls are not guaranteed to have non-base matches
            # in it, so do not rely on being able to derive base
            # matches from them.
            if self._match_source == self._base_filename:
                if span.get('data-base-match') is None:
                    span.set('data-base-match', '')
            else:
                texts = span.get('data-texts')
                if ' {} '.format(self._match_source) not in texts:
                    new_value = '{}{} '.format(texts, self._match_source)
                    span.set('data-texts', new_value)
        return etree.tostring(root, encoding='unicode')[5:-6]

    def generate_base (self, matches, filename, all=True):
        """Returns an XML document containing the text of `filename`
        marked up with its n-grams in `matches`.

        If `all` is True, generate results for all matches, not just
        those on `filename`.

        :param matches: matches data
        :type matches: `pandas.DataFrame`
        :param filename: filename of text to generate an XML document from
        :type filename: `str`
        :rtype: `lxml.etree._Element`

        """
        self._logger.debug('Generating the base XML file for {}'.format(
            filename))
        self._base_filename = filename
        text = self._corpus.get_text(filename).get_content().strip()
        text = self._prepare_text(text)
        if not all:
            matches = matches[matches[constants.FILENAME_FIELDNAME] == filename]
        text = self._highlight(text, matches)
        root = etree.fromstring('<div>{}</div>'.format(text))
        return root

    def _generate_html (self, matches, base_filename, text):
        text_list = self._generate_text_list(matches, base_filename)
        text_list_html = self._generate_text_list_html(text_list)
        text_data = {'base_filename': base_filename, 'text': text,
                     'text_list': text_list_html}
        return constants.HIGHLIGHT_TEMPLATE.format(**text_data)

    @staticmethod
    def _generate_text_list (matches, base_filename):
        text_list = list(matches[constants.FILENAME_FIELDNAME].unique())
        text_list.remove(base_filename)
        text_list.sort()
        return text_list

    @staticmethod
    def _generate_text_list_html (texts):
        widgets = []
        for text in texts:
            widgets.append('<li><input type="checkbox" name="text" value="{0}"> {0}'.format(text))
        text_list = '<form><ul>{}</ul></form>'.format(''.join(widgets))
        return text_list

    def _get_regexp_pattern (self, ngram):
        inter_token_pattern = r'</span>\W*<span[^>]*>'
        pattern = inter_token_pattern.join(
            [re.escape(token) for token in self._tokenizer.tokenize(ngram)])
        return r'(<span[^>]*>{}</span>)'.format(pattern)

    def highlight (self, matches_filename, text_filename):
        """Returns the text of `filename` as an HTML document with its matches
        in `matches` highlighted.

        :param results: file containing matches to highlight
        :type results: `TextIOWrapper`
        :param corpus: corpus of documents containing `text_filename`
        :type corpus: `tacl.Corpus`
        :param filename: filename of text to highlight
        :type filename: `str`

        """
        matches = pd.read_csv(matches_filename)
        base = self.generate_base(matches, text_filename, all=True)
        text = etree.tostring(base, encoding='unicode', xml_declaration=False)
        return self._generate_html(matches, text_filename, text)

    def _highlight (self, text, matches):
        for row_index, row in matches.iterrows():
            ngram = row[constants.NGRAM_FIELDNAME]
            self._match_source = row[constants.FILENAME_FIELDNAME]
            pattern = self._get_regexp_pattern(ngram)
            text = re.sub(pattern, self._annotate_tokens, text)
        return text

    def _prepare_text (self, text):
        """Returns `text` with each consituent token wrapped in HTML markup
        for later match annotation.

        :param text: text to be marked up
        :type text: `str`
        :rtype: `str`

        """
        # Remove characters that should be escaped for XML input (but
        # which cause problems when escaped, since they become
        # tokens).
        text = re.sub(r'[<>&]', '', text)
        pattern = r'({})'.format(self._tokenizer.pattern)
        replacement = r'<span data-count="0" data-texts=" ">\1</span>'
        return re.sub(pattern, replacement, text)
