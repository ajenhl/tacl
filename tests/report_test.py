#!/usr/bin/env python3

import io
import unittest

import tacl
from .tacl_test_case import TaclTestCase


class ReportTestCase (TaclTestCase):

    def test_generate_statistics (self):
        input_results = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'A'], ['ABCD', '4', 'a', '2', 'A'],
            ['AB', '2', 'b', '2', 'B'], ['ABC', '3', 'b', '2', 'B'],
            ['AB', '2', 'c', '3', 'A'], ['ABC', '3', 'c', '3', 'A'])
        fh = self._create_csv(input_results)
        report = tacl.Report(fh)
        input_count = (
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
        count_fh = self._create_csv(input_count,
                                    tacl.constants.COUNTS_FIELDNAMES)
        report.generate_statistics(count_fh)
        expected_rows = [
            ('a', '13', str(13 / 31 * 100), 'A'),
            ('b', '6', str(6 / 201 * 100), 'B'),
            ('c', '9', str(9 / 43 * 100), 'A')
            ]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline=''), tacl.constants.STATISTICS_FIELDNAMES))
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_prune_by_ngram_count (self):
        input_data = (
            ['AB', '2', 'a', '7', 'A'], ['BA', '2', 'a', '1', 'A'],
            ['BA', '2', 'b', '3', 'B'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.prune_by_ngram_count(minimum=3)
        expected_rows = [
            ('AB', '2', 'a', '7', 'A'), ('BA', '2', 'a', '1', 'A'),
            ('BA', '2', 'b', '3', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune_by_ngram_count(maximum=4)
        expected_rows = [('BA', '2', 'a', '1', 'A'), ('BA', '2', 'b', '3', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune_by_ngram_count(minimum=4, maximum=5)
        expected_rows = [('BA', '2', 'a', '1', 'A'), ('BA', '2', 'b', '3', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_prune_by_ngram_size (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'A'], ['ABCD', '4', 'a', '2', 'A'],
            ['AB', '2', 'b', '2', 'A'], ['ABC', '3', 'b', '2', 'A'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.prune_by_ngram_size(minimum=3)
        expected_rows = [
            ('ABC', '3', 'a', '2', 'A'), ('ABD', '3', 'a', '1', 'A'),
            ('ABCD', '4', 'a', '2', 'A'), ('ABC', '3', 'b', '2', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune_by_ngram_size(maximum=3)
        expected_rows = [
            ('AB', '2', 'a', '4', 'A'), ('ABC', '3', 'a', '2', 'A'),
            ('ABD', '3', 'a', '1', 'A'), ('AB', '2', 'b', '2', 'A'),
            ('ABC', '3', 'b', '2', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune_by_ngram_size(minimum=3, maximum=3)
        expected_rows = [
            ('ABC', '3', 'a', '2', 'A'), ('ABD', '3', 'a', '1', 'A'),
            ('ABC', '3', 'b', '2', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_prune_by_text_count (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['AB', '2', 'b', '7', 'A'],
            ['AB', '2', 'c', '1', 'A'], ['AB', '2', 'd', '3', 'A'],
            ['ABC', '3', 'a', '3', 'A'], ['ABC', '3', 'b', '5', 'A'],
            ['ABC', '3', 'c', '1', 'A'], ['BA', '2', 'a', '6', 'A'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.prune_by_text_count(minimum=3)
        expected_rows = [
            ('AB', '2', 'a', '4', 'A'), ('AB', '2', 'b', '7', 'A'),
            ('AB', '2', 'c', '1', 'A'), ('AB', '2', 'd', '3', 'A'),
            ('ABC', '3', 'a', '3', 'A'), ('ABC', '3', 'b', '5', 'A'),
            ('ABC', '3', 'c', '1', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune_by_text_count(maximum=3)
        expected_rows = [
            ('ABC', '3', 'a', '3', 'A'), ('ABC', '3', 'b', '5', 'A'),
            ('ABC', '3', 'c', '1', 'A'), ('BA', '2', 'a', '6', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh)
        report.prune_by_text_count(minimum=2, maximum=3)
        expected_rows = [
            ('ABC', '3', 'a', '3', 'A'), ('ABC', '3', 'b', '5', 'A'),
            ('ABC', '3', 'c', '1', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_reciprocal_remove (self):
        input_data = (
            ['AB', '2', 'a', '5', 'A'], ['ABCDEF', '6', 'a', '7', 'A'],
            ['DEF', '3', 'a', '2', 'A'], ['GHIJ', '4', 'a', '3', 'A'],
            ['ABCDEF', '6', 'b', '3', 'B'], ['GHIJ', '4', 'b', '2', 'B'],
            ['KLM', '3', 'b', '17', 'B'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.reciprocal_remove()
        expected_rows = [
            ('ABCDEF', '6', 'a', '7', 'A'), ('GHIJ', '4', 'a', '3', 'A'),
            ('ABCDEF', '6', 'b', '3', 'B'), ('GHIJ', '4', 'b', '2', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        # More than two labels, and more than one text per label.
        input_data = (
            ['AB', '2', 'a', '5', 'A'], ['ABCDEF', '6', 'a', '7', 'A'],
            ['DEF', '3', 'a', '2', 'A'], ['AB', '2', 'b', '6', 'A'],
            ['GHIJ', '4', 'b', '3', 'A'], ['ABCDEF', '6', 'c', '3', 'B'],
            ['KLM', '3', 'c', '17', 'B'], ['GHIJ', '4', 'd', '2', 'B'],
            ['KLM', '3', 'e', '3', 'C'], ['GHIJ', '4', 'f', '11', 'C'],
            ['ABCDEF', '6', 'g', '8', 'C'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.reciprocal_remove()
        expected_rows = [
            ('ABCDEF', '6', 'a', '7', 'A'), ('GHIJ', '4', 'b', '3', 'A'),
            ('ABCDEF', '6', 'c', '3', 'B'), ('GHIJ', '4', 'd', '2', 'B'),
            ('GHIJ', '4', 'f', '11', 'C'), ('ABCDEF', '6', 'g', '8', 'C')]
        actual_rows = self._get_rows_from_csv(report.csv(
                io.StringIO(newline='')))
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
        self.assertEqual(set(actual_rows), expected_rows)
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
        self.assertEqual(set(actual_rows), expected_rows)
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
        self.assertEqual(set(actual_rows), expected_rows)
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
        self.assertEqual(set(actual_rows), expected_rows)

    def _perform_reduce (self, input_data):
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.reduce()
        return self._get_rows_from_csv(report.csv(io.StringIO(newline='')))

    def test_remove_label (self):
        input_data = (
            ['AB', '2', 'a', '4', 'A'], ['ABC', '3', 'a', '2', 'A'],
            ['ABD', '3', 'a', '1', 'B'], ['ABCD', '4', 'a', '2', 'B'],
            ['AB', '2', 'b', '2', 'AB'], ['ABC', '3', 'b', '2', 'AB'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh)
        report.remove_label('B')
        expected_rows = [
            ('AB', '2', 'a', '4', 'A'), ('ABC', '3', 'a', '2', 'A'),
            ('AB', '2', 'b', '2', 'AB'), ('ABC', '3', 'b', '2', 'AB')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
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
        expected_rows = [
            ('ABCD', '4', 'a', '2', 'B'), ('ABC', '3', 'c', '3', 'A'),
            ('ABC', '3', 'a', '2', 'A'), ('ABC', '3', 'b', '2', 'AB'),
            ('ABD', '3', 'a', '1', 'B'), ('AB', '2', 'a', '4', 'A'),
            ('AB', '2', 'b', '2', 'AB')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)


if __name__ == '__main__':
    unittest.main()
