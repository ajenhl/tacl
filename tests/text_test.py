#!/usr/bin/env python3

import collections
import unittest
from unittest.mock import call, MagicMock, sentinel

import tacl
from .tacl_test_case import TaclTestCase


class TextTestCase (TaclTestCase):

    def setUp (self):
        self._tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                         tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_assemble_filename (self):
        actual_filename = tacl.Text.assemble_filename('T1', 'base')
        expected_filename = 'T1/base.txt'
        self.assertEqual(actual_filename, expected_filename)

    def test_get_checksum (self):
        content = '阿闍世[(禾*尤)/上/日]首佛足。敬\n強耶。又'
        text = tacl.Text('test', 'base', content, self._tokenizer)
        actual_checksum = text.get_checksum()
        expected_checksum = 'a94e3a20bc95a93710487611e65484d1'
        self.assertEqual(actual_checksum, expected_checksum)

    def test_get_filename (self):
        text = tacl.Text('test', 'base', 'test content', self._tokenizer)
        actual_filename = text.get_filename()
        expected_filename = 'test/base.txt'
        self.assertEqual(actual_filename, expected_filename)

    def test_get_names (self):
        text = tacl.Text('T1', 'base', 'test content', self._tokenizer)
        actual_names = text.get_names()
        expected_names = ('T1', 'base')
        self.assertEqual(actual_names, expected_names)

    def test_get_ngrams (self):
        # Being a static method, a mock of tacl.Text.ngrams using
        # autospec will be non-callable, so avoid this.
        ngrams = self._create_patch('tacl.Text._ngrams', False)
        sample_ngrams = ['a', 'b', 'c']
        ngrams.return_value = sample_ngrams
        get_tokens = self._create_patch('tacl.Text.get_tokens')
        get_tokens.return_value = sentinel.tokens
        collection = collections.Counter(sample_ngrams)
        text = tacl.Text('test', 'base', 'test content', self._tokenizer)
        actual_ngrams = list(text.get_ngrams(2, 3))
        expected_ngrams = [(2, collection), (3, collection)]
        get_tokens.assert_called_once_with(text)
        self.assertEqual(ngrams.mock_calls,
                         [call(sentinel.tokens, 2), call(sentinel.tokens, 3)])
        self.assertEqual(actual_ngrams, expected_ngrams)

    def test_get_tokens (self):
        content = '阿闍世[(禾*尤)/上/日]首佛足。敬\n強耶。又'
        self._tokenizer.tokenize = MagicMock(return_value=sentinel.tokens)
        text = tacl.Text('test', 'base', content, self._tokenizer)
        actual_tokens = text.get_tokens()
        self._tokenizer.tokenize.assert_called_once_with(content)
        self.assertEqual(actual_tokens, sentinel.tokens)

    def test_ngrams_cbeta (self):
        content = ''
        text = tacl.Text('test', 'base', content, self._tokenizer)
        tokens = ['阿', '闍', '世', '[(禾*尤)\n/上/日]', '首', '佛', '足',
                  '敬', '強', '耶', '又']
        expected_ngrams = [
            '阿闍世', '闍世[(禾*尤)/上/日]', '世[(禾*尤)/上/日]首',
            '[(禾*尤)/上/日]首佛', '首佛足', '佛足敬', '足敬強', '敬強耶',
            '強耶又'
            ]
        actual_ngrams = text._ngrams(tokens, 3)
        self.assertEqual(expected_ngrams, actual_ngrams)

    def test_ngrams_pagel (self):
        content = ''
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        text = tacl.Text('test', 'base', content, tokenizer)
        tokens = ["dpa'", "sems", "dpa'", "chen", "po", "rnam", "par", "mi"]
        expected_ngrams = [
            "dpa' sems dpa'", "sems dpa' chen", "dpa' chen po", "chen po rnam",
            "po rnam par", "rnam par mi"
        ]
        actual_ngrams = text._ngrams(tokens, 3)
        self.assertEqual(expected_ngrams, actual_ngrams)


if __name__ == '__main__':
    unittest.main()
