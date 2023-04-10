#!/usr/bin/env python3

import os.path
import tempfile
import unittest

import tacl
from ..tacl_test_case import TaclTestCase


class StripperIntegrationTestCase (TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'data')
        self._xml_dir = os.path.join(self._data_dir, 'expected_corpus_output')
        self._expected_output_dir = os.path.join(
            self._data_dir, 'expected_stripped_output')

    def _strip_and_compare(self, input_path, output_path):
        xml_dir = os.path.join(self._xml_dir, input_path)
        expected_dir = os.path.join(self._expected_output_dir, output_path)
        with tempfile.TemporaryDirectory() as actual_dir:
            stripper = tacl.Stripper(xml_dir, actual_dir)
            stripper.strip_files()
            self._compare_dirs(actual_dir, expected_dir)

    def test_github_basic_strip_files(self):
        self._strip_and_compare(os.path.join('github', 'basic'), 'basic')

    def test_github_cb_tt_strip_files(self):
        self._strip_and_compare(os.path.join('github', 'cb_tt'), 'cb_tt')

    def test_github_strip_empty_file(self):
        input_dir = os.path.join(self._xml_dir, 'github', 'empty')
        output_dir = os.path.join(self._expected_output_dir, 'empty')
        stripper = tacl.Stripper(input_dir, output_dir)
        stripper.strip_files()
        self.assertFalse(os.path.exists(os.path.join(output_dir, 'empty')))


if __name__ == '__main__':
    unittest.main()
