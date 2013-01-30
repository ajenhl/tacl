#!/usr/bin/env python3

import unittest

import tacl


class TestTokenize (unittest.TestCase):

    def test_tokenize (self):
        data = (
            ('無願境', ['無', '願', '境']),
            ('言童子。汝', ['言', '童', '子', '汝']),
            ('黎(二)恥', ['黎', '二', '恥']),
            ('地[口*梨](十一)阿', ['地', '[口*梨]', '十', '一', '阿']),
            ('「導師化眾生！」', ['導', '師', '化', '眾', '生']),
            ('無,童子：[二+梨]！', ['無', '童', '子', '[二+梨]']),
            )
        for input_text, expected_tokens in data:
            actual_tokens = tacl.Text.tokenizer.tokenize(input_text)
            self.assertEqual(actual_tokens, expected_tokens)


if __name__ == '__main__':
    unittest.main()
