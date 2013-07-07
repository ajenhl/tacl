import os.path
import unittest

import tacl


class CatalogueIntegrationTest (unittest.TestCase):

    def setUp (self):
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_load (self):
        catalogue = tacl.Catalogue()
        catalogue.load(os.path.join(self._data_dir, 'catalogue2.txt'))
        expected_dict = {'1.txt': 'A', '2.txt': 'B', '3.txt': 'C', '5.txt': 'A'}
        self.assertEqual(catalogue, expected_dict)


if __name__ == '__main__':
    unittest.main()
