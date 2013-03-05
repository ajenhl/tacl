#!/usr/bin/env python3

import unittest

import tacl


class TextTestCase (unittest.TestCase):

    def test_ingrams (self):
        text = '''阿闍世[(禾*尤)/上/日]首佛足。敬
強耶。又'''
        tokens = tacl.tokenizer.tokenize(text)
        expected_ngrams = [
            '阿闍世', '闍世[(禾*尤)/上/日]', '世[(禾*尤)/上/日]首',
            '[(禾*尤)/上/日]首佛', '首佛足', '佛足敬', '足敬強', '敬強耶',
            '強耶又'
            ]
        actual_ngrams = [ngram for ngram in tacl.Text.ingrams(tokens, 3)]
        self.assertEqual(expected_ngrams, actual_ngrams)
        # Whitespace occuring between [] should be removed.
        text = '''戈，[有神
作有]隱'''
        tokens = tacl.tokenizer.tokenize(text)
        expected_ngrams = ['戈[有神作有]', '[有神作有]隱']
        actual_ngrams = [ngram for ngram in tacl.Text.ingrams(tokens, 2)]
        self.assertEqual(expected_ngrams, actual_ngrams)

    def test_tokenize (self):
        data = (
            ('無願境', ['無', '願', '境']),
            ('言童子。汝', ['言', '童', '子', '汝']),
            ('黎(二)恥', ['黎', '二', '恥']),
            ('地[口*梨](十一)阿', ['地', '[口*梨]', '十', '一', '阿']),
            ('「導師化眾生！」', ['導', '師', '化', '眾', '生']),
            ('無,\t\r\n童 子：[二+梨 ]！', ['無', '童', '子', '[二+梨 ]']),
            )
        for input_text, expected_tokens in data:
            actual_tokens = tacl.tokenizer.tokenize(input_text)
            self.assertEqual(actual_tokens, expected_tokens)


if __name__ == '__main__':
    unittest.main()
