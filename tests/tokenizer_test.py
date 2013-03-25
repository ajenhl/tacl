#!/usr/bin/env python3

import unittest

import tacl


class TokenizerTestCase (unittest.TestCase):

    def test_init (self):
        self.assertRaises(ValueError, tacl.Tokenizer, r'[broken')

    def test_tokenize (self):
        tokenizer = tacl.Tokenizer(tacl.constants.TOKENIZER_PATTERN)
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


if __name__ == '__main__':
    unittest.main()
