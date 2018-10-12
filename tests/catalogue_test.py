#!/usr/bin/env python3

import unittest
from unittest.mock import call, mock_open, patch, sentinel

import tacl
from .tacl_test_case import TaclTestCase


class CatalogueTestCase (TaclTestCase):

    def test_generate(self):
        listdir = self._create_patch('os.listdir')
        listdir.return_value = [sentinel.filename1, sentinel.filename2]
        catalogue = tacl.Catalogue()
        catalogue.generate(sentinel.path, sentinel.label)
        listdir.assert_called_once_with(sentinel.path)
        self.assertEqual(catalogue.get(sentinel.filename1), sentinel.label)
        self.assertEqual(catalogue.get(sentinel.filename2), sentinel.label)
        self.assertEqual(catalogue.get(sentinel.filename3), None)

    def test_get_works_by_label(self):
        catalogue = tacl.Catalogue()
        catalogue['T1'] = 'label1'
        catalogue['T2'] = 'label2'
        catalogue['T3'] = 'label1'
        actual_works = catalogue.get_works_by_label('label1')
        expected_works = ['T1', 'T3']
        self.assertEqual(set(actual_works), set(expected_works))

    def test_labels(self):
        catalogue = tacl.Catalogue()
        catalogue['T0123'] = 'label1'
        catalogue['T3210'] = 'label2'
        catalogue['T2301'] = 'label1'
        self.assertEqual(catalogue.labels, ['label1', 'label2'])

    def test_load(self):
        # Unfortunately I can't see how to get mock_open to return
        # suitable data on iteration, so this test is extremely
        # limited.
        with patch('builtins.open', mock_open(), create=True) as m:
            catalogue = tacl.Catalogue()
            catalogue.load(sentinel.path)
        m.assert_called_once_with(sentinel.path, 'r', encoding='utf-8',
                                  newline='')

    def test_ordered_labels_not_load(self):
        # When a catalogue is populated by means other than its load
        # method, the ordered labels are in string sort order.
        catalogue = tacl.Catalogue()
        catalogue['T1'] = 'label2'
        catalogue['T2'] = 'label3'
        catalogue['T3'] = 'label1'
        self.assertEqual(catalogue.ordered_labels,
                         ['label1', 'label2', 'label3'])

    def test_relabel(self):
        catalogue = tacl.Catalogue()
        catalogue['T0123'] = 'label1'
        catalogue['T3210'] = 'label1'
        catalogue['T2301'] = 'label2'
        catalogue['T1230'] = 'label3'
        catalogue['T3012'] = 'label4'
        relabelling = {
            'label1': 'label3',
            'label2': 'label1',
            'label3': 'label2',
        }
        relabelled_catalogue = catalogue.relabel(relabelling)
        self.assertEqual(relabelled_catalogue['T0123'], 'label3')
        self.assertEqual(relabelled_catalogue['T3210'], 'label3')
        self.assertEqual(relabelled_catalogue['T2301'], 'label1')
        self.assertEqual(relabelled_catalogue['T1230'], 'label2')
        self.assertNotIn('T3012', relabelled_catalogue)

    def test_remove_label(self):
        catalogue = tacl.Catalogue()
        catalogue['T0123'] = 'label1'
        catalogue['T3210'] = 'label1'
        catalogue['T2301'] = 'label2'
        catalogue.remove_label('label1')
        self.assertEqual(catalogue.labels, ['label2'])
        self.assertNotIn('T0123', catalogue)
        self.assertNotIn('T3210', catalogue)

    def test_save(self):
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
