#!/usr/bin/env python3

import os.path
import unittest
from unittest.mock import call, MagicMock, mock_open, patch, sentinel

import tacl
from .tacl_test_case import TaclTestCase


class CorpusTestCase (TaclTestCase):

    def test_get_text (self):
        Text = self._create_patch('tacl.corpus.Text')
        path = '/test'
        filename = 'foo.txt'
        m = mock_open(read_data=sentinel.content)
        with patch('builtins.open', m, create=True):
            corpus = tacl.Corpus(path)
            actual_text = corpus.get_text(filename)
        m.assert_called_once_with(os.path.join(path, filename),
                                  encoding='utf-8')
        Text.assert_called_once_with(filename, sentinel.content)
        assert isinstance(actual_text, tacl.Text)

    def test_get_texts (self):
        listdir = self._create_patch('os.listdir')
        listdir.return_value = [sentinel.filename1, sentinel.filename2]
        get_text = self._create_patch('tacl.Corpus.get_text')
        get_text.return_value = MagicMock(spec_set=tacl.Text)
        path = '/'
        corpus = tacl.Corpus(path)
        for text in corpus.get_texts():
            assert isinstance(text, tacl.Text)
        listdir.assert_called_once_with(path)
        self.assertEqual(get_text.mock_calls,
                         [call(corpus, sentinel.filename1),
                          call(corpus, sentinel.filename2)])


if __name__ == '__main__':
    unittest.main()
