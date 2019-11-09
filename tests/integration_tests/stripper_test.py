#!/usr/bin/env python3

import os
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

    def test_github_strip_files(self):
        xml_dir = os.path.join(self._xml_dir, 'github', 'basic')
        expected_dir = os.path.join(self._expected_output_dir, 'basic')
        with tempfile.TemporaryDirectory() as actual_dir:
            stripper = tacl.Stripper(xml_dir, actual_dir)
            stripper.strip_files()
            self._compare_dirs(actual_dir, expected_dir)


if __name__ == '__main__':
    unittest.main()
