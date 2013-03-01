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

    def test_prune (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'A'], ['ABCD', '4', 'a', '2', 'A'],
            ['AB', '2', 'b', '2', 'A'], ['ABC', '3', 'b', '2', 'A'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.prune(minimum=3)
        expected_rows = set((
            ('ABC', '3', 'a', '2', 'A'), ('ABD', '3', 'a', '1', 'A'),
            ('ABCD', '4', 'a', '2', 'A'), ('ABC', '3', 'b', '2', 'A')))
        actual_rows = self._get_rows_from_csv(report.csv())
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune(maximum=3)
        expected_rows = set((
                ('AB', '2', 'a', '4', 'A'), ('ABC', '3', 'a', '2', 'A'),
                ('ABD', '3', 'a', '1', 'A'), ('AB', '2', 'b', '2', 'A'),
                ('ABC', '3', 'b', '2', 'A')))
        actual_rows = self._get_rows_from_csv(report.csv())
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune(minimum=3, maximum=3)
        expected_rows = set((
                ('ABC', '3', 'a', '2', 'A'), ('ABD', '3', 'a', '1', 'A'),
                ('ABC', '3', 'b', '2', 'A')))
        actual_rows = self._get_rows_from_csv(report.csv())
        self.assertEqual(actual_rows, expected_rows)

    def test_reduce (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'A'], ['ABCD', '4', 'a', '2', 'A'],
            ['AB', '2', 'b', '2', 'A'], ['ABC', '3', 'b', '2', 'A'])
        expected_rows = set(
            (('AB', '2', 'a', '1', 'A'), ('ABD', '3', 'a', '1', 'A'),
             ('ABCD', '4', 'a', '2', 'A'), ('ABC', '3', 'b', '2', 'A')))
        actual_rows = self._perform_reduce(input_data)
        self.assertEqual(actual_rows, expected_rows)
        # Overlapping n-grams are trickier. Take the intersection of
        # two texts:
        #     ABABABCABDA and ABABABEABFA
        input_data = (
            ['ABABAB', '6', 'text1', '1', 'C1'],
            ['ABABA', '5', 'text1', '1', 'C1'],
            ['BABAB', '5', 'text1', '1', 'C1'],
            ['ABAB', '4', 'text1', '2', 'C1'],
            ['BABA', '4', 'text1', '1', 'C1'],
            ['ABA', '3', 'text1', '2', 'C1'],
            ['BAB', '3', 'text1', '2', 'C1'],
            ['AB', '2', 'text1', '4', 'C1'],
            ['BA', '2', 'text1', '2', 'C1'],
            ['A', '1', 'text1', '5', 'C1'],
            ['B', '1', 'text1', '4', 'C1'])
        expected_rows = set(
            (('ABABAB', '6', 'text1', '1', 'C1'),
             ('AB', '2', 'text1', '1', 'C1'),
             ('A', '1', 'text1', '1', 'C1')))
        actual_rows = self._perform_reduce(input_data)
        self.assertEqual(actual_rows, expected_rows)
        # An n-gram that consists of a single repeated token is a form
        # of overlapping. Take the intersection of two texts:
        #     AAAAABAAAACAAADAAEA and AAAAAFAAAAGAAAHAAIA
        input_data = (
            ['AAAAA', '5', 'text1', '1', 'C1'],
            ['AAAA', '4', 'text1', '3', 'C1'],
            ['AAA', '3', 'text1', '6', 'C1'],
            ['AA', '2', 'text1', '10', 'C1'],
            ['A', '1', 'text1', '15', 'C1'],
            ['AAAAA', '5', 'text2', '1', 'C2'],
            ['AAAA', '4', 'text2', '3', 'C2'],
            ['AAA', '3', 'text2', '6', 'C2'],
            ['AA', '2', 'text2', '10', 'C2'],
            ['A', '1', 'text2', '15', 'C2'])
        expected_rows = set(
            (('AAAAA', '5', 'text1', '1', 'C1'),
             ('AAAA', '4', 'text1', '1', 'C1'),
             ('AAA', '3', 'text1', '1', 'C1'),
             ('AA', '2', 'text1', '1', 'C1'),
             ('A', '1', 'text1', '1', 'C1'),
             ('AAAAA', '5', 'text2', '1', 'C2'),
             ('AAAA', '4', 'text2', '1', 'C2'),
             ('AAA', '3', 'text2', '1', 'C2'),
             ('AA', '2', 'text2', '1', 'C2'),
             ('A', '1', 'text2', '1', 'C2')))
        actual_rows = self._perform_reduce(input_data)
        self.assertEqual(actual_rows, expected_rows)
        # If the token is more than a single character, the case is
        # even more pathological. [...] is a single token.
        #     [A][A][A]B[A][A]C[A] and [A][A][A]D[A][A]E[A]
        input_data = (
            ['[A][A][A]', '3', 'text1', '1', 'C1'],
            ['[A][A]', '2', 'text1', '3', 'C1'],
            ['[A]', '1', 'text1', '6', 'C1'])
        expected_rows = set(
            (('[A][A][A]', '3', 'text1', '1', 'C1'),
             ('[A][A]', '2', 'text1', '1', 'C1'),
             ('[A]', '1', 'text1', '1', 'C1')))
        actual_rows = self._perform_reduce(input_data)
        self.assertEqual(actual_rows, expected_rows)

    def _perform_reduce (self, input_data):
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.reduce()
        return self._get_rows_from_csv(report.csv())

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
