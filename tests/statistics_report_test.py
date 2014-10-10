#!/usr/bin/env python3

import io
import unittest

import tacl
from .tacl_test_case import TaclTestCase


class ReportTestCase (TaclTestCase):

    def test_generate_statistics (self):
        input_results = (
            ['AB', '2', 'a', 'base', '1', 'A'],
            ['ABD', '3', 'a', 'base', '1', 'A'],
            ['ABCD', '4', 'a', 'base', '2', 'A'],
            ['ABC', '3', 'b', 'base', '2', 'B'],
            ['ABC', '3', 'c', 'base', '3', 'A'])
        results_fh = self._create_csv(input_results)
        input_counts = (
            ['a', 'base', '2', '5', '30', '31', 'A'],
            ['a', 'base', '3', '7', '29', '31', 'A'],
            ['a', 'base', '4', '11', '28', '31', 'A'],
            ['b', 'base', '2', '29', '200', '201', 'B'],
            ['b', 'base', '3', '42', '199', '201', 'B'],
            ['b', 'base', '4', '121', '198', '201', 'B'],
            ['c', 'base', '2', '9', '42', '43', 'A'],
            ['c', 'base', '3', '11', '41', '43', 'A'],
            ['c', 'base', '4', '12', '40', '43', 'A']
            )
        counts_fh = self._create_csv(input_counts,
                                     tacl.constants.COUNTS_FIELDNAMES)
        report = tacl.StatisticsReport(results_fh, counts_fh)
        report.generate_statistics()
        expected_rows = [
            ('a', 'base', '13', '31', str(13 / 31 * 100), 'A'),
            ('b', 'base', '6', '201', str(6 / 201 * 100), 'B'),
            ('c', 'base', '9', '43', str(9 / 43 * 100), 'A')
            ]
        actual_rows = self._get_rows_from_csv(
            report.csv(io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_generate_statistics_zero_count (self):
        # A text may have no n-grams (usually by accident, but it's
        # not TACL's place to judge).
        input_results = (
            ['AB', '2', 'a', 'base', '1', 'A'],
            ['ABD', '3', 'a', 'base', '1', 'A'],
            ['ABCD', '4', 'a', 'base', '2', 'A'])
        results_fh = self._create_csv(input_results)
        input_counts = (
            ['a', 'base', '2', '5', '30', '31', 'A'],
            ['a', 'base', '3', '7', '29', '31', 'A'],
            ['a', 'base', '4', '11', '28', '31', 'A'],
            ['b', 'base', '2', '0', '-1', '0', 'A'])
        counts_fh = self._create_csv(input_counts,
                                     tacl.constants.COUNTS_FIELDNAMES)
        report = tacl.StatisticsReport(results_fh, counts_fh)
        report.generate_statistics()
        # Why are the values 13.0 and 0.0 here, but not in the test
        # above?
        expected_rows = [
            ('a', 'base', '13.0', '31', str(13 / 31 * 100), 'A'),
            ('b', 'base', '0.0', '0', 'inf', 'A')]
        actual_rows = self._get_rows_from_csv(
            report.csv(io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))


if __name__ == '__main__':
    unittest.main()
