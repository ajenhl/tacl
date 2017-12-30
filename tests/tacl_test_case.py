import csv
import io
import shlex
import subprocess
import unittest
import unittest.mock

import tacl
from tacl.exceptions import MalformedResultsError


class TaclTestCase (unittest.TestCase):

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

    def _get_rows_from_command(self, command):
        data = subprocess.check_output(shlex.split(command))
        return self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))

    def _get_rows_from_csv(self, fh):
        rows = []
        fh.seek(0)
        reader = csv.reader(fh)
        for row in reader:
            rows.append(tuple(row))
        return rows[1:]

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
