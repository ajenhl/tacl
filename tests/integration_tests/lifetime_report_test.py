import os.path
import shlex
import subprocess
import tempfile

import tacl
from ..tacl_test_case import TaclTestCase


class LifetimeReportTestCase (TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'lifetime_report_data')

    def test_cli(self):
        expected_dir = os.path.join(self._data_dir, 'expected')
        catalogue_path = os.path.join(self._data_dir, 'catalogue.txt')
        results_path = os.path.join(self._data_dir, 'results.csv')
        label = 'A'
        with tempfile.TemporaryDirectory() as temp_dir:
            command = 'tacl lifetime {} {} {} {}'.format(
                catalogue_path, results_path, label, temp_dir)
            subprocess.run(shlex.split(command))
            self._compare_dirs(temp_dir, expected_dir)

    def test_generate(self):
        expected_dir = os.path.join(self._data_dir, 'expected')
        catalogue = tacl.Catalogue()
        catalogue.load(os.path.join(self._data_dir, 'catalogue.txt'))
        results_path = os.path.join(self._data_dir, 'results.csv')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        results = tacl.Results(results_path, tokenizer)
        label = 'A'
        with tempfile.TemporaryDirectory() as temp_dir:
            report = tacl.LifetimeReport()
            report.generate(temp_dir, catalogue, results, label)
            self._compare_dirs(temp_dir, expected_dir)
