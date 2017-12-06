#!/usr/bin/env python3

import collections
import unittest

import tacl
from .tacl_test_case import TaclTestCase


class TextTestCase (TaclTestCase):

    def setUp(self):
        self._tokenizer = tacl.Tokenizer(
            tacl.constants.TOKENIZER_PATTERN_CBETA,
            tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_excise(self):
        content = 'abcd efgh. ije'
        excised_ngrams = ['b', 'de', 'je', 'hij']
        replacement = 'F'
        text = tacl.Text(content, self._tokenizer)
        actual_content = text.excise(excised_ngrams, replacement)
        expected_content = 'aFcFfgFe'
        self.assertEqual(actual_content, expected_content)

    def test_get_ngrams(self):
        content = '阿闍世[(禾*尤)\n/上/日]首佛足。敬強阿闍世耶。又'
        text = tacl.WitnessText('test', 'base', content, self._tokenizer)
        expected_ngrams = [
            (3, collections.Counter(
                ['阿闍世', '闍世[(禾*尤)/上/日]', '世[(禾*尤)/上/日]首',
                 '[(禾*尤)/上/日]首佛', '首佛足', '佛足敬', '足敬強',
                 '敬強阿', '強阿闍', '阿闍世', '闍世耶', '世耶又'])),
            (4, collections.Counter(
                ['阿闍世[(禾*尤)/上/日]', '闍世[(禾*尤)/上/日]首',
                 '世[(禾*尤)/上/日]首佛', '[(禾*尤)/上/日]首佛足',
                 '首佛足敬', '佛足敬強', '足敬強阿', '敬強阿闍',
                 '強阿闍世', '阿闍世耶', '闍世耶又']))
        ]
        actual_ngrams = list(text.get_ngrams(3, 4))
        self.assertEqual(actual_ngrams, expected_ngrams)

    def test_get_token_content_cbeta(self):
        content = '阿闍世[(禾*尤)\n/上/日]首佛足。敬強阿闍世耶。又'
        text = tacl.WitnessText('test', 'base', content, self._tokenizer)
        expected_content = '阿闍世[(禾*尤)\n/上/日]首佛足敬強阿闍世耶又'
        actual_content = text.get_token_content()
        self.assertEqual(actual_content, expected_content)

    def test_get_token_content_pagel(self):
        content = "bka' stsal pa  | rigs kyi\nbu dag de'i || rigs kyi"
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        text = tacl.WitnessText('test', 'base', content, tokenizer)
        expected_content = "bka' stsal pa rigs kyi bu dag de'i rigs kyi"
        actual_content = text.get_token_content()
        self.assertEqual(actual_content, expected_content)

    def test_get_tokens_cbeta(self):
        content = '阿闍世[(禾*尤)\n/上/日]首佛足。敬\n強耶。又'
        text = tacl.Text(content, self._tokenizer)
        expected_tokens = ['阿', '闍', '世', '[(禾*尤)\n/上/日]', '首', '佛',
                           '足', '敬', '強', '耶', '又']
        actual_tokens = text.get_tokens()
        self.assertEqual(actual_tokens, expected_tokens)

    def test_get_tokens_pagel(self):
        content = "bka' stsal pa  | rigs kyi\nbu dag de'i || rigs kyi"
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        text = tacl.Text(content, tokenizer)
        expected_content = ["bka'", 'stsal', 'pa', 'rigs', 'kyi', 'bu', 'dag',
                            "de'i", 'rigs', 'kyi']
        actual_content = text.get_tokens()
        self.assertEqual(actual_content, expected_content)


class WitnessTextTestCase (TaclTestCase):

    def setUp(self):
        self._tokenizer = tacl.Tokenizer(
            tacl.constants.TOKENIZER_PATTERN_CBETA,
            tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_assemble_filename(self):
        actual_filename = tacl.WitnessText.assemble_filename('T1', 'base')
        expected_filename = 'T1/base.txt'
        self.assertEqual(actual_filename, expected_filename)

    def test_get_checksum(self):
        content = '阿闍世[(禾*尤)/上/日]首佛足。敬\n強耶。又'
        text = tacl.WitnessText('test', 'base', content, self._tokenizer)
        actual_checksum = text.get_checksum()
        expected_checksum = 'a94e3a20bc95a93710487611e65484d1'
        self.assertEqual(actual_checksum, expected_checksum)

    def test_get_filename(self):
        text = tacl.WitnessText('test', 'base', 'test content',
                                self._tokenizer)
        actual_filename = text.get_filename()
        expected_filename = 'test/base.txt'
        self.assertEqual(actual_filename, expected_filename)

    def test_get_names(self):
        text = tacl.WitnessText('T1', 'base', 'test content', self._tokenizer)
        actual_names = text.get_names()
        expected_names = ('T1', 'base')
        self.assertEqual(actual_names, expected_names)


class FilteredWitnessTextTestCase (TaclTestCase):

    def setUp(self):
        self._tokenizer = tacl.Tokenizer(
            tacl.constants.TOKENIZER_PATTERN_CBETA,
            tacl.constants.TOKENIZER_JOINER_CBETA)

    def test_get_ngrams(self):
        content = '阿闍世[(禾*尤)\n/上/日]首 佛足敬 強闍世耶又'
        minimum = 2
        maximum = 3
        filter_ngrams = ['闍世', '[(禾*尤)/上/日]首佛', '佛足敬強']
        text = tacl.FilteredWitnessText('test', 'base', content,
                                        self._tokenizer)
        actual_ngrams = list(text.get_ngrams(minimum, maximum, filter_ngrams))
        expected_ngrams = [
            (2, collections.Counter(['闍世', '闍世'])),
            (3, collections.Counter(
                ['阿闍世', '闍世[(禾*尤)/上/日]', '[(禾*尤)/上/日]首佛',
                 '強闍世', '闍世耶']))
        ]
        self.assertEqual(actual_ngrams, expected_ngrams)


if __name__ == '__main__':
    unittest.main()
