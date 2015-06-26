#!/usr/bin/env python3

import io
import os
import shlex
import subprocess
import unittest


import tacl
from ..tacl_test_case import TaclTestCase


class ReportIntegrationTestCase (TaclTestCase):

    def setUp (self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'report_data')
        self._stripped_dir = os.path.join(self._data_dir, 'stripped')

    def test_extend_cbeta (self):
        results = os.path.join(self._data_dir, 'cbeta-non-extend-results.csv')
        command = 'tacl report -e {} -t {} {}'.format(
            os.path.join(self._stripped_dir, 'cbeta'),
            tacl.constants.TOKENIZER_CHOICE_CBETA, results)
        data = subprocess.check_output(shlex.split(command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_results = os.path.join(self._data_dir,
                                        'cbeta-extend-results.csv')
        with open(expected_results, newline='') as fh:
            expected_rows = self._get_rows_from_csv(fh)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_extend_pagel (self):
        results = os.path.join(self._data_dir, 'pagel-non-extend-results.csv')
        command = 'tacl report -e {} -t {} {}'.format(
            os.path.join(self._stripped_dir, 'pagel'),
            tacl.constants.TOKENIZER_CHOICE_PAGEL, results)
        data = subprocess.check_output(shlex.split(command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_results = os.path.join(self._data_dir,
                                        'pagel-extend-results.csv')
        with open(expected_results, newline='') as fh:
            expected_rows = self._get_rows_from_csv(fh)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_extend_multiply_labelled (self):
        # Test that a witness that exists under more than one label is
        # properly extended.
        results = os.path.join(self._data_dir,
                               'multiply-labelled-non-extend-results.csv')
        command = 'tacl report -e {} -t {} {}'.format(
            os.path.join(self._stripped_dir, 'multiply-labelled'),
            tacl.constants.TOKENIZER_CHOICE_CBETA, results)
        data = subprocess.check_output(shlex.split(command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_results = os.path.join(self._data_dir,
                                        'multiply-labelled-extend-results.csv')
        with open(expected_results, newline='') as fh:
            expected_rows = self._get_rows_from_csv(fh)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_zero_fill (self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = os.path.join(data_dir, 'stripped')
        catalogue = os.path.join(data_dir, 'catalogue.txt')
        results = os.path.join(data_dir, 'non-zero-fill-results.csv')
        command = 'tacl report -c {} -z {} {}'.format(catalogue, corpus,
                                                      results)
        data = subprocess.check_output(shlex.split(command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_results = os.path.join(data_dir, 'zero-fill-results.csv')
        with open(expected_results, newline='') as fh:
            expected_rows = self._get_rows_from_csv(fh)
        self.assertEqual(set(actual_rows), set(expected_rows))


if __name__ == '__main__':
    unittest.main()
