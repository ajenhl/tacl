import os.path
import unittest

import tacl


class CorpusIntegrationTestCase (unittest.TestCase):

    def setUp (self):
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data',
                                      'stripped')
        self._tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                         tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_get_text (self):
        corpus = tacl.Corpus(self._data_dir, self._tokenizer)
        actual_text = corpus.get_text('1.txt')
        expected_text = tacl.Text('1.txt', 'then we went\n', self._tokenizer)
        self.assertEqual(actual_text.get_checksum(),
                         expected_text.get_checksum())
        self.assertEqual(actual_text.get_filename(),
                         expected_text.get_filename())

    def test_get_texts (self):
        corpus = tacl.Corpus(self._data_dir, self._tokenizer)
        expected_texts = [tacl.Text('1.txt', 'then we went\n', self._tokenizer),
                          tacl.Text('2.txt', 'these he sent\n',
                                    self._tokenizer),
                          tacl.Text('3.txt', 'that\n', self._tokenizer),
                          tacl.Text('4.txt', 'hense\n', self._tokenizer),
                          tacl.Text('5.txt', 'well\n', self._tokenizer)]
        actual_texts = list(corpus.get_texts())
        actual_texts.sort(key=lambda x: x.get_filename())
        for actual_text, expected_text in zip(actual_texts, expected_texts):
            self.assertEqual(actual_text.get_checksum(),
                             expected_text.get_checksum())
            self.assertEqual(actual_text.get_filename(),
                             expected_text.get_filename())


if __name__ == '__main__':
    unittest.main()
