#!/usr/bin/env python3

import io
import os
import unittest

import tacl
from .tacl_test_case import TaclTestCase


class ReportTestCase (TaclTestCase):

    def setUp (self):
        self._tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                         tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_prune_by_ngram_count (self):
        input_data = (
            ['AB', '2', 'a', 'base', '7', 'A'],
            ['BA', '2', 'a', 'wit', '1', 'A'],
            ['BA', '2', 'b', 'base', '3', 'B'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_ngram_count(minimum=3)
        expected_rows = [
            ('AB', '2', 'a', 'base', '7', 'A'),
            ('BA', '2', 'a', 'wit', '1', 'A'),
            ('BA', '2', 'b', 'base', '3', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_ngram_count(maximum=4)
        expected_rows = [('BA', '2', 'a', 'wit', '1', 'A'),
                         ('BA', '2', 'b', 'base', '3', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_ngram_count(minimum=4, maximum=5)
        expected_rows = [('BA', '2', 'a', 'wit', '1', 'A'),
                         ('BA', '2', 'b', 'base', '3', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_prune_by_ngram_size (self):
        input_data = (
            ['AB', '2', 'a', 'base', '4', 'A'],
            ['ABC', '3', 'a', 'base', '2', 'A'],
            ['ABD', '3', 'a', 'wit', '1', 'A'],
            ['ABCD', '4', 'a', 'base', '2', 'A'],
            ['AB', '2', 'b', 'base', '2', 'A'],
            ['ABC', '3', 'b', 'wit', '2', 'A'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_ngram_size(minimum=3)
        expected_rows = [
            ('ABC', '3', 'a', 'base', '2', 'A'),
            ('ABD', '3', 'a', 'wit', '1', 'A'),
            ('ABCD', '4', 'a', 'base', '2', 'A'),
            ('ABC', '3', 'b', 'wit', '2', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_ngram_size(maximum=3)
        expected_rows = [
            ('AB', '2', 'a', 'base', '4', 'A'),
            ('ABC', '3', 'a', 'base', '2', 'A'),
            ('ABD', '3', 'a', 'wit', '1', 'A'),
            ('AB', '2', 'b', 'base', '2', 'A'),
            ('ABC', '3', 'b', 'wit', '2', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_ngram_size(minimum=3, maximum=3)
        expected_rows = [
            ('ABC', '3', 'a', 'base', '2', 'A'),
            ('ABD', '3', 'a', 'wit', '1', 'A'),
            ('ABC', '3', 'b', 'wit', '2', 'A')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_prune_by_text_count (self):
        input_data = (
            ['AB', '2', 'a', 'base', '4', 'A'],
            ['AB', '2', 'b', 'base', '7', 'A'],
            ['AB', '2', 'c', 'base', '1', 'B'],
            ['AB', '2', 'd', 'base', '3', 'B'],
            ['ABC', '3', 'a', 'base', '3', 'A'],
            ['ABC', '3', 'b', 'base', '5', 'A'],
            ['ABC', '3', 'c', 'base', '1', 'B'],
            ['BA', '2', 'a', 'base', '6', 'A'],
            ['B', '1', 'a', 'base', '5', 'A'],
            ['B', '1', 'b', 'base', '3', 'A'],
            ['B', '1', 'b', 'wit', '3', 'A'],
            ['B', '1', 'c', 'base', '0', 'B'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_text_count(minimum=3)
        expected_rows = [
            ('AB', '2', 'a', 'base', '4', 'A'),
            ('AB', '2', 'b', 'base', '7', 'A'),
            ('AB', '2', 'c', 'base', '1', 'B'),
            ('AB', '2', 'd', 'base', '3', 'B'),
            ('ABC', '3', 'a', 'base', '3', 'A'),
            ('ABC', '3', 'b', 'base', '5', 'A'),
            ('ABC', '3', 'c', 'base', '1', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_text_count(maximum=3)
        expected_rows = [
            ('ABC', '3', 'a', 'base', '3', 'A'),
            ('ABC', '3', 'b', 'base', '5', 'A'),
            ('ABC', '3', 'c', 'base', '1', 'B'),
            ('BA', '2', 'a', 'base', '6', 'A'),
            ('B', '1', 'a', 'base', '5', 'A'),
            ('B', '1', 'b', 'base', '3', 'A'),
            ('B', '1', 'b', 'wit', '3', 'A'),
            ('B', '1', 'c', 'base', '0', 'B'),
        ]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)
        fh.seek(0)
        report = tacl.Report(fh, self._tokenizer)
        report.prune_by_text_count(minimum=2, maximum=3)
        expected_rows = [
            ('ABC', '3', 'a', 'base', '3', 'A'),
            ('ABC', '3', 'b', 'base', '5', 'A'),
            ('ABC', '3', 'c', 'base', '1', 'B'),
            ('B', '1', 'a', 'base', '5', 'A'),
            ('B', '1', 'b', 'base', '3', 'A'),
            ('B', '1', 'b', 'wit', '3', 'A'),
            ('B', '1', 'c', 'base', '0', 'B'),]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_reciprocal_remove (self):
        input_data = (
            ['AB', '2', 'a', 'base', '5', 'A'],
            ['ABCDEF', '6', 'a', 'base', '7', 'A'],
            ['DEF', '3', 'a', 'base', '2', 'A'],
            ['GHIJ', '4', 'a', 'base', '3', 'A'],
            ['KLM', '3', 'b', 'base', '0', 'A'],
            ['ABCDEF', '6', 'b', 'base', '3', 'B'],
            ['GHIJ', '4', 'b', 'base', '2', 'B'],
            ['KLM', '3', 'b', 'base', '17', 'B'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.reciprocal_remove()
        expected_rows = [
            ('ABCDEF', '6', 'a', 'base', '7', 'A'),
            ('GHIJ', '4', 'a', 'base', '3', 'A'),
            ('ABCDEF', '6', 'b', 'base', '3', 'B'),
            ('GHIJ', '4', 'b', 'base', '2', 'B')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))
        # More than two labels, and more than one text per label.
        input_data = (
            ['AB', '2', 'a', 'base', '5', 'A'],
            ['ABCDEF', '6', 'a', 'base', '7', 'A'],
            ['DEF', '3', 'a', 'base', '2', 'A'],
            ['AB', '2', 'b', 'base', '6', 'A'],
            ['GHIJ', '4', 'b', 'base', '3', 'A'],
            ['KLM', '3', 'b', 'base', '0', 'A'],
            ['ABCDEF', '6', 'c', 'base', '3', 'B'],
            ['KLM', '3', 'c', 'base', '17', 'B'],
            ['GHIJ', '4', 'd', 'base', '2', 'B'],
            ['KLM', '3', 'e', 'base', '3', 'C'],
            ['GHIJ', '4', 'f', 'base', '11', 'C'],
            ['ABCDEF', '6', 'g', 'base', '8', 'C'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.reciprocal_remove()
        expected_rows = [
            ('ABCDEF', '6', 'a', 'base', '7', 'A'),
            ('GHIJ', '4', 'b', 'base', '3', 'A'),
            ('ABCDEF', '6', 'c', 'base', '3', 'B'),
            ('GHIJ', '4', 'd', 'base', '2', 'B'),
            ('GHIJ', '4', 'f', 'base', '11', 'C'),
            ('ABCDEF', '6', 'g', 'base', '8', 'C')]
        actual_rows = self._get_rows_from_csv(report.csv(
                io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))
        # Now with variants.
        input_data = (
            ['AB', '2', 'a', 'base', '5', 'A'],
            ['ABCDEF', '6', 'a', 'wit1', '7', 'A'],
            ['DEF', '3', 'a', 'base', '2', 'A'],
            ['AB', '2', 'b', 'base', '6', 'A'],
            ['GHIJ', '4', 'b', 'base', '3', 'A'],
            ['KLM', '3', 'b', 'base', '0', 'A'],
            ['ABCDEF', '6', 'c', 'base', '3', 'B'],
            ['KLM', '3', 'c', 'base', '17', 'B'],
            ['GHIJ', '4', 'd', 'base', '2', 'B'],
            ['KLM', '3', 'e', 'base', '3', 'C'],
            ['GHIJ', '4', 'f', 'wit2', '11', 'C'],
            ['ABCDEF', '6', 'g', 'base', '8', 'C'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.reciprocal_remove()
        expected_rows = [
            ('ABCDEF', '6', 'a', 'wit1', '7', 'A'),
            ('GHIJ', '4', 'b', 'base', '3', 'A'),
            ('ABCDEF', '6', 'c', 'base', '3', 'B'),
            ('GHIJ', '4', 'd', 'base', '2', 'B'),
            ('GHIJ', '4', 'f', 'wit2', '11', 'C'),
            ('ABCDEF', '6', 'g', 'base', '8', 'C')]
        actual_rows = self._get_rows_from_csv(report.csv(
                io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_reduce_cbeta (self):
        tokenizer = self._tokenizer
        input_data = (
            ['AB', '2', 'a', 'base', '4', 'A'],
            ['ABC', '3', 'a', 'base', '2', 'A'],
            ['ABD', '3', 'a', 'base', '1', 'A'],
            ['ABCD', '4', 'a', 'base', '2', 'A'],
            ['AB', '2', 'b', 'base', '2', 'A'],
            ['ABC', '3', 'b', 'base', '2', 'A'],
            ['AB', '2', 'b', 'wit', '3', 'A'],
            ['ABC', '3', 'b', 'wit', '1', 'A'])
        expected_rows = set(
            (('AB', '2', 'a', 'base', '1', 'A'),
             ('ABD', '3', 'a', 'base', '1', 'A'),
             ('ABCD', '4', 'a', 'base', '2', 'A'),
             ('ABC', '3', 'b', 'base', '2', 'A'),
             ('AB', '2', 'b', 'wit', '2', 'A'),
             ('ABC', '3', 'b', 'wit', '1', 'A')))
        actual_rows = self._perform_reduce(input_data, tokenizer)
        self.assertEqual(set(actual_rows), expected_rows)
        # Overlapping n-grams are trickier. Take the intersection of
        # two texts:
        #     ABABABCABDA and ABABABEABFA
        input_data = (
            ['ABABAB', '6', 'text1', 'base', '1', 'C1'],
            ['ABABA', '5', 'text1', 'base', '1', 'C1'],
            ['BABAB', '5', 'text1', 'base', '1', 'C1'],
            ['ABAB', '4', 'text1', 'base', '2', 'C1'],
            ['BABA', '4', 'text1', 'base', '1', 'C1'],
            ['ABA', '3', 'text1', 'base', '2', 'C1'],
            ['BAB', '3', 'text1', 'base', '2', 'C1'],
            ['AB', '2', 'text1', 'base', '4', 'C1'],
            ['BA', '2', 'text1', 'base', '2', 'C1'],
            ['A', '1', 'text1', 'base', '5', 'C1'],
            ['B', '1', 'text1', 'base', '4', 'C1'])
        expected_rows = set(
            (('ABABAB', '6', 'text1', 'base', '1', 'C1'),
             ('AB', '2', 'text1', 'base', '1', 'C1'),
             ('A', '1', 'text1', 'base', '1', 'C1')))
        actual_rows = self._perform_reduce(input_data, tokenizer)
        self.assertEqual(set(actual_rows), expected_rows)
        # An n-gram that consists of a single repeated token is a form
        # of overlapping. Take the intersection of two texts:
        #     AAAAABAAAACAAADAAEA and AAAAAFAAAAGAAAHAAIA
        input_data = (
            ['AAAAA', '5', 'text1', 'base', '1', 'C1'],
            ['AAAA', '4', 'text1', 'base', '3', 'C1'],
            ['AAA', '3', 'text1', 'base', '6', 'C1'],
            ['AA', '2', 'text1', 'base', '10', 'C1'],
            ['A', '1', 'text1', 'base', '15', 'C1'],
            ['AAAAA', '5', 'text2', 'base', '1', 'C2'],
            ['AAAA', '4', 'text2', 'base', '3', 'C2'],
            ['AAA', '3', 'text2', 'base', '6', 'C2'],
            ['AA', '2', 'text2', 'base', '10', 'C2'],
            ['A', '1', 'text2', 'base', '15', 'C2'])
        expected_rows = set(
            (('AAAAA', '5', 'text1', 'base', '1', 'C1'),
             ('AAAA', '4', 'text1', 'base', '1', 'C1'),
             ('AAA', '3', 'text1', 'base', '1', 'C1'),
             ('AA', '2', 'text1', 'base', '1', 'C1'),
             ('A', '1', 'text1', 'base', '1', 'C1'),
             ('AAAAA', '5', 'text2', 'base', '1', 'C2'),
             ('AAAA', '4', 'text2', 'base', '1', 'C2'),
             ('AAA', '3', 'text2', 'base', '1', 'C2'),
             ('AA', '2', 'text2', 'base', '1', 'C2'),
             ('A', '1', 'text2', 'base', '1', 'C2')))
        actual_rows = self._perform_reduce(input_data, tokenizer)
        self.assertEqual(set(actual_rows), expected_rows)
        # If the token is more than a single character, the case is
        # even more pathological. [...] is a single token.
        #     [A][A][A]B[A][A]C[A] and [A][A][A]D[A][A]E[A]
        input_data = (
            ['[A][A][A]', '3', 'text1', 'base', '1', 'C1'],
            ['[A][A]', '2', 'text1', 'base', '3', 'C1'],
            ['[A]', '1', 'text1', 'base', '6', 'C1'])
        expected_rows = set(
            (('[A][A][A]', '3', 'text1', 'base', '1', 'C1'),
             ('[A][A]', '2', 'text1', 'base', '1', 'C1'),
             ('[A]', '1', 'text1', 'base', '1', 'C1')))
        actual_rows = self._perform_reduce(input_data, tokenizer)
        self.assertEqual(set(actual_rows), expected_rows)

    def test_reduce_nan (self):
        # Check that the n-gram "nan" is not interpreted as NaN.
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        input_data = (
            ['nan', '1', 'text1', 'base', '2', 'A'],
            ['nan dus', '2', 'text1', 'base', '1', 'A'],
            ['pa', '1', 'text2', 'base', '1', 'B'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, tokenizer)
        report.reduce()
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        expected_rows = (
            ('nan', '1', 'text1', 'base', '1', 'A'),
            ('nan dus', '2', 'text1', 'base', '1', 'A'),
            ('pa', '1', 'text2', 'base', '1', 'B'))
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_reduce_pagel (self):
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        input_data = (
            ['pa dus', '2', 'text1', 'base', '1', 'B'],
            ['pa dus gcig', '3', 'text1', 'base', '1', 'B'],
            ['pa dus gcig na', '4', 'text1', 'base', '1', 'B'],
            ['pa dus', '2', 'text1', 'wit', '2', 'B'],
            ['pa dus gcig', '3', 'text1', 'wit', '1', 'B'],
        )
        expected_rows = (
            ('pa dus', '2', 'text1', 'wit', '1', 'B'),
            ('pa dus gcig', '3', 'text1', 'wit', '1', 'B'),
            ('pa dus gcig na', '4', 'text1', 'base', '1', 'B'),
        )
        actual_rows = self._perform_reduce(input_data, tokenizer)
        self.assertEqual(set(actual_rows), set(expected_rows))

    def _perform_reduce (self, input_data, tokenizer):
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, tokenizer)
        report.reduce()
        return self._get_rows_from_csv(report.csv(io.StringIO(newline='')))

    def test_remove_label (self):
        input_data = (
            ['AB', '2', 'a', 'base', '4', 'A'],
            ['AB', '2', 'a', 'wit', '3', 'A'],
            ['ABC', '3', 'a', 'base', '2', 'A'],
            ['ABD', '3', 'a', 'base', '1', 'B'],
            ['ABCD', '4', 'a', 'base', '2', 'B'],
            ['AB', '2', 'b', 'base', '2', 'AB'],
            ['ABC', '3', 'b', 'base', '2', 'AB'],
            ['AB', '2', 'c', 'wit', '1', 'B'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.remove_label('B')
        expected_rows = [
            ('AB', '2', 'a', 'base', '4', 'A'),
            ('AB', '2', 'a', 'wit', '3', 'A'),
            ('ABC', '3', 'a', 'base', '2', 'A'),
            ('AB', '2', 'b', 'base', '2', 'AB'),
            ('ABC', '3', 'b', 'base', '2', 'AB')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_sort (self):
        input_data = (
            ['AB', '2', 'a', 'base', '4', 'A'],
            ['AB', '2', 'a', 'wit', '3', 'A'],
            ['ABC', '3', 'a', 'base', '2', 'A'],
            ['ABD', '3', 'a', 'base', '1', 'B'],
            ['ABCD', '4', 'a', 'base', '2', 'B'],
            ['AB', '2', 'b', 'base', '2', 'AB'],
            ['AB', '2', 'b', 'a', '2', 'AB'],
            ['ABC', '3', 'b', 'base', '2', 'AB'],
            ['ABC', '3', 'c', 'base', '3', 'A'])
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, self._tokenizer)
        report.sort()
        expected_rows = [
            ('ABCD', '4', 'a', 'base', '2', 'B'),
            ('ABC', '3', 'c', 'base', '3', 'A'),
            ('ABC', '3', 'a', 'base', '2', 'A'),
            ('ABC', '3', 'b', 'base', '2', 'AB'),
            ('ABD', '3', 'a', 'base', '1', 'B'),
            ('AB', '2', 'a', 'base', '4', 'A'),
            ('AB', '2', 'a', 'wit', '3', 'A'),
            ('AB', '2', 'b', 'a', '2', 'AB'),
            ('AB', '2', 'b', 'base', '2', 'AB')]
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        self.assertEqual(actual_rows, expected_rows)

    def test_zero_fill (self):
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                   tacl.constants.TOKENIZER_JOINER_CBETA)
        input_data = (
            ['AB', '2', 'T1', 'base', '7', 'A'],
            ['AB', '2', 'T2', 'a', '3', 'B'],
            ['ABC', '3', 'T5', 'base', '1', 'A'],
        )
        base_dir = os.path.dirname(__file__)
        stripped_dir = os.path.join(base_dir, 'integration_tests', 'data',
                                    'stripped')
        corpus = tacl.Corpus(stripped_dir, tokenizer)
        fh = self._create_csv(input_data)
        report = tacl.Report(fh, tokenizer)
        catalogue = {'T1': 'A', 'T2': 'B', 'T3': 'C', 'T5': 'A'}
        report.zero_fill(corpus, catalogue)
        actual_rows = self._get_rows_from_csv(report.csv(
            io.StringIO(newline='')))
        expected_rows = [
            ('AB', '2', 'T1', 'base', '7', 'A'),
            ('AB', '2', 'T1', 'a', '0', 'A'),
            ('AB', '2', 'T2', 'a', '3', 'B'),
            ('AB', '2', 'T2', 'base', '0', 'B'),
            ('ABC', '3', 'T5', 'base', '1', 'A'),
        ]
        self.assertEqual(set(actual_rows), set(expected_rows))


if __name__ == '__main__':
    unittest.main()
