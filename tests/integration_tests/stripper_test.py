#!/usr/bin/env python3

import os
import shutil
import unittest

import tacl


class StripperIntegrationTestCase (unittest.TestCase):

    def setUp (self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'data')
        self._xml_dir = os.path.join(self._data_dir, 'expected_corpus_output')
        self._actual_output_dir = os.path.join(
            self._data_dir, 'actual_stripped_output')
        self._expected_output_dir = os.path.join(
            self._data_dir, 'expected_stripped_output')
        if os.path.exists(self._actual_output_dir):
            raise Exception('{} exists; aborting test that would create '
                            'this directory'.format(self._expected_output_dir))

    def tearDown (self):
        if os.path.exists(self._actual_output_dir):
            shutil.rmtree(self._actual_output_dir)

    def test_strip_files (self):
        stripper = tacl.Stripper(self._xml_dir, self._actual_output_dir)
        stripper.strip_files()
        expected_files = ['T0001/base.txt', 'T0001/大.txt', 'T0001/宋.txt',
                          'T0002/base.txt', 'T0003/base.txt', 'T0003/元.txt',
                          'T0003/明.txt', 'T0003/宋.txt']
        for filename in expected_files:
            actual_path = os.path.join(self._actual_output_dir, filename)
            expected_path = os.path.join(self._expected_output_dir, filename)
            self.assertTrue(os.path.exists(actual_path),
                            'Expected file {} to exist, but it does not'.format(
                    actual_path))
            with open(actual_path, 'r') as fh:
                actual_content = fh.readlines()
            with open(expected_path) as fh:
                expected_content = fh.readlines()
            self.maxDiff = None
            self.assertEqual(actual_content, expected_content, 'Expected contents of {} to match {}'.format(actual_path, expected_path))
        # Check that no extra files are created.
        files = set()
        for directory in ['T0001', 'T0002', 'T0003']:
            output_dir = os.path.join(self._actual_output_dir, directory)
            for filename in os.listdir(output_dir):
                files.add(os.path.join(directory, filename))
        self.assertEqual(files, set(expected_files))


if __name__ == '__main__':
    unittest.main()
