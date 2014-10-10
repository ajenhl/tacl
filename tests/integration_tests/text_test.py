import collections
import unittest

import tacl


class TextIntegrationTestCase (unittest.TestCase):

    def setUp (self):
        self._tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                         tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_get_checksum (self):
        content = '阿闍世[(禾*尤)\n/上/日]首佛足。敬強阿闍世耶。又'
        text = tacl.Text('test', 'base', content, self._tokenizer)
        actual_checksum = text.get_checksum()
        expected_checksum = 'b8f33a481780c4128c1b852488cede88'
        self.assertEqual(actual_checksum, expected_checksum)

    def test_get_filename (self):
        content = '阿闍世[(禾*尤)\n/上/日]首佛足。敬強阿闍世耶。又'
        filename = 'test/base.txt'
        text = tacl.Text('test', 'base', content, self._tokenizer)
        actual_filename = text.get_filename()
        expected_filename = filename
        self.assertEqual(actual_filename, expected_filename)

    def test_get_ngrams (self):
        content = '阿闍世[(禾*尤)\n/上/日]首佛足。敬強阿闍世耶。又'
        text = tacl.Text('test', 'base', content, self._tokenizer)
        expected_ngrams = [
            (3, {'阿闍世': 2, '闍世[(禾*尤)/上/日]': 1,
                 '世[(禾*尤)/上/日]首': 1, '[(禾*尤)/上/日]首佛': 1,
                 '首佛足': 1, '佛足敬': 1, '足敬強': 1, '敬強阿': 1,
                 '強阿闍': 1, '闍世耶': 1, '世耶又': 1}),
            (4, {'阿闍世[(禾*尤)/上/日]': 1, '闍世[(禾*尤)/上/日]首': 1,
                 '世[(禾*尤)/上/日]首佛': 1, '[(禾*尤)/上/日]首佛足': 1,
                 '首佛足敬': 1, '佛足敬強': 1, '足敬強阿': 1,
                 '敬強阿闍': 1, '強阿闍世': 1, '阿闍世耶': 1,
                 '闍世耶又': 1})]
        for actual, expected in zip(text.get_ngrams(3, 4), expected_ngrams):
            self.assertEqual(actual[0], expected[0])
            self.assertEqual(actual[1], collections.Counter(expected[1]))

    def test_get_tokens_cbeta (self):
        content = '阿闍世[(禾*尤)\n/上/日]首佛足。敬強阿闍世耶。又'
        text = tacl.Text('test', 'base', content, self._tokenizer)
        expected_tokens = ['阿', '闍', '世', '[(禾*尤)\n/上/日]', '首', '佛',
                           '足', '敬', '強', '阿', '闍', '世', '耶', '又']
        actual_tokens = text.get_tokens()
        self.assertEqual(actual_tokens, expected_tokens)

    def test_get_tokens_pagel (self):
        content = "bka' stsal pa | rigs kyi\nbu dag de'i || rigs kyi"
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        text = tacl.Text('test', 'base', content, tokenizer)
        expected_tokens = ["bka'", "stsal", "pa", "rigs", "kyi", "bu", "dag",
                           "de'i", "rigs", "kyi"]
        actual_tokens = text.get_tokens()
        self.assertEqual(actual_tokens, expected_tokens)


if __name__ == '__main__':
    unittest.main()
