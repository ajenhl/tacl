import os.path
import unittest

import tacl


class CorpusIntegrationTestCase (unittest.TestCase):

    def setUp (self):
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data',
                                      'stripped')

    def test_get_text (self):
        corpus = tacl.Corpus(self._data_dir)
        actual_text = corpus.get_text('1.txt')
        expected_text = tacl.Text('1.txt', 'then we went\n')
        self.assertEqual(actual_text.get_checksum(),
                         expected_text.get_checksum())
        self.assertEqual(actual_text.get_filename(),
                         expected_text.get_filename())

    def test_get_texts (self):
        corpus = tacl.Corpus(self._data_dir)
        expected_texts = [tacl.Text('1.txt', 'then we went\n'),
                          tacl.Text('2.txt', 'these he sent\n'),
                          tacl.Text('3.txt', 'that\n'),
                          tacl.Text('4.txt', 'hense\n'),
                          tacl.Text('5.txt', 'well\n')]
        actual_texts = list(corpus.get_texts())
        actual_texts.sort(key=lambda x: x.get_filename())
        for actual_text, expected_text in zip(actual_texts, expected_texts):
            self.assertEqual(actual_text.get_checksum(),
                             expected_text.get_checksum())
            self.assertEqual(actual_text.get_filename(),
                             expected_text.get_filename())


if __name__ == '__main__':
    unittest.main()
