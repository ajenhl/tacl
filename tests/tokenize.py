#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import tacl


class TestTokenize (unittest.TestCase):

    def test_tokenize (self):
        data = (
            (u'無願境', [u'無', u'願', u'境']),
            (u'言童子。汝', [u'言', u'童', u'子', u'汝']),
            (u'黎(二)恥', [u'黎', u'二', u'恥']),
            (u'地[口*梨](十一)阿', [u'地', u'[口*梨]', u'十', u'一', u'阿']),
            )
        for input_text, expected_tokens in data:
            actual_tokens = tacl.Text.tokenizer.tokenize(input_text)
            self.assertEqual(actual_tokens, expected_tokens)


if __name__ == '__main__':
    unittest.main()
