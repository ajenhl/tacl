import io
import os.path
import unittest

import tacl
from tacl.exceptions import MalformedQueryError
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
            'SELECT Text.name, Text.siglum, Text.checksum, Text.label, '
            'TextNGram.ngram, TextNGram.size, TextNGram.count '
            'FROM Text, TextNGram WHERE Text.id = TextNGram.text').fetchall()
        expected_rows = [
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 't', 1, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'h', 1, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'e', 1, 3),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'n', 1, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'w', 1, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'th', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'he', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'en', 2, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'nw', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'we', 2, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'ew', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'nt', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'the', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'hen', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'enw', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'nwe', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'wew', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'ewe', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'wen', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'ent', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 't', 1, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'h', 1, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'e', 1, 3),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'w', 1, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'n', 1, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'th', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'he', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'ew', 2, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'we', 2, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'en', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'nt', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'the', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'hew', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'ewe', 3, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'wew', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'wen', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'ent', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 't', 1, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'h', 1, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'e', 1, 4),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 's', 1, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'n', 1, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'th', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'he', 2, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'es', 2, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'se', 2, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'eh', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'en', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'nt', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'the', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'hes', 3, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ese', 3, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'seh', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ehe', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'sen', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ent', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 't', 1, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'h', 1, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'e', 1, 3),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'w', 1, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 's', 1, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'n', 1, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'th', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'he', 2, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ew', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ws', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'sh', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'es', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'se', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'en', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'nt', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'the', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'hew', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ews', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'wsh', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'she', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'hes', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ese', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'sen', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ent', 3, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 't', 1, 2),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'h', 1, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'a', 1, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'th', 2, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'ha', 2, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'at', 2, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'tha', 3, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'hat', 3, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'h', 1, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'e', 1, 2),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'n', 1, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 's', 1, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'he', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'en', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'ns', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'se', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'hen', 3, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'ens', 3, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'nse', 3, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'w', 1, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'e', 1, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'l', 1, 2),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'we', 2, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'el', 2, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'll', 2, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'wel', 3, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'ell', 3, 1)]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = self._store._conn.execute(
            'SELECT Text.name, Text.siglum, TextHasNGram.size '
            'FROM Text, TextHasNGram '
            'WHERE Text.id = TextHasNGram.text').fetchall()
        expected_rows = [
            ('T1', 'base', 1), ('T1', 'base', 2), ('T1', 'base', 3),
            ('T1', 'a', 1), ('T1', 'a', 2), ('T1', 'a', 3),
            ('T2', 'base', 1), ('T2', 'base', 2), ('T2', 'base', 3),
            ('T2', 'a', 1), ('T2', 'a', 2), ('T2', 'a', 3),
            ('T3', 'base', 1), ('T3', 'base', 2), ('T3', 'base', 3),
            ('T4', 'base', 1), ('T4', 'base', 2), ('T4', 'base', 3),
            ('T5', 'base', 1), ('T5', 'base', 2), ('T5', 'base', 3),
            ]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_counts (self):
        actual_rows = self._get_rows_from_csv(self._store.counts(
                self._catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('T1', 'base', '1', '5', '10', '10', 'A'),
            ('T1', 'base', '2', '7', '9', '10', 'A'),
            ('T1', 'base', '3', '8', '8', '10', 'A'),
            ('T1', 'a', '1', '5', '9', '9', 'A'),
            ('T1', 'a', '2', '6', '8', '9', 'A'),
            ('T1', 'a', '3', '6', '7', '9', 'A'),
            ('T2', 'base', '1', '5', '11', '11', 'B'),
            ('T2', 'base', '2', '7', '10', '11', 'B'),
            ('T2', 'base', '3', '7', '9', '11', 'B'),
            ('T2', 'a', '1', '6', '11', '11', 'B'),
            ('T2', 'a', '2', '9', '10', '11', 'B'),
            ('T2', 'a', '3', '9', '9', '11', 'B'),
            ('T3', 'base', '1', '3', '4', '4', 'C'),
            ('T3', 'base', '2', '3', '3', '4', 'C'),
            ('T3', 'base', '3', '2', '2', '4', 'C'),
            ('T5', 'base', '1', '3', '4', '4', 'A'),
            ('T5', 'base', '2', '3', '3', '4', 'A'),
            ('T5', 'base', '3', '2', '2', '4', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff (self):
        actual_rows = self._get_rows_from_csv(self._store.diff(
                self._catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('s', '1', 'T2', 'base', '2', 'B'),
            ('s', '1', 'T2', 'a', '2', 'B'),
            ('a', '1', 'T3', 'base', '1', 'C'),
            ('l', '1', 'T5', 'base', '2', 'A'),
            ('nw', '2', 'T1', 'base', '1', 'A'),
            ('we', '2', 'T1', 'base', '2', 'A'),
            ('we', '2', 'T1', 'a', '2', 'A'),
            ('we', '2', 'T5', 'base', '1', 'A'),
            ('es', '2', 'T2', 'base', '2', 'B'),
            ('es', '2', 'T2', 'a', '1', 'B'),
            ('se', '2', 'T2', 'base', '2', 'B'),
            ('se', '2', 'T2', 'a', '1', 'B'),
            ('ws', '2', 'T2', 'a', '1', 'B'),
            ('sh', '2', 'T2', 'a', '1', 'B'),
            ('eh', '2', 'T2', 'base', '1', 'B'),
            ('ha', '2', 'T3', 'base', '1', 'C'),
            ('at', '2', 'T3', 'base', '1', 'C'),
            ('el', '2', 'T5', 'base', '1', 'A'),
            ('ll', '2', 'T5', 'base', '1', 'A'),
            ('hen', '3', 'T1', 'base', '1', 'A'),
            ('enw', '3', 'T1', 'base', '1', 'A'),
            ('nwe', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'a', '1', 'A'),
            ('ewe', '3', 'T1', 'base', '1', 'A'),
            ('ewe', '3', 'T1', 'a', '2', 'A'),
            ('wen', '3', 'T1', 'base', '1', 'A'),
            ('wen', '3', 'T1', 'a', '1', 'A'),
            ('hes', '3', 'T2', 'base', '2', 'B'),
            ('hes', '3', 'T2', 'a', '1', 'B'),
            ('ese', '3', 'T2', 'base', '2', 'B'),
            ('ese', '3', 'T2', 'a', '1', 'B'),
            ('ews', '3', 'T2', 'a', '1', 'B'),
            ('seh', '3', 'T2', 'base', '1', 'B'),
            ('wsh', '3', 'T2', 'a', '1', 'B'),
            ('ehe', '3', 'T2', 'base', '1', 'B'),
            ('she', '3', 'T2', 'a', '1', 'B'),
            ('sen', '3', 'T2', 'base', '1', 'B'),
            ('sen', '3', 'T2', 'a', '1', 'B'),
            ('tha', '3', 'T3', 'base', '1', 'C'),
            ('hat', '3', 'T3', 'base', '1', 'C'),
            ('wel', '3', 'T5', 'base', '1', 'A'),
            ('ell', '3', 'T5', 'base', '1', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_asymmetric (self):
        actual_rows = self._get_rows_from_csv(self._store.diff_asymmetric(
                self._catalogue, 'A', io.StringIO(newline='')))
        expected_rows = [
            ('l', '1', 'T5', 'base', '2', 'A'),
            ('nw', '2', 'T1', 'base', '1', 'A'),
            ('we', '2', 'T1', 'base', '2', 'A'),
            ('we', '2', 'T1', 'a', '2', 'A'),
            ('we', '2', 'T5', 'base', '1', 'A'),
            ('el', '2', 'T5', 'base', '1', 'A'),
            ('ll', '2', 'T5', 'base', '1', 'A'),
            ('hen', '3', 'T1', 'base', '1', 'A'),
            ('enw', '3', 'T1', 'base', '1', 'A'),
            ('nwe', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'a', '1', 'A'),
            ('ewe', '3', 'T1', 'base', '1', 'A'),
            ('ewe', '3', 'T1', 'a', '2', 'A'),
            ('wen', '3', 'T1', 'base', '1', 'A'),
            ('wen', '3', 'T1', 'a', '1', 'A'),
            ('wel', '3', 'T5', 'base', '1', 'A'),
            ('ell', '3', 'T5', 'base', '1', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_supplied (self):
        supplied_dir = os.path.join(self._data_dir, 'supplied_input')
        results = [os.path.join(supplied_dir, 'diff_input_1.csv'),
                   os.path.join(supplied_dir, 'diff_input_2.csv'),
                   os.path.join(supplied_dir, 'diff_input_3.csv')]
        labels = ('A', 'B', 'C')
        actual_rows = self._get_rows_from_csv(
            self._store.diff_supplied(results, labels, io.StringIO(newline='')))
        expected_rows = [
            ('過失', '2', 'T0005', 'base', '5', 'A'),
            ('過失', '2', 'T0003', '大', '2', 'A'),
            ('皆不', '2', 'T0004', 'base', '1', 'A'),
            ('皆不', '2', 'T0002', '大', '1', 'A'),
            ('皆不', '2', 'T0003', '大', '1', 'A'),
            ('棄捨', '2', 'T0004', '元', '4', 'A'),
            ('棄捨', '2', 'T0003', 'base', '2', 'A'),
            ('七佛', '2', 'T0006', 'base', '3', 'B'),
            ('七佛', '2', 'T0004', '元', '3', 'B'),
            ('七佛', '2', 'T0002', '大', '2', 'B'),
            ('人子', '2', 'T0004', '元', '1', 'C'),
            ('人子', '2', 'T0007', 'base', '1', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_supplied_argument_mismatch (self):
        # Supplying a list of labels that differs in length from the
        # list of results should raise an exception.
        supplied_dir = os.path.join(self._data_dir, 'supplied_input')
        results = [os.path.join(supplied_dir, 'diff_input_1.csv'),
                   os.path.join(supplied_dir, 'diff_input_2.csv'),
                   os.path.join(supplied_dir, 'diff_input_3.csv')]
        labels = ('A', 'B')
        self.assertRaises(MalformedQueryError, self._store.diff_supplied,
                          results, labels, io.StringIO(newline=''))

    def test_intersection (self):
        actual_rows = self._get_rows_from_csv(self._store.intersection(
                self._catalogue, io.StringIO(newline='')))
        expected_rows = [
            ('t', '1', 'T1', 'base', '2', 'A'),
            ('t', '1', 'T1', 'a', '2', 'A'),
            ('t', '1', 'T2', 'base', '2', 'B'),
            ('t', '1', 'T2', 'a', '2', 'B'),
            ('t', '1', 'T3', 'base', '2', 'C'),
            ('h', '1', 'T1', 'base', '1', 'A'),
            ('h', '1', 'T1', 'a', '1', 'A'),
            ('h', '1', 'T2', 'base', '2', 'B'),
            ('h', '1', 'T2', 'a', '2', 'B'),
            ('h', '1', 'T3', 'base', '1', 'C'),
            ('th', '2', 'T1', 'base', '1', 'A'),
            ('th', '2', 'T1', 'a', '1', 'A'),
            ('th', '2', 'T2', 'base', '1', 'B'),
            ('th', '2', 'T2', 'a', '1', 'B'),
            ('th', '2', 'T3', 'base', '1', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_supplied (self):
        supplied_dir = os.path.join(self._data_dir, 'supplied_input')
        results = [os.path.join(supplied_dir, 'intersect_input_1.csv'),
                   os.path.join(supplied_dir, 'intersect_input_2.csv'),
                   os.path.join(supplied_dir, 'intersect_input_3.csv')]
        labels = ('A', 'B', 'C')
        actual_rows = self._get_rows_from_csv(
            self._store.intersection_supplied(results, labels,
                                              io.StringIO(newline='')))
        expected_rows = [
            ('龍皆起前', '4', 'T0033', '元', '1', 'A'),
            ('龍皆起前', '4', 'T0034', '明', '2', 'A'),
            ('龍皆起前', '4', 'T0002', 'base', '3', 'B'),
            ('龍皆起前', '4', 'T0052', 'base', '2', 'C'),
            ('[月*劦]生', '2', 'T0002', '明', '10', 'A'),
            ('[月*劦]生', '2', 'T0002', 'base', '10', 'A'),
            ('[月*劦]生', '2', 'T0023', '大', '2', 'B'),
            ('[月*劦]生', '2', 'T0053', '大', '2', 'C'),
        ]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_supplied_argument_mismatch (self):
        # Supplying a list of labels that differs in length from the
        # list of results should raise an exception.
        supplied_dir = os.path.join(self._data_dir, 'supplied_input')
        results = [os.path.join(supplied_dir, 'intersect_input_1.csv'),
                   os.path.join(supplied_dir, 'intersect_input_2.csv'),
                   os.path.join(supplied_dir, 'intersect_input_3.csv')]
        labels = ('A', 'B')
        self.assertRaises(
            MalformedQueryError, self._store.intersection_supplied,
            results, labels, io.StringIO(newline=''))

    def test_validate_missing_text (self):
        self._catalogue['missing'] = 'A'
        with self.assertRaises(FileNotFoundError):
            self._store.validate(self._corpus, self._catalogue)


if __name__ == '__main__':
    unittest.main()
