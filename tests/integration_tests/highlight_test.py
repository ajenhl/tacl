#!/usr/bin/env python3

import os
import shlex
import subprocess
import unittest

import lxml.html

import tacl
from ..tacl_test_case import TaclTestCase


class HighlightIntegrationTestCase (TaclTestCase):

    def setUp (self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'highlight_data')

    def test_highlight (self):
        corpus = os.path.join(self._data_dir, 'stripped')
        results = os.path.join(self._data_dir, 'results.csv')
        command = 'tacl highlight -t {} {} {} {} {}'.format(
            tacl.constants.TOKENIZER_CHOICE_PAGEL, corpus, results, 't1',
            'base')
        actual_output = subprocess.check_output(shlex.split(command))
        with open(os.path.join(self._data_dir, 'highlight.html'), 'r') as fh:
            expected_output = fh.read()
        self.assertEqual(self._extract_text(actual_output),
                         self._extract_text(expected_output))

    def _extract_text (self, html):
        """Returns the contents of the <div class="text"> in `html`."""
        root = lxml.html.fromstring(html)
        return lxml.html.tostring(root.xpath('//div[@class="text"]')[0])


if __name__ == '__main__':
    unittest.main()
