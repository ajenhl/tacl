#!/usr/bin/env python3

import collections
import unittest
from unittest.mock import call, sentinel

import tacl
from .tacl_test_case import TaclTestCase


class TextTestCase (TaclTestCase):

    def test_get_checksum (self):
        content = '阿闍世[(禾*尤)/上/日]首佛足。敬\n強耶。又'
        text = tacl.Text('test.txt', content)
        actual_checksum = text.get_checksum()
        expected_checksum = 'a94e3a20bc95a93710487611e65484d1'
        self.assertEqual(actual_checksum, expected_checksum)

    def test_get_filename (self):
        filename = 'test.txt'
        text = tacl.Text(filename, 'test content')
        actual_filename = text.get_filename()
        expected_filename = filename
        self.assertEqual(actual_filename, expected_filename)

    def test_get_ngrams (self):
        # Being a static method, a mock of tacl.Text.ngrams using
        # autospec will be non-callable, so avoid this.
        ngrams = self._create_patch('tacl.Text.ngrams', False)
        sample_ngrams = ['a', 'b', 'c']
        ngrams.return_value = sample_ngrams
        get_tokens = self._create_patch('tacl.Text.get_tokens')
        get_tokens.return_value = sentinel.tokens
        collection = collections.Counter(sample_ngrams)
        text = tacl.Text('test.txt', 'test content')
        actual_ngrams = list(text.get_ngrams(2, 3))
        expected_ngrams = [(2, collection), (3, collection)]
        get_tokens.assert_called_once_with(text)
        self.assertEqual(ngrams.mock_calls,
                         [call(sentinel.tokens, 2), call(sentinel.tokens, 3)])
        self.assertEqual(actual_ngrams, expected_ngrams)

    def test_get_tokens (self):
        content = '阿闍世[(禾*尤)/上/日]首佛足。敬\n強耶。又'
        tokenize = self._create_patch('tacl.Tokenizer.tokenize')
        tokenize.return_value = sentinel.tokens
        text = tacl.Text('test.txt', content)
        actual_tokens = text.get_tokens()
        tokenize.assert_called_once_with(text._tokenizer, content)
        self.assertEqual(actual_tokens, sentinel.tokens)

    def test_ngrams (self):
        tokens = ['阿', '闍', '世', '[(禾*尤)\n/上/日]', '首', '佛', '足',
                  '敬', '強', '耶', '又']
        expected_ngrams = [
            '阿闍世', '闍世[(禾*尤)/上/日]', '世[(禾*尤)/上/日]首',
            '[(禾*尤)/上/日]首佛', '首佛足', '佛足敬', '足敬強', '敬強耶',
            '強耶又'
            ]
        actual_ngrams = tacl.Text.ngrams(tokens, 3)
        self.assertEqual(expected_ngrams, actual_ngrams)


if __name__ == '__main__':
    unittest.main()
