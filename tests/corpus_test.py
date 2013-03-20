#!/usr/bin/env python3

import csv
import io
import unittest

import tacl


class CorpusTestCase (unittest.TestCase):

    def setUp (self):
        manager = tacl.DBManager(':memory:')
        self._corpus = tacl.Corpus('.', manager)

    def _create_csv (self, data):
        fh = io.StringIO(newline='')
        writer = csv.writer(fh)
        writer.writerow(tacl.constants.QUERY_FIELDNAMES)
        for row in data:
            writer.writerow(row)
        fh.seek(0)
        return fh

    def test_process_supplied_results (self):
        input_rows = [
            ('一言', '2', 'T0281.txt', '1', 'A'),
            ('入大乘', '3', 'T0281.txt', '1', 'A'),
            ('意識', '2', 'T0761.txt', '3', 'B'),
            ('以為', '2', 'T0603.txt', '2', 'B'),
            ('入大乘', '3', 'T0283.txt', '2', 'A'),
            ]
        input_csv = self._create_csv(input_rows)
        actual_ngrams, actual_labels = self._corpus.process_supplied_results(
            input_csv)
        expected_ngrams = ['一言', '入大乘', '意識', '以為']
        expected_labels = ['A', 'B']
        self.assertEqual(set(actual_ngrams), set(expected_ngrams))
        self.assertEqual(set(actual_labels), set(expected_labels))


if __name__ == '__main__':
    unittest.main()
