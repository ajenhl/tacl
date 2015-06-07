import os.path
import unittest

import tacl
from tacl.exceptions import MalformedCatalogueError


class CatalogueIntegrationTest (unittest.TestCase):

    def setUp (self):
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_load (self):
        catalogue = tacl.Catalogue()
        catalogue.load(os.path.join(self._data_dir, 'catalogue2.txt'))
        expected_dict = {'T1': 'A', 'T2': 'B', 'T3': 'C', 'T5': 'A'}
        self.assertEqual(catalogue, expected_dict)

    def test_load_relabelled_text (self):
        catalogue = tacl.Catalogue()
        path = os.path.join(self._data_dir, 'catalogue_relabel.txt')
        self.assertRaises(MalformedCatalogueError, catalogue.load, path)


if __name__ == '__main__':
    unittest.main()
