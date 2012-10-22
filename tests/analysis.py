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
        self._manager = manager

    def test_diff (self):
        actual_rows = self._manager.diff(['A', 'B', 'C'], 2, 2, 1)
        expected_rows = [(u'n ', 1, u'A'), (u' w', 2, u'A'), (u'we', 3, u'A'),
                         (u'el', 1, u'A'), (u'll', 1, u'A'), (u'es', 1, u'B'),
                         (u'se', 2, u'B'), (u' h', 1, u'B'), (u' s', 1, u'B'),
                         (u'ha', 1, u'C'), (u'at', 1, u'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff(['A', 'B', 'C'], 2, 2, 2)
        expected_rows = [(u' w', 2, u'A'), (u'we', 3, u'A'), (u'se', 2, u'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_text (self):
        actual_rows = self._manager.diff_text(['A', 'B', 'C'], 2, 2, 1)
        expected_rows = [(u'n ', 1, u'1.txt', u'A'), (u' w', 2, u'1.txt', u'A'),
                         (u'we', 2, u'1.txt', u'A'), (u'we', 1, u'5.txt', u'A'),
                         (u'el', 1, u'5.txt', u'A'), (u'll', 1, u'5.txt', u'A'),
                         (u'es', 1, u'2.txt', u'B'), (u'se', 2, u'2.txt', u'B'),
                         (u' h', 1, u'2.txt', u'B'), (u' s', 1, u'2.txt', u'B'),
                         (u'ha', 1, u'3.txt', u'C'), (u'at', 1, u'3.txt', u'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff_text(['A', 'B', 'C'], 2, 2, 2)
        expected_rows = [(u' w', 2, u'1.txt', u'A'), (u'we', 2, u'1.txt', u'A'),
                         (u'we', 1, u'5.txt', u'A'), (u'se', 2, u'2.txt', u'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.diff_text(['A', 'B', 'C'], 2, 2, 3)
        expected_rows = [(u'we', 2, u'1.txt', u'A'), (u'we', 1, u'5.txt', u'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection (self):
        # Intersection will give incorrect results if there are
        # labelled texts that are not referenced in the labels passed
        # to the method. This is not an issue in normal usage, since
        # all texts are updated with the labels from the catalogue
        # file, which are then passed to the method.
        self._update_text('3.txt', '1', '')
        actual_rows = self._manager.intersection(['A', 'B'], 2, 2, 1)
        expected_rows = [(u'th', 2, u'ALL'), (u'he', 3, u'ALL'),
                         (u'en', 3, u'ALL'), (u'e ', 3, u'ALL'),
                         (u'nt', 2, u'ALL')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.intersection(['A', 'B'], 2, 2, 3)
        expected_rows = [(u'he', 3, u'ALL'), (u'en', 3, u'ALL'),
                         (u'e ', 3, u'ALL')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        self._update_text('3.txt', '1', 'C')
        actual_rows = self._manager.intersection(['A', 'B', 'C'], 2, 2, 1)
        expected_rows = [(u'th', 3, u'ALL')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_text (self):
        # Intersection will give incorrect results if there are
        # labelled texts that are not referenced in the labels passed
        # to the method. This is not an issue in normal usage, since
        # all texts are updated with the labels from the catalogue
        # file, which are then passed to the method.
        self._update_text('3.txt', '1', '')
        actual_rows = self._manager.intersection_text(['A', 'B'], 2, 2, 1)
        expected_rows = [(u'th', 1, u'1.txt', u'A'), (u'th', 1, u'2.txt', u'B'),
                         (u'he', 1, u'1.txt', u'A'), (u'he', 2, u'2.txt', u'B'),
                         (u'en', 2, u'1.txt', u'A'), (u'en', 1, u'2.txt', u'B'),
                         (u'e ', 1, u'1.txt', u'A'), (u'e ', 2, u'2.txt', u'B'),
                         (u'nt', 1, u'1.txt', u'A'), (u'nt', 1, u'2.txt', u'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.intersection_text(['A', 'B'], 2, 2, 3)
        expected_rows = [(u'he', 1, u'1.txt', u'A'), (u'he', 2, u'2.txt', u'B'),
                         (u'en', 2, u'1.txt', u'A'), (u'en', 1, u'2.txt', u'B'),
                         (u'e ', 1, u'1.txt', u'A'), (u'e ', 2, u'2.txt', u'B')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        self._update_text('3.txt', '1', 'C')
        actual_rows = self._manager.intersection_text(['A', 'B', 'C'], 2, 2, 1)
        expected_rows = [(u'th', 1, u'1.txt', u'A'), (u'th', 1, u'2.txt', u'B'),
                         (u'th', 1, u'3.txt', u'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._manager.intersection_text(['A', 'B', 'C'], 2, 2, 3)
        expected_rows = [(u'th', 1, u'1.txt', u'A'), (u'th', 1, u'2.txt', u'B'),
                         (u'th', 1, u'3.txt', u'C')]
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
