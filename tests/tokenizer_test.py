#!/usr/bin/env python3

import unittest

import tacl


class TokenizerTestCase (unittest.TestCase):

    def test_init (self):
        self.assertRaises(ValueError, tacl.Tokenizer, r'[broken', '')

    def test_joiner (self):
        expected_joiner = ' '
        tokenizer = tacl.Tokenizer(r'[\w]+', expected_joiner)
        actual_joiner = tokenizer.joiner
        self.assertEqual(actual_joiner, expected_joiner)

    def test_pattern (self):
        expected_pattern = r'[\w]+'
        tokenizer = tacl.Tokenizer(expected_pattern, ' ')
        actual_pattern = tokenizer.pattern
        self.assertEqual(actual_pattern, expected_pattern)

    def test_tokenize_cbeta (self):
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_CBETA,
                                   tacl.constants.TOKENIZER_JOINER_CBETA)
        data = (
            ('無願境', ['無', '願', '境']),
            ('言童子。汝', ['言', '童', '子', '汝']),
            ('黎(二)恥', ['黎', '二', '恥']),
            ('地[口*梨](十一)阿', ['地', '[口*梨]', '十', '一', '阿']),
            ('「導師化眾生！」', ['導', '師', '化', '眾', '生']),
            ('無,\t\r\n童 子：[二+梨 ]！', ['無', '童', '子', '[二+梨 ]']),
            )
        for input_text, expected_tokens in data:
            actual_tokens = tokenizer.tokenize(input_text)
            self.assertEqual(actual_tokens, expected_tokens)

    def test_tokenize_pagel (self):
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN_PAGEL,
                                   tacl.constants.TOKENIZER_JOINER_PAGEL)
        data = (
            ("bcom ldan 'das", ["bcom", "ldan", "'das"]),
            ("so || lha'i", ["so", "lha'i"]),
            ("ba\tdang | zhe\r\nsdang", ["ba", "dang", "zhe", "sdang"]),
            ("pr-its+tshA", ["pr-its+tshA"]),
            ("rgya?sa", ["rgya?sa"]),
            ("hU~M", ["hU~M"]),
        )
        for input_text, expected_tokens in data:
            actual_tokens = tokenizer.tokenize(input_text)
            self.assertEqual(actual_tokens, expected_tokens)


if __name__ == '__main__':
    unittest.main()
