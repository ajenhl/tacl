#!/usr/bin/env python3

import sqlite3
import unittest

import tacl


class TestAnalysis (unittest.TestCase):

    """Test case for testing the database analysis functions."""

    def setUp (self):
        manager = tacl.DBManager(':memory:')
        # 1.txt: "then we went"
        # 2.txt: "these he sent"
        # 3.txt: "that"
        # 4.txt: "hense"
        # 5.txt: "well"
        id1 = manager.add_text('1.txt', '1', 'A')
        id2 = manager.add_text('2.txt', '1', 'B')
        id3 = manager.add_text('3.txt', '1', 'C')
        id4 = manager.add_text('4.txt', '1', '')
        id5 = manager.add_text('5.txt', '1', 'A')
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
        manager.add_ngram
        manager.commit()
        # Do not use sqlite3.Row in results, because it makes the
        # comparison of result rows harder.
        manager._conn.row_factory = None
        manager._c = manager._conn.cursor()
        manager.add_indices()
        manager.analyse()
        self._manager = manager

    def test_diff (self):
        actual_rows = self._manager.diff(['A', 'B', 'C'], 2, 2, 1)
        expected_rows = [('n ', 1, 'A'), (' w', 2, 'A'), ('we', 3, 'A'),
                         ('el', 1, 'A'), ('ll', 1, 'A'), ('es', 1, 'B'),
                         ('se', 2, 'B'), (' h', 1, 'B'), (' s', 1, 'B'),
                         ('ha', 1, 'C'), ('at', 1, 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff(['A', 'B', 'C'], 2, 2, 2)
        expected_rows = [(' w', 2, 'A'), ('we', 3, 'A'), ('se', 2, 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_text (self):
        actual_rows = self._manager.diff_text(['A', 'B', 'C'], 2, 2)
        expected_rows = [('n ', 1, '1.txt', 'A'), (' w', 2, '1.txt', 'A'),
                         ('we', 2, '1.txt', 'A'), ('we', 1, '5.txt', 'A'),
                         ('el', 1, '5.txt', 'A'), ('ll', 1, '5.txt', 'A'),
                         ('es', 1, '2.txt', 'B'), ('se', 2, '2.txt', 'B'),
                         (' h', 1, '2.txt', 'B'), (' s', 1, '2.txt', 'B'),
                         ('ha', 1, '3.txt', 'C'), ('at', 1, '3.txt', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_asymmetric (self):
        actual_rows = self._manager.diff_asymmetric('A', 2, 2, 1)
        expected_rows = [('n ', 1, 'A'), (' w', 2, 'A'), ('we', 3, 'A'),
                         ('el', 1, 'A'), ('ll', 1, 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff_asymmetric('B', 2, 2, 1)
        expected_rows = [('es', 1, 'B'), ('se', 2, 'B'), (' h', 1, 'B'),
                         (' s', 1, 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff_asymmetric('C', 2, 2, 1)
        expected_rows = [('ha', 1, 'C'), ('at', 1, 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff_asymmetric('A', 2, 2, 2)
        expected_rows = [(' w', 2, 'A'), ('we', 3, 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_asymmetric_text (self):
        actual_rows = self._manager.diff_asymmetric_text('A', 2, 2)
        expected_rows = [('n ', 1, '1.txt', 'A'), (' w', 2, '1.txt', 'A'),
                         ('we', 2, '1.txt', 'A'), ('we', 1, '5.txt', 'A'),
                         ('el', 1, '5.txt', 'A'), ('ll', 1, '5.txt', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff_asymmetric_text('B', 2, 2)
        expected_rows = [('es', 1, '2.txt', 'B'), ('se', 2, '2.txt', 'B'),
                         (' h', 1, '2.txt', 'B'), (' s', 1, '2.txt', 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff_asymmetric_text('C', 2, 2)
        expected_rows = [('ha', 1, '3.txt', 'C'), ('at', 1, '3.txt', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection (self):
        # Intersection will give incorrect results if there are
        # labelled texts that are not referenced in the labels passed
        # to the method. This is not an issue in normal usage, since
        # all texts are updated with the labels from the catalogue
        # file, which are then passed to the method.
        self._update_text('3.txt', '1', '')
        actual_rows = self._manager.intersection(['A', 'B'], 2, 2, 4)
        expected_rows = [('th', 2, 'ALL'), ('he', 3, 'ALL'), ('en', 3, 'ALL'),
                         ('e ', 3, 'ALL'), ('nt', 2, 'ALL')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.intersection(['A', 'B'], 2, 2, 2)
        expected_rows = [('th', 2, 'ALL'), ('nt', 2, 'ALL')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        self._update_text('3.txt', '1', 'C')
        actual_rows = self._manager.intersection(['A', 'B', 'C'], 2, 2, 3)
        expected_rows = [('th', 3, 'ALL')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_text (self):
        # Intersection will give incorrect results if there are
        # labelled texts that are not referenced in the labels passed
        # to the method. This is not an issue in normal usage, since
        # all texts are updated with the labels from the catalogue
        # file, which are then passed to the method.
        self._update_text('3.txt', '1', '')
        actual_rows = self._manager.intersection_text(['A', 'B'], 2, 2)
        expected_rows = [('th', 1, '1.txt', 'A'), ('th', 1, '2.txt', 'B'),
                         ('he', 1, '1.txt', 'A'), ('he', 2, '2.txt', 'B'),
                         ('en', 2, '1.txt', 'A'), ('en', 1, '2.txt', 'B'),
                         ('e ', 1, '1.txt', 'A'), ('e ', 2, '2.txt', 'B'),
                         ('nt', 1, '1.txt', 'A'), ('nt', 1, '2.txt', 'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        self._update_text('3.txt', '1', 'C')
        actual_rows = self._manager.intersection_text(['A', 'B', 'C'], 2, 2)
        expected_rows = [('th', 1, '1.txt', 'A'), ('th', 1, '2.txt', 'B'),
                         ('th', 1, '3.txt', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def _update_text (self, filename, timestamp, label):
        # Because DBManager makes use of sqlite3.Row features
        # internally, in order to update texts, it must be switched to
        # (and then away from).
        self._manager._conn.row_factory = sqlite3.Row
        self._manager._c = self._manager._conn.cursor()
        self._manager.add_text(filename, timestamp, label)
        self._manager.commit()
        self._manager._conn.row_factory = None
        self._manager._c = self._manager._conn.cursor()


if __name__ == '__main__':
    unittest.main()
