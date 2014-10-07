import io
import os.path
import unittest

import tacl
from ..tacl_test_case import TaclTestCase

class DataStoreIntegrationTestCase (TaclTestCase):

    def setUp (self):
        self._tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                         tacl.constants.TOKENIZER_JOINER_CBETA)
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self._corpus = tacl.Corpus(os.path.join(self._data_dir, 'stripped'),
                                   self._tokenizer)
        self._catalogue = tacl.Catalogue()
        self._catalogue.load(os.path.join(self._data_dir, 'catalogue.txt'))
        self._store = tacl.DataStore(':memory:')
        self._store.add_ngrams(self._corpus, 1, 3)

    def test_add_ngrams (self):
        self._store._conn.row_factory = None
        actual_rows = self._store._conn.execute(
            'SELECT Text.filename, Text.checksum, Text.label, '
            'TextNGram.ngram, TextNGram.size, TextNGram.count '
            'FROM Text, TextNGram WHERE Text.id = TextNGram.text').fetchall()
        expected_rows = [
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 't', 1, 2),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'h', 1, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'e', 1, 3),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'n', 1, 2),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'w', 1, 2),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'th', 2, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'he', 2, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'en', 2, 2),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'nw', 2, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'we', 2, 2),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'ew', 2, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'nt', 2, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'the', 3, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'hen', 3, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'enw', 3, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'nwe', 3, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'wew', 3, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'ewe', 3, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'wen', 3, 1),
            ('1.txt', '705c89d665a5300516fe7314f84ebce0', '', 'ent', 3, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 't', 1, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'h', 1, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'e', 1, 4),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 's', 1, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'n', 1, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'th', 2, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'he', 2, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'es', 2, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'se', 2, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'eh', 2, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'en', 2, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'nt', 2, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'the', 3, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'hes', 3, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ese', 3, 2),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'seh', 3, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ehe', 3, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'sen', 3, 1),
            ('2.txt', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ent', 3, 1),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 't', 1, 2),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 'h', 1, 1),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 'a', 1, 1),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 'th', 2, 1),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 'ha', 2, 1),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 'at', 2, 1),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 'tha', 3, 1),
            ('3.txt', 'bb34469a937a77ae77c2aeb67248c43c', '', 'hat', 3, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'h', 1, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'e', 1, 2),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'n', 1, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 's', 1, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'he', 2, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'en', 2, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'ns', 2, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'se', 2, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'hen', 3, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'ens', 3, 1),
            ('4.txt', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'nse', 3, 1),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'w', 1, 1),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'e', 1, 1),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'l', 1, 2),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'we', 2, 1),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'el', 2, 1),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'll', 2, 1),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'wel', 3, 1),
            ('5.txt', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'ell', 3, 1)]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._store._conn.execute(
            'SELECT Text.filename, TextHasNGram.size FROM Text, TextHasNGram '
            'WHERE Text.id = TextHasNGram.text').fetchall()
        expected_rows = [
            ('1.txt', 1), ('1.txt', 2), ('1.txt', 3),
            ('2.txt', 1), ('2.txt', 2), ('2.txt', 3),
            ('3.txt', 1), ('3.txt', 2), ('3.txt', 3),
            ('4.txt', 1), ('4.txt', 2), ('4.txt', 3),
            ('5.txt', 1), ('5.txt', 2), ('5.txt', 3),
            ]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_counts (self):
        actual_rows = self._get_rows_from_csv(self._store.counts(
                self._catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('1.txt', '1', '5', '10', '10', 'A'),
            ('1.txt', '2', '7', '9', '10', 'A'),
            ('1.txt', '3', '8', '8', '10', 'A'),
            ('2.txt', '1', '5', '11', '11', 'B'),
            ('2.txt', '2', '7', '10', '11', 'B'),
            ('2.txt', '3', '7', '9', '11', 'B'),
            ('3.txt', '1', '3', '4', '4', 'C'),
            ('3.txt', '2', '3', '3', '4', 'C'),
            ('3.txt', '3', '2', '2', '4', 'C'),
            ('5.txt', '1', '3', '4', '4', 'A'),
            ('5.txt', '2', '3', '3', '4', 'A'),
            ('5.txt', '3', '2', '2', '4', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff (self):
        actual_rows = self._get_rows_from_csv(self._store.diff(
                self._catalogue, io.StringIO(newline='')))
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
        actual_rows = self._get_rows_from_csv(self._store.diff_asymmetric(
                self._catalogue, 'A', io.StringIO(newline='')))
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
        actual_rows = self._get_rows_from_csv(self._store.diff_supplied(
                self._catalogue, input_csv, io.StringIO(newline='')))
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
        actual_rows = self._get_rows_from_csv(self._store.intersection(
                self._catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('t', '1', '1.txt', '2', 'A'), ('t', '1', '2.txt', '2', 'B'),
            ('t', '1', '3.txt', '2', 'C'), ('h', '1', '1.txt', '1', 'A'),
            ('h', '1', '2.txt', '2', 'B'), ('h', '1', '3.txt', '1', 'C'),
            ('th', '2', '1.txt', '1', 'A'), ('th', '2', '2.txt', '1', 'B'),
            ('th', '2', '3.txt', '1', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_supplied (self):
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
        actual_rows = self._get_rows_from_csv(self._store.intersection_supplied(
                self._catalogue, input_csv, io.StringIO(newline='')))
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


if __name__ == '__main__':
    unittest.main()
