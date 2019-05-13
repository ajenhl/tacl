"""Test suite for the normaliser/variant handling code."""

import os.path

from tacl import constants, exceptions, VariantMapping, Tokenizer
from ..tacl_test_case import TaclTestCase


class VariantMappingTestCase(TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, 'normaliser_data')
        self._mapping_dir = os.path.join(data_dir, 'mappings')
        self._tokenizer = Tokenizer(*constants.TOKENIZERS['cbeta'])

    def test_denormalise_simple(self):
        mapping_path = os.path.join(self._mapping_dir, 'map1.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        text = 'AQA'
        actual = mapping.denormalise(text)
        expected = [
            'ABCA',
            'NBCA',
            'ABCN',
            'NBCN',
            'OPBCA',
            'ABCOP',
            'OPBCOP',
            'AQA',
            'ARSTA',
            'AUA',
            'NQA',
            'AQN',
            'NQN',
            'OPQA',
            'AQOP',
            'OPQOP',
            'NRSTA',
            'ARSTN',
            'NRSTN',
            'OPRSTA',
            'ARSTOP',
            'OPRSTOP',
            'NUA',
            'AUN',
            'NUN',
            'OPUA',
            'AUOP',
            'OPUOP',
            'OPUN',
            'OPRSTN',
            'NRSTOP',
            'OPBCN',
            'OPQN',
            'NQOP',
            'NBCOP',
            'NUOP',
        ]
        self.assertEqual(set(actual), set(expected))

    def test_denormalise_complex(self):
        mapping_path = os.path.join(self._mapping_dir, 'map3.csv')
        tokenizer = Tokenizer(*constants.TOKENIZERS['latin'])
        mapping = VariantMapping(mapping_path, tokenizer)
        text = 'then that thatched anthem hit bees'
        expected = [
            'then that thatched anthem hit bees',
            'then the thatched anthem hit bees',
            'then that thatched anthem hit the ant',
            'then the thatched anthem hit the ant',
            "then Mozart's thatched anthem hit bees",
            "then Mozart's thatched anthem hit the ant",
        ]
        actual = mapping.denormalise(text)
        self.assertEqual(set(actual), set(expected))

    def test_mapping_duplicate_normalised_forms(self):
        mapping_path = os.path.join(self._mapping_dir,
                                    'duplicate_normalised.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        self.assertRaises(exceptions.MalformedNormaliserMappingError,
                          mapping.normalise, 'foo')

    def test_mapping_empty_normalised_form(self):
        mapping_path = os.path.join(self._mapping_dir,
                                    'empty_normalised_form.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        self.assertRaises(exceptions.MalformedNormaliserMappingError,
                          mapping.normalise, 'foo')

    def test_mapping_empty_variant(self):
        mapping_path = os.path.join(self._mapping_dir, 'empty_variant.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        self.assertRaises(exceptions.MalformedNormaliserMappingError,
                          mapping.normalise, 'foo')

    def test_mapping_long_normalised_form(self):
        mapping_path = os.path.join(self._mapping_dir,
                                    'long_normalised_form.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        self.assertRaises(exceptions.MalformedNormaliserMappingError,
                          mapping.normalise, 'foo')

    def test_mapping_multiple_normalised_forms(self):
        mapping_path = os.path.join(self._mapping_dir,
                                    'multiple_normalised.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        self.assertRaises(exceptions.MalformedNormaliserMappingError,
                          mapping.normalise, 'foo')

    def test_mapping_no_variants(self):
        mapping_path = os.path.join(self._mapping_dir, 'no_variants.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        self.assertRaises(exceptions.MalformedNormaliserMappingError,
                          mapping.normalise, 'foo')

    def test_normalise_simple(self):
        mapping_path = os.path.join(self._mapping_dir, 'map1.csv')
        mapping = VariantMapping(mapping_path, self._tokenizer)
        text = 'DURSTYVWX'
        expected = 'DQQDDD'
        actual = mapping.normalise(text)
        self.assertEqual(actual, expected)

    def test_normalise_complex(self):
        mapping_path = os.path.join(self._mapping_dir, 'map3.csv')
        tokenizer = Tokenizer(*constants.TOKENIZERS['latin'])
        mapping = VariantMapping(mapping_path, tokenizer)
        text = 'then the anthem hit the ant'
        expected = 'then that anthem hit bees'
        actual = mapping.normalise(text)
        self.assertEqual(actual, expected)
