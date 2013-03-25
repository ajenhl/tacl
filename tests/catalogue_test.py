#!/usr/bin/env python3

import unittest
from unittest.mock import call, mock_open, patch, sentinel

import tacl
from .tacl_test_case import TaclTestCase


class CatalogueTestCase (TaclTestCase):

    def test_generate (self):
        listdir = self._create_patch('os.listdir')
        listdir.return_value = [sentinel.filename1, sentinel.filename2]
        catalogue = tacl.Catalogue()
        catalogue.generate(sentinel.path, sentinel.label)
        listdir.assert_called_once_with(sentinel.path)
        self.assertEqual(catalogue.get(sentinel.filename1), sentinel.label)
        self.assertEqual(catalogue.get(sentinel.filename2), sentinel.label)
        self.assertEqual(catalogue.get(sentinel.filename3), None)

    def test_laod (self):
        # Unfortunately I can't see how to get mock_open to return
        # suitable data on iteration, so this test is extremely
        # limited.
        with patch('builtins.open', mock_open(), create=True) as m:
            catalogue = tacl.Catalogue()
            catalogue.load(sentinel.path)
        m.assert_called_once_with(sentinel.path, 'r', encoding='utf-8',
                                  newline='')

    def test_save (self):
        with patch('builtins.open', mock_open(), create=True) as m:
            catalogue = tacl.Catalogue()
            catalogue['filename1'] = 'label1'
            catalogue['filename2'] = 'label1'
            catalogue['filename3'] = 'label2'
            catalogue.save(sentinel.path)
        expected_calls = [call(sentinel.path, 'w', newline=''),
                          call().write('filename1 label1\r\n'),
                          call().write('filename2 label1\r\n'),
                          call().write('filename3 label2\r\n')]
        m.assert_has_calls(expected_calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
