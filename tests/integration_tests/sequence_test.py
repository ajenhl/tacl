import os
import shlex
import shutil
import subprocess
import unittest


class SequenceIntegrationTestCase (unittest.TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'sequence_data')
        self._actual_output_dir = os.path.join(self._data_dir, 'actual_output')
        if os.path.exists(self._actual_output_dir):
            raise Exception('{} exists; aborting test that would create '
                            'this directory'.format(self._actual_output_dir))

    def tearDown(self):
        if os.path.exists(self._actual_output_dir):
            shutil.rmtree(self._actual_output_dir)

    def test_file_creation(self):
        """Tests that only the expected files are created."""
        corpus_dir = os.path.join(self._data_dir, 'corpus')
        results = os.path.join(self._data_dir, 'results.csv')
        command = 'tacl align -m 4 {} {} {}'.format(
            corpus_dir, self._actual_output_dir, results)
        subprocess.call(shlex.split(command))
        expected_files = set(['T1_base-T3_base.html', 'T1_base-T3_wit1.html',
                              'T2_base-T3_base.html', 'T2_base-T3_wit1.html'])
        actual_files = set()
        for filename in os.listdir(self._actual_output_dir):
            actual_files.add(filename)
        self.assertEqual(actual_files, expected_files)
