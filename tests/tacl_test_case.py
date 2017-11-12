import csv
import io
import shlex
import subprocess
import unittest
import unittest.mock

import tacl


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
