"""Module containing the Highlighter class."""

import logging
import re

from lxml import etree
import pandas as pd

from . import constants
from .report import Report
from .text import WitnessText


class HighlightReport(Report):

    _base_token_markup = r'<span>\1</span>'

    def __init__(self, corpus, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus
        self._tokenizer = tokenizer

    def _format_content(self, content):
        """Returns `content` with consecutive spaces converted to non-break
        spaces, and linebreak converted into HTML br elements.

        :param content: text to format
        :type content: `str`
        :rtype: `str`

        """
        content = re.sub(r'\n', '<br/>\n', content)
        content = re.sub(r'  ', '&#160;&#160;', content)
        content = re.sub(r'&#160; ', '&#160;&#160;', content)
        return content

    def _generate_base(self, work, siglum):
        witness = self._corpus.get_witness(work, siglum)
        content = witness.get_content().strip()
        return self._prepare_text(content)

    def _get_regexp_pattern(self, ngram):
        inter_token_pattern = r'</span>\W*<span[^>]*>'
        pattern = inter_token_pattern.join(
            [re.escape(token) for token in self._tokenizer.tokenize(ngram)])
        return r'(<span[^>]*>{}</span>)'.format(pattern)

    def generate(self, output_dir, work, siglum, *args):
        raise NotImplementedError

    def _prepare_text(self, text):
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
        return re.sub(pattern, self._base_token_markup, text)

    def _write(self, work, siglum, text, report_dir, copy_assets=False,
               **kwargs):
        context = {'base_name': work, 'base_siglum': siglum, 'text': text}
        context.update(kwargs)
        assets_dir = None
        if copy_assets:
            assets_dir = report_dir
        super()._write(context, report_dir, 'report.html', assets_dir)


class NgramHighlightReport (HighlightReport):

    _base_token_markup = r'<span>\1</span>'
    _report_name = 'ngram_highlight'

    def _annotate_tokens(self, match_obj):
        match = match_obj.group(0)
        root = etree.fromstring('<div>{}</div>'.format(match))
        for span in root.xpath('//span'):
            if self._add_highlight:
                span.set('class', 'highlight')
            elif span.get('class'):
                del span.attrib['class']
        return etree.tostring(root, encoding='unicode')[5:-6]

    def generate(self, output_dir, work, siglum, ngrams, minus_ngrams):
        """Generates an HTML report showing the text of `siglum` witness to
        `work` with its n-grams in `ngrams` highlighted.

        Any n-grams in `minus_ngrams` have any highlighting of them
        (or subsets of them) removed.

        :param output_dir: directory to write report to
        :type output_dir: `str`
        :param work: name of work to highlight
        :type work: `str`
        :param siglum: siglum of witness to highlight
        :type siglum: `str`
        :param ngrams: n-grams to highlight
        :type ngrams: `list` of `str`
        :param minus_ngrams: n-grams to remove highlighting from
        :type minus_ngrams: `list` of `str`
        :rtype: `str`

        """
        content = self._generate_base(work, siglum)
        content = self._highlight(content, ngrams, True)
        content = self._highlight(content, minus_ngrams, False)
        content = self._format_content(content)
        self._write(work, siglum, content, output_dir, ngrams=ngrams,
                    minus_ngrams=minus_ngrams)

    def _highlight(self, content, ngrams, highlight):
        """Returns `content` with its n-grams from `ngrams` highlighted (if
        `add_class` is True) or unhighlighted.

        :param content: text to be modified
        :type content: `str`
        :param ngrams: n-grams to modify
        :type ngrams: `list` of `str`
        :param highlight: whether to highlight or unhighlight `ngrams`
        :type highlight: `bool`
        :rtype: `str`

        """
        self._add_highlight = highlight
        for ngram in ngrams:
            pattern = self._get_regexp_pattern(ngram)
            content = re.sub(pattern, self._annotate_tokens, content)
        return content


class ResultsHighlightReport (HighlightReport):

    _base_token_markup = r'<span data-count="0" data-texts=" ">\1</span>'
    _report_name = 'results_highlight'

    def _annotate_tokens(self, match_obj):
        match = match_obj.group(0)
        root = etree.fromstring('<div>{}</div>'.format(match))
        for span in root.xpath('//span'):
            texts = span.get('data-texts')
            if ' {} '.format(self._match_source) not in texts:
                new_value = '{}{} '.format(texts, self._match_source)
                span.set('data-texts', new_value)
        return etree.tostring(root, encoding='unicode')[5:-6]

    @staticmethod
    def _generate_text_list(matches):
        texts = matches[[constants.WORK_FIELDNAME,
                         constants.SIGLUM_FIELDNAME]].drop_duplicates()
        text_list = []
        for index, (work, siglum) in texts.iterrows():
            text_list.append(WitnessText.assemble_filename(work, siglum))
        text_list.sort()
        return text_list

    def generate(self, output_dir, work, siglum, matches_filename):
        """Returns the text of `siglum` witness to `work` as an HTML
        document with its matches in `matches` highlighted.

        :param output_dir: directory to write report to
        :type output_dir: `str`
        :param work: name of work to highlight
        :type text_name: `str`
        :param siglum: siglum of witness to highlight
        :type siglum: `str`
        :param matches_filename: file containing matches to highlight
        :type matches_filename: `str`
        :rtype: `str`

        """
        matches = pd.read_csv(matches_filename)
        matches = matches[(matches[constants.WORK_FIELDNAME] != work) |
                          (matches[constants.SIGLUM_FIELDNAME] != siglum)]
        content = self._generate_base(work, siglum)
        content = self._highlight(content, matches)
        content = self._format_content(content)
        text_list = self._generate_text_list(matches)
        self._write(work, siglum, content, output_dir, True,
                    text_list=text_list)

    def _highlight(self, content, matches):
        for row_index, row in matches.iterrows():
            ngram = row[constants.NGRAM_FIELDNAME]
            self._match_source = WitnessText.assemble_filename(
                row[constants.WORK_FIELDNAME], row[constants.SIGLUM_FIELDNAME])
            pattern = self._get_regexp_pattern(ngram)
            content = re.sub(pattern, self._annotate_tokens, content)
        return content
