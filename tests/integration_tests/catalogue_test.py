import os.path
import unittest

import tacl
from tacl.exceptions import MalformedCatalogueError


class CatalogueIntegrationTest (unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_load(self):
        catalogue = tacl.Catalogue()
        catalogue.load(os.path.join(self._data_dir, 'catalogue2.txt'))
        expected_dict = {'T1': 'A', 'T2': 'B', 'T3': 'C', 'T5': 'A'}
        self.assertEqual(catalogue, expected_dict)

    def test_load_relabelled_text(self):
        catalogue = tacl.Catalogue()
        path = os.path.join(self._data_dir, 'catalogue_relabel.txt')
        self.assertRaises(MalformedCatalogueError, catalogue.load, path)

    def test_ordered_labels_load(self):
        catalogue = tacl.Catalogue()
        catalogue.load(os.path.join(self._data_dir, 'catalogue2.txt'))
        expected_labels = ['B', 'C', 'A']
        self.assertEqual(catalogue.ordered_labels, expected_labels)

    def test_ordered_labels_relabel(self):
        catalogue = tacl.Catalogue()
        catalogue.load(os.path.join(self._data_dir, 'catalogue4.txt'))
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
        self.assertNotIn('T1234', relabelled_catalogue)
        self.assertNotIn('T2341', relabelled_catalogue)

    def test_ordered_labels_remove(self):
        catalogue = tacl.Catalogue()
        catalogue.load(os.path.join(self._data_dir, 'catalogue2.txt'))
        catalogue.remove_label('C')
        self.assertEqual(catalogue.ordered_labels, ['B', 'A'])


if __name__ == '__main__':
    unittest.main()
