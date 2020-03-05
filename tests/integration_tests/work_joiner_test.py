import os
import shutil
import tempfile

import tacl
from ..tacl_test_case import TaclTestCase


class WorkJoinerTestCase (TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'data', 'work_joiner')
        self._corpus_dir = os.path.join(self._data_dir, 'corpus')

    def _setup(self, temp_dir):
        actual_dir = os.path.join(temp_dir, 'corpus')
        shutil.copytree(self._corpus_dir, actual_dir)
        return tacl.WorkJoiner(actual_dir), actual_dir

    def test_output_exists_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            joiner, actual_dir = self._setup(temp_dir)
            self.assertRaises(tacl.exceptions.TACLError, joiner.join,
                              'T0001-3', ['T0001-1', 'T0001-2'])

    def test_work_joiner(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            joiner, actual_dir = self._setup(temp_dir)
            expected_dir = os.path.join(self._data_dir, 'expected')
            joiner.join('output', ['T0001-1', 'T0001-2'])
            self._compare_dirs(actual_dir, expected_dir)
