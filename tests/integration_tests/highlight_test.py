#!/usr/bin/env python3

import os
import shlex
import shutil
import subprocess
import unittest

import lxml.html

import tacl
from ..tacl_test_case import TaclTestCase


class BaseHighlightIntegrationTestCase (TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'highlight_data')
        self._actual_output_dir = os.path.join(self._data_dir, 'actual_output')
        self._corpus = os.path.join(self._data_dir, 'stripped')
        self._tokenizer = tacl.constants.TOKENIZER_CHOICE_PAGEL
        if os.path.exists(self._actual_output_dir):
            raise Exception('{} exists; aborting test that would create '
                            'this directory'.format(self._actual_output_dir))

    def tearDown(self):
        if os.path.exists(self._actual_output_dir):
            shutil.rmtree(self._actual_output_dir)

    def _extract_text(self, html):
        """Returns the contents of the <div class="text"> in `html`."""
        root = lxml.html.fromstring(html)
        return lxml.html.tostring(root.xpath('//div[@class="text"]')[0])


class NgramHighlightIntegrationTestCase (BaseHighlightIntegrationTestCase):

    def test_highlight(self):
        ngrams = os.path.join(self._data_dir, 'ngrams.txt')
        minus_ngrams = os.path.join(self._data_dir, 'minus_ngrams.txt')
        command = 'tacl highlight -t {} -m {} -n {} -l L {} {} {} {}'.format(
            self._tokenizer, minus_ngrams, ngrams, self._corpus, 't1', 'base',
            self._actual_output_dir)
        subprocess.call(shlex.split(command))
        with open(os.path.join(self._actual_output_dir, 'report.html')) as fh:
            actual_output = fh.read()
        with open(os.path.join(self._data_dir, 'highlight.html')) as fh:
            expected_output = fh.read()
        self.assertEqual(self._extract_text(actual_output),
                         self._extract_text(expected_output))


class ResultsHighlightIntegrationTestCase (BaseHighlightIntegrationTestCase):

    def test_highlight(self):
        results = os.path.join(self._data_dir, 'results.csv')
        command = 'tacl highlight -t {} -r {} {} {} {} {}'.format(
            self._tokenizer, results, self._corpus, 't1', 'base',
            self._actual_output_dir)
        subprocess.call(shlex.split(command))
        with open(os.path.join(self._actual_output_dir, 'report.html')) as fh:
            actual_output = fh.read()
        with open(os.path.join(self._data_dir, 'heatmap.html')) as fh:
            expected_output = fh.read()
        self.assertEqual(self._extract_text(actual_output),
                         self._extract_text(expected_output))


if __name__ == '__main__':
    unittest.main()
