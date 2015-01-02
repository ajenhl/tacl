#!/usr/bin/env python3

import io
import os
import unittest

import tacl
from ..tacl_test_case import TaclTestCase


class StatisticsReportIntegrationTestCase (TaclTestCase):

    def setUp (self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'stats_data')
        self._stripped_dir = os.path.join(self._data_dir, 'stripped')

    def test_generate_statistics (self):
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                   tacl.constants.TOKENIZER_JOINER_CBETA)
        corpus = tacl.Corpus(self._stripped_dir, tokenizer)
        input_results = (
            # Test two n-grams that overlap.
            ['he', '2', 'a', 'base', '1', 'A'],
            ['th', '2', 'a', 'base', '1', 'A'],
            # Test a single n-gram that overlaps itself. Also
            # alternate witness.
            ['heh', '3', 'a', 'v1', '2', 'A'],
            ['AB', '2', 'b', 'base', '1', 'B'],
            ['ABD', '3', 'b', 'base', '1', 'B'],
            ['ABCD', '4', 'b', 'base', '2', 'B'],
            )
        results_fh = self._create_csv(input_results)
        report = tacl.StatisticsReport(corpus, tokenizer, results_fh)
        report.generate_statistics()
        actual_results = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        expected_results = [
            ('a', 'base', '3', '3', '100.0', 'A'),
            ('a', 'v1', '5', '6', str(5 / 6 * 100), 'A'),
            ('b', 'base', '13', '14', str(13 / 14 * 100), 'B'),
        ]
        self.assertEqual(set(actual_results), set(expected_results))


if __name__ == '__main__':
    unittest.main()
