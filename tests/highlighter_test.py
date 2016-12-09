#!/usr/bin/env python3

import unittest

import pandas as pd

import tacl
from .tacl_test_case import TaclTestCase


class NgramHighlightReportTestCase (TaclTestCase):

    def setUp(self):
        self._tokenizer = tacl.Tokenizer(
            tacl.constants.TOKENIZER_PATTERN_CBETA,
            tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_highlight(self):
        input_text = (
            '<span>火</span><span>無</span><span>[火*因]</span>。'
            '<span>是</span><span>故</span><span>顯</span><span>物</span>')
        ngrams = ['無[火*因]是']
        report = tacl.NgramHighlightReport(None, self._tokenizer)
        actual_text = report._highlight(input_text, ngrams, True)
        expected_text = (
            '<span>火</span><span class="highlight1">無</span>'
            '<span class="highlight1">[火*因]</span>。'
            '<span class="highlight1">是</span><span>故</span><span>顯</span>'
            '<span>物</span>')
        self.assertEqual(actual_text, expected_text)

    def test_highlight_minus(self):
        input_text = (
            '<span class="highlight2">火</span><span class="highlight">無</span>'
            '<span class="highlight1">[火*因]</span>。<span class="highlight1">'
            '是</span><span>故</span><span class="highlight2">火</span>'
            '<span>顯</span><span>物</span><span class="highlight2">火</span>')
        minus_ngrams = ['火顯']
        report = tacl.NgramHighlightReport(None, self._tokenizer)
        actual_text = report._highlight(input_text, minus_ngrams, False)
        expected_text = (
            '<span class="highlight2">火</span><span class="highlight">無</span>'
            '<span class="highlight1">[火*因]</span>。<span class="highlight1">'
            '是</span><span>故</span><span>火</span><span>顯</span><span>物'
            '</span><span class="highlight2">火</span>')
        self.assertEqual(actual_text, expected_text)

    def test_prepare_text_cbeta(self):
        input_text = '無[火*因]是<物即\n\n    同如'
        expected_text = (
            '<span>無</span><span>[火*因]</span><span>是</span><span>物</span>'
            '<span>即</span>\n\n    <span>同</span><span>如</span>')
        report = tacl.NgramHighlightReport(None, self._tokenizer)
        actual_text = report._prepare_text(input_text)
        self.assertEqual(actual_text, expected_text)

    def test_prepare_text_pagel(self):
        input_text = "'dzin dang | snang\n \nba'i"
        expected_text = (
            "<span>'dzin</span> <span>dang</span> | <span>snang</span>\n \n"
            "<span>ba'i</span>")
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        report = tacl.NgramHighlightReport(None, tokenizer)
        actual_text = report._prepare_text(input_text)
        self.assertEqual(actual_text, expected_text)


class ResultsHighlightReportTestCase (TaclTestCase):

    def setUp(self):
        self._tokenizer = tacl.Tokenizer(
            tacl.constants.TOKENIZER_PATTERN_CBETA,
            tacl.constants.TOKENIZER_JOINER_CBETA)
        self.maxDiff = None

    def test_format_content(self):
        input_text = (
            '<span data-count="0" data-texts=" ">火</span>'
            '<span data-count="0" data-texts=" ">無</span>'
            ' <span data-count="0" data-texts=" ">[火*因]</span>。'
            '<span data-count="0" data-texts=" ">是</span>'
            '<span data-count="0" data-texts=" ">故</span>\n\n'
            '    <span data-count="0" data-texts=" ">顯</span>'
            '     <span data-count="0" data-texts=" ">物</span>')
        report = tacl.ResultsHighlightReport(None, self._tokenizer)
        actual_output = report._format_content(input_text)
        expected_output = (
            '<span data-count="0" data-texts=" ">火</span>'
            '<span data-count="0" data-texts=" ">無</span>'
            ' <span data-count="0" data-texts=" ">[火*因]</span>。'
            '<span data-count="0" data-texts=" ">是</span>'
            '<span data-count="0" data-texts=" ">故</span><br/>\n<br/>'
            '\n&#160;&#160;&#160;&#160;<span data-count="0" data-texts=" ">'
            '顯</span>&#160;&#160;&#160;&#160;&#160;'
            '<span data-count="0" data-texts=" ">物</span>')
        self.assertEqual(actual_output, expected_output)

    def test_generate_text_list(self):
        results = pd.DataFrame([
            {tacl.constants.NGRAM_FIELDNAME: '無[火*因]是',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.WORK_FIELDNAME: 't2',
             tacl.constants.SIGLUM_FIELDNAME: 'base',
             tacl.constants.COUNT_FIELDNAME: '2',
             tacl.constants.LABEL_FIELDNAME: 'B'},
            {tacl.constants.NGRAM_FIELDNAME: '無[火*因]是',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.WORK_FIELDNAME: 't2',
             tacl.constants.SIGLUM_FIELDNAME: '大',
             tacl.constants.COUNT_FIELDNAME: '1',
             tacl.constants.LABEL_FIELDNAME: 'B'},
            {tacl.constants.NGRAM_FIELDNAME: '無[火*因]是',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.WORK_FIELDNAME: 't3',
             tacl.constants.SIGLUM_FIELDNAME: 'base',
             tacl.constants.COUNT_FIELDNAME: '4',
             tacl.constants.LABEL_FIELDNAME: 'B'},
            ])
        actual_text_list = tacl.ResultsHighlightReport._generate_text_list(
            results)
        expected_text_list = ['t2/base.txt', 't2/大.txt', 't3/base.txt']
        self.assertEqual(actual_text_list, expected_text_list)

    def test_get_regexp_pattern(self):
        input_ngram = 'ab[cd]e'
        report = tacl.ResultsHighlightReport(None, self._tokenizer)
        actual_pattern = report._get_regexp_pattern(input_ngram)
        expected_pattern = (r'(<span[^>]*>a</span>\W*<span[^>]*>b</span>\W*'
                            r'<span[^>]*>\[cd\]</span>\W*<span[^>]*>e</span>)')
        self.assertEqual(actual_pattern, expected_pattern)

    def test_highlight(self):
        input_text = (
            '<span data-count="0" data-texts=" ">火</span>'
            '<span data-count="0" data-texts=" ">無</span>'
            '<span data-count="0" data-texts=" ">[火*因]</span>。'
            '<span data-count="0" data-texts=" ">是</span>'
            '<span data-count="0" data-texts=" ">故</span>'
            '<span data-count="0" data-texts=" ">顯</span>'
            '<span data-count="0" data-texts=" ">物</span>')
        input_results = pd.DataFrame([
            {tacl.constants.NGRAM_FIELDNAME: '無[火*因]是',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.WORK_FIELDNAME: 't2',
             tacl.constants.SIGLUM_FIELDNAME: 'base',
             tacl.constants.COUNT_FIELDNAME: '2',
             tacl.constants.LABEL_FIELDNAME: 'B'}])
        report = tacl.ResultsHighlightReport(None, self._tokenizer)
        actual_text = report._highlight(input_text, input_results)
        expected_text = (
            '<span data-count="0" data-texts=" ">火</span>'
            '<span data-count="0" data-texts=" t2/base.txt ">無</span>'
            '<span data-count="0" data-texts=" t2/base.txt ">[火*因]</span>。'
            '<span data-count="0" data-texts=" t2/base.txt ">是</span>'
            '<span data-count="0" data-texts=" ">故</span>'
            '<span data-count="0" data-texts=" ">顯</span>'
            '<span data-count="0" data-texts=" ">物</span>')
        self.assertEqual(actual_text, expected_text)

    def test_prepare_text_cbeta(self):
        input_text = '無[火*因]是<物即\n\n    同如'
        expected_text = (
            '<span data-count="0" data-texts=" ">無</span>'
            '<span data-count="0" data-texts=" ">[火*因]</span>'
            '<span data-count="0" data-texts=" ">是</span>'
            '<span data-count="0" data-texts=" ">物</span>'
            '<span data-count="0" data-texts=" ">即</span>\n\n'
            '    <span data-count="0" data-texts=" ">同</span>'
            '<span data-count="0" data-texts=" ">如</span>')
        report = tacl.ResultsHighlightReport(None, self._tokenizer)
        actual_text = report._prepare_text(input_text)
        self.assertEqual(actual_text, expected_text)

    def test_prepare_text_pagel(self):
        input_text = "'dzin dang | snang\n \nba'i"
        expected_text = (
            '''<span data-count="0" data-texts=" ">'dzin</span>'''
            ' <span data-count="0" data-texts=" ">dang</span> |'
            ' <span data-count="0" data-texts=" ">snang</span>\n \n'
            '''<span data-count="0" data-texts=" ">ba'i</span>''')
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        report = tacl.ResultsHighlightReport(None, tokenizer)
        actual_text = report._prepare_text(input_text)
        self.assertEqual(actual_text, expected_text)


if __name__ == '__main__':
    unittest.main()
