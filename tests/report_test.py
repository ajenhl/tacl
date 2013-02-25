#!/usr/bin/env python3

import csv
import io
import unittest

import tacl


class ReportTestCase (unittest.TestCase):

    def _create_csv (self, data):
        fh = io.StringIO(newline='')
        writer = csv.writer(fh)
        for row in data:
            writer.writerow(row)
        fh.seek(0)
        return fh

    def _get_rows_from_csv (self, fh):
        rows = set()
        reader = csv.reader(fh)
        for row in reader:
            rows.add(tuple(row))
        return rows

    def test_reduce (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'A'], ['ABCD', '4', 'a', '2', 'A'],
            ['AB', '2', 'b', '2', 'A'], ['ABC', '3', 'b', '2', 'A'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.reduce()
        expected_rows = set(
            (('AB', '2', 'a', '1', 'A'), ('ABD', '3', 'a', '1', 'A'),
             ('ABCD', '4', 'a', '2', 'A'), ('ABC', '3', 'b', '2', 'A')))
        actual_rows = self._get_rows_from_csv(report.csv())
        self.assertEqual(actual_rows, expected_rows)

    def test_remove_label (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'B'], ['ABCD', '4', 'a', '2', 'B'],
            ['AB', '2', 'b', '2', 'AB'], ['ABC', '3', 'b', '2', 'AB'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.remove_label('B')
        expected_rows = set(
            (('AB', '2', 'a', '4', 'A'), ('ABC', '3', 'a', '2', 'A'),
             ('AB', '2', 'b', '2', 'AB'), ('ABC', '3', 'b', '2', 'AB')))
        actual_rows = self._get_rows_from_csv(report.csv())
        self.assertEqual(actual_rows, expected_rows)

    def test_sort (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'B'], ['ABCD', '4', 'a', '2', 'B'],
            ['AB', '2', 'b', '2', 'AB'], ['ABC', '3', 'b', '2', 'AB'],
            ['ABC', '3', 'c', '3', 'A'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.sort()
        expected_rows = [['ABCD', '4', 'a', '2', 'B'],
                         ['ABC', '3', 'c', '3', 'A'],
                         ['ABC', '3', 'a', '2', 'A'],
                         ['ABC', '3', 'b', '2', 'AB'],
                         ['ABD', '3', 'a', '1', 'B'],
                         ['AB', '2', 'a', '4', 'A'],
                         ['AB', '2', 'b', '2', 'AB']]
        actual_rows = [row for row in csv.reader(report.csv())]
        self.assertEqual(actual_rows, expected_rows)


if __name__ == '__main__':
    unittest.main()
