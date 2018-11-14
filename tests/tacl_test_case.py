import csv
import filecmp
import io
import os.path
import shlex
import subprocess
import unittest
import unittest.mock

import tacl
from tacl.exceptions import MalformedResultsError


class TaclTestCase (unittest.TestCase):

    def _check_common(self, dircmp):
        for common_file in dircmp.common_files:
            actual_path = os.path.join(dircmp.left, common_file)
            expected_path = os.path.join(dircmp.right, common_file)
            if os.path.splitext(common_file)[0] == '.csv':
                self._compare_results_files(actual_path, expected_path)
            else:
                self._compare_non_results_files(actual_path, expected_path)
        for sd in dircmp.subdirs.values():
            self._check_common(sd)

    def _check_unshared(self, dircmp):
        self.assertEqual(dircmp.left_only, [], 'Actual results contains unexpected files and/or subdirectories in {}'.format(dircmp.left))
        self.assertEqual(dircmp.right_only, [], 'Actual results missing expected files and/or subdirectories found in {}'.format(dircmp.right))
        for sd in dircmp.subdirs.values():
            self._check_unshared(sd)

    def _compare_non_results_files(self, actual_path, expected_path):
        """Checks that the non-results files at `actual_path` and
        `expected_path` are the same."""
        with open(actual_path) as actual_fh:
            with open(expected_path) as expected_fh:
                self.assertEqual(actual_fh.read(), expected_fh.read())

    def _compare_results_dirs(self, actual_dir, expected_dir):
        # First check that the two directories contain only the same
        # files and subdirectories.
        dircmp = filecmp.dircmp(actual_dir, expected_dir)
        self._check_unshared(dircmp)
        # Then check that the common files are the same.
        self._check_common(dircmp)

    def _compare_results_files(self, actual_path, expected_path):
        """Checks that the results files at `actual_path` and `expected_path`
        contain the same results."""
        self.assertEqual(
            self._get_results(actual_path), self._get_results(expected_path),
            'Actual results in {} do not match expected results in {}'.format(
                actual_path, expected_path))

    def _create_csv(self, data, fieldnames=tacl.constants.QUERY_FIELDNAMES):
        fh = io.StringIO(newline='')
        writer = csv.writer(fh)
        writer.writerow(fieldnames)
        for row in data:
            writer.writerow(row)
        fh.seek(0)
        return fh

    def _create_patch(self, name, spec=True):
        patcher = unittest.mock.patch(name, autospec=spec, spec_set=spec)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def _get_results(self, path):
        rows = []
        with open(path, newline='') as fh:
            reader = csv.reader(fh)
            for row in reader:
                rows.append(tuple(row))
        return set(rows)

    def _get_rows_from_command(self, command):
        data = subprocess.check_output(shlex.split(command))
        return self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))

    def _get_rows_from_csv(self, fh):
        rows = []
        fh.seek(0)
        reader = csv.reader(fh)
        for row in reader:
            rows.append(tuple(row))
        return rows

    def _get_rows_from_file(self, path):
        with open(path, newline='') as fh:
            expected_rows = self._get_rows_from_csv(fh)
        return expected_rows

    def _get_rows_from_results(self, results):
        return self._get_rows_from_csv(results.csv(
            io.StringIO(newline='')))

    def _test_required_columns(self, cols, cmd, *args, **kwargs):
        """Tests that when `cmd` is run with `args` and `kwargs`, it raises a
        `MalformedResultsError when each of `cols` is not present in
        the results. Further tests that that exception is not raised
        when other columns are not present.

        This test is designed to test Results methods only.

        """
        input_results = (
            ['AB', '2', 'T1', 'base', '4', 'A'],
            ['AB', '2', 'T1', 'a', '3', 'A'],
            ['AB', '2', 'T2', 'base', '2', 'A'],
            ['ABC', '3', 'T1', 'base', '2', 'A'],
            ['ABC', '3', 'T1', 'a', '0', 'A'],
            ['AB', '2', 'T3', 'base', '2', 'B'],
            ['BC', '2', 'T1', 'base', '3', 'A'],
        )
        for col in tacl.constants.QUERY_FIELDNAMES:
            fs = list(tacl.constants.QUERY_FIELDNAMES[:])
            index = fs.index(col)
            fs[index] = 'dummy'
            fh = self._create_csv(input_results, fieldnames=fs)
            results = tacl.Results(fh, self._tokenizer)
            if col in cols:
                self.assertRaises(MalformedResultsError, getattr(results, cmd),
                                  *args, **kwargs)
            else:
                try:
                    getattr(results, cmd)(*args, **kwargs)
                except MalformedResultsError:
                    self.fail(
                        'Results.{} improperly raises MalformedResultsError '
                        'when column "{}" not present in results'.format(
                            cmd, col))
                except KeyError as e:
                    if str(e).strip('"\'') == col:
                        self.fail(
                            'Results.{} requires column "{}" but does not '
                            'specify this.'.format(cmd, col))
