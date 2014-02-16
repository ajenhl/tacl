#!/usr/bin/env python3

import os
import shutil
import unittest

import tacl


class TEICorpusIntegrationTestCase (unittest.TestCase):

    def setUp (self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'data')
        self._cbeta_xml_dir = os.path.join(self._data_dir, 'cbeta_xml')
        self._xml_dir = os.path.join(self._data_dir, 'xml')
        self._actual_output_dir = os.path.join(
            self._data_dir, 'actual_corpus_output')
        self._expected_output_dir = os.path.join(
            self._data_dir, 'expected_corpus_output')
        for path in (self._xml_dir, self._actual_output_dir):
            if os.path.exists(path):
                raise Exception('{} exists; aborting test that would create '
                                'this directory'.format(path))
        # Copy the source XML files. This is necessary since the
        # splitting process must sometimes modify the source CBETA
        # files to pass validation.
        shutil.copytree(self._cbeta_xml_dir, self._xml_dir)

    def tearDown (self):
        for path in (self._xml_dir, self._actual_output_dir):
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_tidy (self):
        corpus = tacl.TEICorpus(self._xml_dir, self._actual_output_dir)
        corpus.tidy()
        expected_files = ['T0001.xml', 'T0002.xml', 'T0003.xml']
        for filename in expected_files:
            actual_path = os.path.join(self._actual_output_dir, filename)
            self.assertTrue(os.path.exists(actual_path),
                            'Expected file {} to exist, but it does not'.format(
                    actual_path))
            with open(actual_path, 'r') as fh:
                actual_content = fh.readlines()
            with open(os.path.join(self._expected_output_dir, filename)) as fh:
                expected_content = fh.readlines()
            self.assertEqual(actual_content, expected_content)
        # Check that no extra files are created.
        self.assertEqual(set(os.listdir(self._actual_output_dir)),
                         set(expected_files))
