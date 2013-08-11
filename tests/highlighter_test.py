#!/usr/bin/env python3

import csv
import unittest

import tacl
from .tacl_test_case import TaclTestCase


class HighlighterTestCase (TaclTestCase):

    def test_get_regexp_pattern (self):
        input_ngram = 'ab[cd]e'
        actual_pattern = tacl.Highlighter._get_regexp_pattern(input_ngram)
        expected_pattern = r'(a\W*b\W*[\W*c\W*d\W*]\W*e)'
        self.assertEqual(actual_pattern, expected_pattern)

    def test_get_text_results (self):
        input_results = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'A'], ['ABCD', '4', 'a', '2', 'A'],
            ['AB', '2', 'b', '2', 'B'], ['ABC', '3', 'c', '2', 'A'])
        input_rows = [row for row in csv.DictReader(
            self._create_csv(input_results))]
        actual_rows = tacl.Highlighter._get_text_results(input_rows, 'a')
        expected_rows = [
            {tacl.constants.NGRAM_FIELDNAME: 'ABCD',
             tacl.constants.SIZE_FIELDNAME: '4',
             tacl.constants.FILENAME_FIELDNAME: 'a',
             tacl.constants.COUNT_FIELDNAME: '2',
             tacl.constants.LABEL_FIELDNAME: 'A'},
            {tacl.constants.NGRAM_FIELDNAME: 'ABC',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.FILENAME_FIELDNAME: 'a',
             tacl.constants.COUNT_FIELDNAME: '2',
             tacl.constants.LABEL_FIELDNAME: 'A'},
            {tacl.constants.NGRAM_FIELDNAME: 'ABD',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.FILENAME_FIELDNAME: 'a',
             tacl.constants.COUNT_FIELDNAME: '1',
             tacl.constants.LABEL_FIELDNAME: 'A'},
            {tacl.constants.NGRAM_FIELDNAME: 'AB',
             tacl.constants.SIZE_FIELDNAME: '2',
             tacl.constants.FILENAME_FIELDNAME: 'a',
             tacl.constants.COUNT_FIELDNAME: '4',
             tacl.constants.LABEL_FIELDNAME: 'A'},
        ]
        self.assertEqual(actual_rows, expected_rows)

    def test_highlight (self):
        input_text = 'thenAweAwent'
        input_results = [
            {tacl.constants.NGRAM_FIELDNAME: 'the',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.FILENAME_FIELDNAME: '2.txt',
             tacl.constants.COUNT_FIELDNAME: '1',
             tacl.constants.LABEL_FIELDNAME: 'B'},
            {tacl.constants.NGRAM_FIELDNAME: 'ent',
             tacl.constants.SIZE_FIELDNAME: '3',
             tacl.constants.FILENAME_FIELDNAME: '2.txt',
             tacl.constants.COUNT_FIELDNAME: '1',
             tacl.constants.LABEL_FIELDNAME: 'B'},
            {tacl.constants.NGRAM_FIELDNAME: 'th',
             tacl.constants.SIZE_FIELDNAME: '2',
             tacl.constants.FILENAME_FIELDNAME: '2.txt',
             tacl.constants.COUNT_FIELDNAME: '1',
             tacl.constants.LABEL_FIELDNAME: 'B'},
            {tacl.constants.NGRAM_FIELDNAME: 'he',
             tacl.constants.SIZE_FIELDNAME: '2',
             tacl.constants.FILENAME_FIELDNAME: '2.txt',
             tacl.constants.COUNT_FIELDNAME: '2',
             tacl.constants.LABEL_FIELDNAME: 'B'},
            {tacl.constants.NGRAM_FIELDNAME: 'eA',
             tacl.constants.SIZE_FIELDNAME: '2',
             tacl.constants.FILENAME_FIELDNAME: '2.txt',
             tacl.constants.COUNT_FIELDNAME: '2',
             tacl.constants.LABEL_FIELDNAME: 'B'}]
        highlighter = tacl.Highlighter(None, [])
        actual_text = highlighter._highlight(input_text, input_results)
        expected_text = '<span class="highlight"><span class="highlight">th</span>e</span>nAw<span class="highlight">eA</span>w<span class="highlight">ent</span>'
        self.assertEqual(actual_text, expected_text)


if __name__ == '__main__':
    unittest.main()
