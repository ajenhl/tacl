#!/usr/bin/env python3

import io
import os
import unittest

import tacl
from tacl_test_case import TaclTestCase


class CorpusTestCase (TaclTestCase):

    def setUp (self):
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'data')
        self._manager = tacl.DBManager(':memory:')
        self._corpus = tacl.Corpus(data_dir, self._manager)
        # generate_ngrams is tested indirectly through the tests of
        # the query methods; not ideal.
        self._corpus.generate_ngrams(1, 3, False)

    def test_counts (self):
        catalogue = tacl.Catalogue({'1.txt': 'A', '2.txt': 'B', '3.txt': 'C',
                                    '4.txt': 'D', '5.txt': 'A'})
        actual_rows = self._get_rows_from_csv(
            self._corpus.counts(catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('1.txt', '1', '5', '10', 'A'), ('1.txt', '2', '7', '9', 'A'),
            ('1.txt', '3', '8', '8', 'A'), ('2.txt', '1', '5', '11', 'B'),
            ('2.txt', '2', '7', '10', 'B'), ('2.txt', '3', '7', '9', 'B'),
            ('3.txt', '1', '3', '4', 'C'), ('3.txt', '2', '3', '3', 'C'),
            ('3.txt', '3', '2', '2', 'C'), ('4.txt', '1', '4', '5', 'D'),
            ('4.txt', '2', '4', '4', 'D'), ('4.txt', '3', '3', '3', 'D'),
            ('5.txt', '1', '3', '4', 'A'), ('5.txt', '2', '3', '3', 'A'),
            ('5.txt', '3', '2', '2', 'A')]
        self.assertEqual(actual_rows, expected_rows)

    def test_diff (self):
        catalogue = tacl.Catalogue({'1.txt': 'A', '2.txt': 'B', '3.txt': 'C',
                                    '5.txt': 'A'})
        actual_rows = self._get_rows_from_csv(
            self._corpus.diff(catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('w', '1', '1.txt', '2', 'A'), ('w', '1', '5.txt', '1', 'A'),
            ('s', '1', '2.txt', '2', 'B'), ('a', '1', '3.txt', '1', 'C'),
            ('l', '1', '5.txt', '2', 'A'), ('nw', '2', '1.txt', '1', 'A'),
            ('we', '2', '1.txt', '2', 'A'), ('we', '2', '5.txt', '1', 'A'),
            ('ew', '2', '1.txt', '1', 'A'), ('es', '2', '2.txt', '2', 'B'),
            ('se', '2', '2.txt', '2', 'B'), ('eh', '2', '2.txt', '1', 'B'),
            ('ha', '2', '3.txt', '1', 'C'), ('at', '2', '3.txt', '1', 'C'),
            ('el', '2', '5.txt', '1', 'A'), ('ll', '2', '5.txt', '1', 'A'),
            ('hen', '3', '1.txt', '1', 'A'), ('enw', '3', '1.txt', '1', 'A'),
            ('nwe', '3', '1.txt', '1', 'A'), ('wew', '3', '1.txt', '1', 'A'),
            ('ewe', '3', '1.txt', '1', 'A'), ('wen', '3', '1.txt', '1', 'A'),
            ('hes', '3', '2.txt', '2', 'B'), ('ese', '3', '2.txt', '2', 'B'),
            ('seh', '3', '2.txt', '1', 'B'), ('ehe', '3', '2.txt', '1', 'B'),
            ('sen', '3', '2.txt', '1', 'B'), ('tha', '3', '3.txt', '1', 'C'),
            ('hat', '3', '3.txt', '1', 'C'), ('wel', '3', '5.txt', '1', 'A'),
            ('ell', '3', '5.txt', '1', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_asymmetric (self):
        catalogue = tacl.Catalogue({'1.txt': 'A', '2.txt': 'B', '3.txt': 'C',
                                    '5.txt': 'A'})
        actual_rows = self._get_rows_from_csv(
            self._corpus.diff(catalogue, io.StringIO(newline=''),
                              prime_label='A'))
        expected_rows = [
            ('w', '1', '1.txt', '2', 'A'), ('w', '1', '5.txt', '1', 'A'),
            ('l', '1', '5.txt', '2', 'A'), ('nw', '2', '1.txt', '1', 'A'),
            ('we', '2', '1.txt', '2', 'A'), ('we', '2', '5.txt', '1', 'A'),
            ('ew', '2', '1.txt', '1', 'A'), ('el', '2', '5.txt', '1', 'A'),
            ('ll', '2', '5.txt', '1', 'A'), ('hen', '3', '1.txt', '1', 'A'),
            ('enw', '3', '1.txt', '1', 'A'), ('nwe', '3', '1.txt', '1', 'A'),
            ('wew', '3', '1.txt', '1', 'A'), ('ewe', '3', '1.txt', '1', 'A'),
            ('wen', '3', '1.txt', '1', 'A'), ('wel', '3', '5.txt', '1', 'A'),
            ('ell', '3', '5.txt', '1', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_supplied (self):
        catalogue = tacl.Catalogue({'1.txt': 'A', '2.txt': 'B', '3.txt': 'C',
                                    '5.txt': 'A'})
        # Input is intersection of A and B.
        input_rows = [
            ('t', '1', '1.txt', '2', 'A'), ('t', '1', '2.txt', '2', 'B'),
            ('h', '1', '1.txt', '1', 'A'), ('h', '1', '2.txt', '2', 'B'),
            ('e', '1', '1.txt', '3', 'A'), ('e', '1', '2.txt', '4', 'B'),
            ('e', '1', '5.txt', '1', 'A'), ('n', '1', '1.txt', '2', 'A'),
            ('n', '1', '2.txt', '1', 'B'), ('th', '2', '1.txt', '1', 'A'),
            ('th', '2', '2.txt', '1', 'B'), ('he', '2', '1.txt', '1', 'A'),
            ('he', '2', '2.txt', '2', 'B'), ('en', '2', '1.txt', '2', 'A'),
            ('en', '2', '2.txt', '1', 'B'), ('the', '3', '1.txt', '1', 'A'),
            ('the', '3', '2.txt', '1', 'B'), ('ent', '3', '1.txt', '1', 'A'),
            ('ent', '3', '2.txt', '1', 'B')]
        input_csv = self._create_csv(input_rows)
        actual_rows = self._get_rows_from_csv(
            self._corpus.diff(catalogue, io.StringIO(newline=''), input_csv))
        expected_rows = [
            ('e', '1', '1.txt', '3', 'A'), ('e', '1', '2.txt', '4', 'B'),
            ('e', '1', '5.txt', '1', 'A'), ('n', '1', '1.txt', '2', 'A'),
            ('n', '1', '2.txt', '1', 'B'), ('he', '2', '1.txt', '1', 'A'),
            ('he', '2', '2.txt', '2', 'B'), ('en', '2', '1.txt', '2', 'A'),
            ('en', '2', '2.txt', '1', 'B'), ('the', '3', '1.txt', '1', 'A'),
            ('the', '3', '2.txt', '1', 'B'), ('ent', '3', '1.txt', '1', 'A'),
            ('ent', '3', '2.txt', '1', 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection (self):
        catalogue = tacl.Catalogue({'1.txt': 'A', '2.txt': 'B', '3.txt': 'C',
                                    '5.txt': 'A'})
        actual_rows = self._get_rows_from_csv(
            self._corpus.intersection(catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('t', '1', '1.txt', '2', 'A'), ('t', '1', '2.txt', '2', 'B'),
            ('t', '1', '3.txt', '2', 'C'), ('h', '1', '1.txt', '1', 'A'),
            ('h', '1', '2.txt', '2', 'B'), ('h', '1', '3.txt', '1', 'C'),
            ('th', '2', '1.txt', '1', 'A'), ('th', '2', '2.txt', '1', 'B'),
            ('th', '2', '3.txt', '1', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_supplied (self):
        catalogue = tacl.Catalogue({'1.txt': 'A', '2.txt': 'B', '3.txt': 'C',
                                    '5.txt': 'A'})
        # Input is diff of B and C.
        input_rows = [
            ('e', '1', '2.txt', '4', 'B'), ('s', '1', '2.txt', '2', 'B'),
            ('n', '1', '2.txt', '1', 'B'), ('a', '1', '3.txt', '1', 'C'),
            ('he', '2', '2.txt', '2', 'B'), ('es', '2', '2.txt', '2', 'B'),
            ('se', '2', '2.txt', '2', 'B'), ('eh', '2', '2.txt', '1', 'B'),
            ('en', '2', '2.txt', '1', 'B'), ('nt', '2', '2.txt', '1', 'B'),
            ('ha', '2', '3.txt', '1', 'C'), ('at', '2', '3.txt', '1', 'C'),
            ('the', '3', '2.txt', '1', 'B'), ('hes', '3', '2.txt', '2', 'B'),
            ('ese', '3', '2.txt', '2', 'B'), ('seh', '3', '2.txt', '1', 'B'),
            ('ehe', '3', '2.txt', '1', 'B'), ('sen', '3', '2.txt', '1', 'B'),
            ('ent', '3', '2.txt', '1', 'B'), ('tha', '3', '3.txt', '1', 'C'),
            ('hat', '3', '3.txt', '1', 'C')]
        input_csv = self._create_csv(input_rows)
        actual_rows = self._get_rows_from_csv(
            self._corpus.intersection(catalogue, io.StringIO(newline=''),
                                      input_csv))
        expected_rows = [
            ('e', '1', '1.txt', '3', 'A'), ('e', '1', '2.txt', '4', 'B'),
            ('e', '1', '5.txt', '1', 'A'), ('n', '1', '1.txt', '2', 'A'),
            ('n', '1', '2.txt', '1', 'B'), ('he', '2', '1.txt', '1', 'A'),
            ('he', '2', '2.txt', '2', 'B'), ('en', '2', '1.txt', '2', 'A'),
            ('en', '2', '2.txt', '1', 'B'), ('nt', '2', '1.txt', '1', 'A'),
            ('nt', '2', '2.txt', '1', 'B'), ('the', '3', '1.txt', '1', 'A'),
            ('the', '3', '2.txt', '1', 'B'), ('ent', '3', '1.txt', '1', 'A'),
            ('ent', '3', '2.txt', '1', 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))

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

    def test_set_labels (self):
        label_query = 'SELECT label FROM Text GROUP BY label'
        labels = self._manager._conn.execute(label_query).fetchall()
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0][0], '')
        catalogue = tacl.Catalogue({'1.txt': 'A', '2.txt': 'B'})
        self._corpus._set_labels(catalogue)
        labels = self._manager._conn.execute(label_query).fetchall()
        self.assertEqual(len(labels), 3)
        text_query = '''SELECT filename, label FROM text WHERE label != ""
                        ORDER BY filename'''
        texts = self._manager._conn.execute(text_query).fetchall()
        self.assertEqual(len(texts), 2)
        self.assertEqual(texts[0]['filename'], '1.txt')
        self.assertEqual(texts[0]['label'], 'A')
        self.assertEqual(texts[1]['filename'], '2.txt')
        self.assertEqual(texts[1]['label'], 'B')


if __name__ == '__main__':
    unittest.main()
