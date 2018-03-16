#!/usr/bin/env python3

import os
import unittest


import tacl
from ..tacl_test_case import TaclTestCase


class ResultsIntegrationTestCase (TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'results_data')
        self._stripped_dir = os.path.join(self._data_dir, 'stripped')
        self._tokenizer = tacl.Tokenizer(
            tacl.constants.TOKENIZER_PATTERN_CBETA,
            tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_add_label_count(self):
        results = os.path.join(self._data_dir, 'non-label-count-results.csv')
        command = 'tacl results --add-label-count {}'.format(results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'label-count-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_add_label_work_count(self):
        results = os.path.join(self._data_dir,
                               'non-label-work-count-results.csv')
        command = 'tacl results --add-label-work-count {}'.format(results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'label-work-count-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_bifurcated_extend_empty_results(self):
        results = os.path.join(self._data_dir, 'empty-results.csv')
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = os.path.join(data_dir, 'stripped')
        command = 'tacl results -b {} --max-be-count 10 {}'.format(
            corpus, results)
        actual_rows = self._get_rows_from_command(command)
        fieldnames = tuple(list(tacl.constants.QUERY_FIELDNAMES[:]) +
                           [tacl.constants.LABEL_COUNT_FIELDNAME])
        expected_rows = [fieldnames]
        self.assertEqual(actual_rows, expected_rows)

    def test_bifurcated_extend_malformed_results(self):
        fieldnames = [
            tacl.constants.NGRAM_FIELDNAME, tacl.constants.SIZE_FIELDNAME,
            tacl.constants.WORK_FIELDNAME, tacl.constants.SIGLUM_FIELDNAME,
            tacl.constants.LABEL_FIELDNAME
        ]
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = tacl.Corpus(os.path.join(data_dir, 'stripped'),
                             self._tokenizer)
        self._test_required_columns(fieldnames, 'bifurcated_extend', corpus, 2)

    def test_collapse_witnesses(self):
        results = os.path.join(self._data_dir,
                               'non-collapse-witnesses-results.csv')
        command = 'tacl results --collapse-witnesses {}'.format(results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'collapse-witnesses-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_excise(self):
        results = os.path.join(self._data_dir, 'non-excise-results.csv')
        command = 'tacl results --excise {} {}'.format('de', results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir, 'excise-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_extend_cbeta(self):
        results = os.path.join(self._data_dir, 'cbeta-non-extend-results.csv')
        command = 'tacl results -e {} -t {} {}'.format(
            os.path.join(self._stripped_dir, 'cbeta'),
            tacl.constants.TOKENIZER_CHOICE_CBETA, results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'cbeta-extend-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_extend_pagel(self):
        results = os.path.join(self._data_dir, 'pagel-non-extend-results.csv')
        command = 'tacl results -e {} -t {} {}'.format(
            os.path.join(self._stripped_dir, 'pagel'),
            tacl.constants.TOKENIZER_CHOICE_PAGEL, results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'pagel-extend-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_extend_multiply_labelled(self):
        # Test that a witness that exists under more than one label is
        # properly extended.
        results = os.path.join(self._data_dir,
                               'multiply-labelled-non-extend-results.csv')
        command = 'tacl results -e {} -t {} {}'.format(
            os.path.join(self._stripped_dir, 'multiply-labelled'),
            tacl.constants.TOKENIZER_CHOICE_CBETA, results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'multiply-labelled-extend-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_extend_diff(self):
        # Test that diff results are correctly extended.
        results = os.path.join(self._data_dir, 'diff-non-extend-results.csv')
        command = 'tacl results -e {} -t {} {}'.format(
            os.path.join(self._stripped_dir, 'diff-extend'),
            tacl.constants.TOKENIZER_CHOICE_CBETA, results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'diff-extend-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_extend_empty_results(self):
        results = os.path.join(self._data_dir, 'empty-results.csv')
        command = 'tacl results -e {} {}'.format(
            os.path.join(self._stripped_dir, 'cbeta'), results)
        actual_rows = self._get_rows_from_command(command)
        expected_rows = self._get_rows_from_file(results)
        self.assertEqual(actual_rows, expected_rows)

    def test_extend_malformed_results(self):
        fieldnames = [
            tacl.constants.NGRAM_FIELDNAME, tacl.constants.SIZE_FIELDNAME,
            tacl.constants.WORK_FIELDNAME, tacl.constants.SIGLUM_FIELDNAME,
            tacl.constants.LABEL_FIELDNAME
        ]
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = tacl.Corpus(os.path.join(data_dir, 'stripped'),
                             self._tokenizer)
        self._test_required_columns(fieldnames, 'extend', corpus)

    def test_extend_no_duplicate_index_values(self):
        # Extend should not leave the matches with duplicate values in
        # the index, potentially raising a "cannot reindex from a
        # duplicate axis" ValueError when followed by another
        # operation.
        input_data = os.path.join(self._data_dir,
                                  'cbeta-non-extend-results.csv')
        corpus = tacl.Corpus(os.path.join(self._stripped_dir, 'cbeta'),
                             self._tokenizer)
        results = tacl.Results(input_data, self._tokenizer)
        results.extend(corpus)
        self.assertFalse(
            results._matches.index.has_duplicates,
            'Results._matches DataFrame is left with duplicate index values.')

    def test_group_by_ngram(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        catalogue = os.path.join(data_dir, 'catalogue3.txt')
        results = os.path.join(self._data_dir, 'search-results.csv')
        command = 'tacl results --group-by-ngram {} {}'.format(
            catalogue, results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'search-group-by-ngram-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(actual_rows, expected_rows)

    def test_group_by_witness(self):
        results = os.path.join(self._data_dir, 'search-results.csv')
        command = 'tacl results --group-by-witness {}'.format(results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'search-group-by-witness-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_zero_fill(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = os.path.join(data_dir, 'stripped')
        results = os.path.join(self._data_dir, 'non-zero-fill-results.csv')
        command = 'tacl results -z {} {}'.format(corpus, results)
        actual_rows = self._get_rows_from_command(command)
        expected_results = os.path.join(self._data_dir,
                                        'zero-fill-results.csv')
        expected_rows = self._get_rows_from_file(expected_results)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_zero_fill_empty_results(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = os.path.join(data_dir, 'stripped')
        results = os.path.join(self._data_dir, 'empty-results.csv')
        command = 'tacl results -z {} {}'.format(corpus, results)
        actual_rows = self._get_rows_from_command(command)
        expected_rows = self._get_rows_from_file(results)
        self.assertEqual(actual_rows, expected_rows)

    def test_zero_fill_malformed_results(self):
        fieldnames = [
            tacl.constants.NGRAM_FIELDNAME, tacl.constants.SIZE_FIELDNAME,
            tacl.constants.WORK_FIELDNAME, tacl.constants.SIGLUM_FIELDNAME,
            tacl.constants.LABEL_FIELDNAME
        ]
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = tacl.Corpus(os.path.join(data_dir, 'stripped'),
                             self._tokenizer)
        self._test_required_columns(fieldnames, 'zero_fill', corpus)

    def test_zero_fill_no_duplicate_index_values(self):
        # Zero fill should not leave the matches with duplicate values
        # in the index, potentially raising a "cannot reindex from a
        # duplicate axis" ValueError when followed by another
        # operation.
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        corpus = tacl.Corpus(os.path.join(data_dir, 'stripped'),
                             self._tokenizer)
        input_file = os.path.join(self._data_dir, 'non-zero-fill-results.csv')
        results = tacl.Results(input_file, self._tokenizer)
        results.zero_fill(corpus)
        self.assertFalse(
            results._matches.index.has_duplicates,
            'Results._matches DataFrame is left with duplicate index values.')


if __name__ == '__main__':
    unittest.main()
