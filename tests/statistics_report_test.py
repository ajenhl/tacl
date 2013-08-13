#!/usr/bin/env python3

import io
import unittest

import tacl
from .tacl_test_case import TaclTestCase


class ReportTestCase (TaclTestCase):

    def test_generate_statistics (self):
        input_results = (
            ['AB', '2', 'a', '1', 'A'], ['ABD', '3', 'a', '1', 'A'],
            ['ABCD', '4', 'a', '2', 'A'], ['ABC', '3', 'b', '2', 'B'],
            ['ABC', '3', 'c', '3', 'A'])
        results_fh = self._create_csv(input_results)
        input_counts = (
            ['a', '2', '5', '30', 'A'],
            ['a', '3', '7', '29', 'A'],
            ['a', '4', '11', '28', 'A'],
            ['b', '2', '29', '200', 'B'],
            ['b', '3', '42', '199', 'B'],
            ['b', '4', '121', '198', 'B'],
            ['c', '2', '9', '42', 'A'],
            ['c', '3', '11', '41', 'A'],
            ['c', '4', '12', '40', 'A']
            )
        counts_fh = self._create_csv(input_counts,
                                     tacl.constants.COUNTS_FIELDNAMES)
        report = tacl.StatisticsReport(results_fh, counts_fh)
        report.generate_statistics()
        expected_rows = [
            ('a', '13', '31', str(13 / 31 * 100), 'A'),
            ('b', '6', '201', str(6 / 201 * 100), 'B'),
            ('c', '9', '43', str(9 / 43 * 100), 'A')
            ]
        actual_rows = self._get_rows_from_csv(
            report.csv(io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_generate_statistics_zero_count (self):
        # A text may have no n-grams (usually by accident, but it's
        # not TACL's place to judge). This should lead to zeroes in
        # the statistics entry for that text.
        input_results = ([])
        results_fh = self._create_csv(input_results)
        input_counts = (
            ['a', '2', '0', '-1', 'A'],
            )
        counts_fh = self._create_csv(input_counts,
                                     tacl.constants.COUNTS_FIELDNAMES)
        report = tacl.StatisticsReport(results_fh, counts_fh)
        report.generate_statistics()
        expected_rows = [
            ('a', '0', '0', '0', 'A'),
            ]
        actual_rows = self._get_rows_from_csv(
            report.csv(io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))


if __name__ == '__main__':
    unittest.main()
