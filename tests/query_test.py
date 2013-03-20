#!/usr/bin/env python3

import unittest

import tacl


class QueryTestCase (unittest.TestCase):

    """Test case for testing database queries."""

    def setUp (self):
        manager = tacl.DBManager(':memory:')
        # 1.txt: "then we went"
        # 2.txt: "these he sent"
        # 3.txt: "that"
        # 4.txt: "hense"
        # 5.txt: "well"
        id1 = manager.add_text('1.txt', '1')
        id2 = manager.add_text('2.txt', '1')
        id3 = manager.add_text('3.txt', '1')
        id4 = manager.add_text('4.txt', '1')
        id5 = manager.add_text('5.txt', '1')
        manager.add_ngram(id1, 'th', 2, 1)
        manager.add_ngram(id1, 'he', 2, 1)
        manager.add_ngram(id1, 'en', 2, 2)
        manager.add_ngram(id1, 'n ', 2, 1)
        manager.add_ngram(id1, ' w', 2, 2)
        manager.add_ngram(id1, 'we', 2, 2)
        manager.add_ngram(id1, 'e ', 2, 1)
        manager.add_ngram(id1, 'nt', 2, 1)
        manager.add_ngram(id2, 'th', 2, 1)
        manager.add_ngram(id2, 'he', 2, 2)
        manager.add_ngram(id2, 'es', 2, 1)
        manager.add_ngram(id2, 'se', 2, 2)
        manager.add_ngram(id2, 'e ', 2, 2)
        manager.add_ngram(id2, ' h', 2, 1)
        manager.add_ngram(id2, ' s', 2, 1)
        manager.add_ngram(id2, 'en', 2, 1)
        manager.add_ngram(id2, 'nt', 2, 1)
        manager.add_ngram(id3, 'th', 2, 1)
        manager.add_ngram(id3, 'ha', 2, 1)
        manager.add_ngram(id3, 'at', 2, 1)
        manager.add_ngram(id4, 'he', 2, 1)
        manager.add_ngram(id4, 'en', 2, 1)
        manager.add_ngram(id4, 'ns', 2, 1)
        manager.add_ngram(id4, 'se', 2, 1)
        manager.add_ngram(id5, 'we', 2, 1)
        manager.add_ngram(id5, 'el', 2, 1)
        manager.add_ngram(id5, 'll', 2, 1)
        manager.add_ngrams()
        manager.add_label('1.txt', 'A', '1')
        manager.add_label('2.txt', 'B', '1')
        manager.add_label('3.txt', 'C', '1')
        manager.add_label('4.txt', 'D', '1')
        manager.add_label('5.txt', 'A', '1')
        # Do not use sqlite3.Row in results, because it makes the
        # comparison of result rows harder.
        manager._conn.row_factory = None
        manager._c = manager._conn.cursor()
        manager.add_indices()
        manager.analyse()
        self._manager = manager

    def test_counts (self):
        actual_rows = self._manager.counts(['A', 'B', 'C'])
        expected_rows = [('1.txt', 2, 8, 11, 'A'), ('2.txt', 2, 9, 12, 'B'),
                         ('3.txt', 2, 3, 3, 'C'), ('5.txt', 2, 3, 3, 'A')]
        self.assertEqual(list(actual_rows), expected_rows)
        actual_rows = self._manager.counts(['A'])
        expected_rows = [('1.txt', 2, 8, 11, 'A'), ('5.txt', 2, 3, 3, 'A')]
        self.assertEqual(list(actual_rows), expected_rows)

    def test_diff (self):
        actual_rows = self._manager.diff(['A', 'B', 'C'])
        expected_rows = [('n ', 2, 1, '1.txt', 'A'), (' w', 2, 2, '1.txt', 'A'),
                         ('we', 2, 2, '1.txt', 'A'), ('we', 2, 1, '5.txt', 'A'),
                         ('el', 2, 1, '5.txt', 'A'), ('ll', 2, 1, '5.txt', 'A'),
                         ('es', 2, 1, '2.txt', 'B'), ('se', 2, 2, '2.txt', 'B'),
                         (' h', 2, 1, '2.txt', 'B'), (' s', 2, 1, '2.txt', 'B'),
                         ('ha', 2, 1, '3.txt', 'C'), ('at', 2, 1, '3.txt', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_supplied (self):
        # Test (A AND B) XOR C.
        supplied_labels = ['A', 'B']
        input_rows = self._manager.intersection(supplied_labels)
        ngrams = [row[0] for row in input_rows]
        actual_rows = self._manager.diff_supplied(
            ['C'], ngrams, supplied_labels)
        expected_rows = [('he', 2, 1, '1.txt', 'A'), ('he', 2, 2, '2.txt', 'B'),
                         ('en', 2, 2, '1.txt', 'A'), ('en', 2, 1, '2.txt', 'B'),
                         ('e ', 2, 1, '1.txt', 'A'), ('e ', 2, 2, '2.txt', 'B'),
                         ('nt', 2, 1, '1.txt', 'A'), ('nt', 2, 1, '2.txt', 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection (self):
        actual_rows = self._manager.intersection(['A', 'B'])
        expected_rows = [('th', 2, 1, '1.txt', 'A'), ('th', 2, 1, '2.txt', 'B'),
                         ('he', 2, 1, '1.txt', 'A'), ('he', 2, 2, '2.txt', 'B'),
                         ('en', 2, 2, '1.txt', 'A'), ('en', 2, 1, '2.txt', 'B'),
                         ('e ', 2, 1, '1.txt', 'A'), ('e ', 2, 2, '2.txt', 'B'),
                         ('nt', 2, 1, '1.txt', 'A'), ('nt', 2, 1, '2.txt', 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.intersection(['A', 'B', 'C'])
        expected_rows = [('th', 2, 1, '1.txt', 'A'), ('th', 2, 1, '2.txt', 'B'),
                         ('th', 2, 1, '3.txt', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_supplied (self):
        # Test (A XOR B) AND D.
        supplied_labels = ['A', 'B']
        input_rows = self._manager.diff(supplied_labels)
        ngrams = [row[0] for row in input_rows]
        actual_rows = self._manager.intersection_supplied(
            ['D'], ngrams, supplied_labels)
        expected_rows = [('se', 2, 2, '2.txt', 'B'), ('se', 2, 1, '4.txt', 'D')]
        self.assertEqual(set(actual_rows), set(expected_rows))


if __name__ == '__main__':
    unittest.main()
