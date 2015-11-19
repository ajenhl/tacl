"""Module containing the Highlighter class."""

import logging
import re

from jinja2 import Environment, PackageLoader
from lxml import etree
import pandas as pd

from . import constants
from .text import Text


class Highlighter:

    def __init__ (self, corpus, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus
        self._tokenizer = tokenizer

    def _annotate_tokens (self, match_obj):
        match = match_obj.group(0)
        root = etree.fromstring('<div>{}</div>'.format(match))
        for span in root.xpath('//span'):
            # The results are not guaranteed to have non-base matches
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

    def _format_text (self, text):
        """Returns `text` with consecutive spaces converted to non-break
        spaces, and linebreak converted into HTML br elements.

        :param text: text to format
        :type text: `str`
        :rtype: `str`

        """
        text = re.sub(r'\n', '<br/>\n', text)
        text = re.sub(r'  ', '&#160;&#160;', text)
        text = re.sub(r'&#160; ', '&#160;&#160;', text)
        return text

    def generate_base (self, matches, text_name, siglum, all=True):
        """Returns an XML document containing the text of `filename`
        marked up with its n-grams in `matches`.

        If `all` is True, generate results for all matches, not just
        those on `filename`.

        :param matches: matches data
        :type matches: `pandas.DataFrame`
        :param text_name: name of text to generate an XML document from
        :type text_name: `str`
        :param siglum: siglum of text variant to generate an XML document from
        :type siglum: `str`
        :rtype: `lxml.etree._Element`

        """
        text = self._corpus.get_text(text_name, siglum)
        filename = text.get_filename()
        self._logger.debug('Generating the base XML file for {}'.format(
            filename))
        self._base_filename = filename
        content = text.get_content().strip()
        content = self._prepare_text(content)
        if not all:
            matches = matches[matches[constants.NAME_FIELDNAME] == filename]
        content = self._highlight(content, matches)
        content = self._format_text(content)
        root = etree.fromstring('<div>{}</div>'.format(content))
        return root

    def _generate_html (self, matches, text_name, siglum, text):
        loader = PackageLoader('tacl', 'assets/templates')
        env = Environment(loader=loader)
        text_list = self._generate_text_list(matches, text_name, siglum)
        text_data = {'base_name': text_name, 'base_siglum': siglum,
                     'text': text, 'text_list': text_list}
        template = env.get_template('highlight.html')
        return template.render(text_data)

    @staticmethod
    def _generate_text_list (matches, base_name, base_siglum):
        texts = matches[[constants.NAME_FIELDNAME,
                         constants.SIGLUM_FIELDNAME]].drop_duplicates()
        text_list = []
        for index, (name, siglum) in texts.iterrows():
            if not(name == base_name and siglum == base_siglum):
                text_list.append(Text.assemble_filename(name, siglum))
        text_list.sort()
        return text_list

    def _get_regexp_pattern (self, ngram):
        inter_token_pattern = r'</span>\W*<span[^>]*>'
        pattern = inter_token_pattern.join(
            [re.escape(token) for token in self._tokenizer.tokenize(ngram)])
        return r'(<span[^>]*>{}</span>)'.format(pattern)

    def highlight (self, matches_filename, text_name, siglum):
        """Returns the text of `filename` as an HTML document with its matches
        in `matches` highlighted.

        :param results: file containing matches to highlight
        :type results: `TextIOWrapper`
        :param corpus: corpus of documents containing `text_filename`
        :type corpus: `tacl.Corpus`
        :param text_name: name of text to highlight
        :type text_name: `str`
        :param siglum: siglum of text to highlight
        :type siglum: `str`
        :rtype: `str`

        """
        matches = pd.read_csv(matches_filename)
        base = self.generate_base(matches, text_name, siglum, all=True)
        text = etree.tostring(base, encoding='unicode', xml_declaration=False)
        return self._generate_html(matches, text_name, siglum, text)

    def _highlight (self, text, matches):
        for row_index, row in matches.iterrows():
            ngram = row[constants.NGRAM_FIELDNAME]
            self._match_source = Text.assemble_filename(
                row[constants.NAME_FIELDNAME], row[constants.SIGLUM_FIELDNAME])
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
