import csv
import io
import unittest
import unittest.mock

import tacl


class TaclTestCase (unittest.TestCase):

    def _create_csv (self, data, fieldnames=tacl.constants.QUERY_FIELDNAMES):
        fh = io.StringIO(newline='')
        writer = csv.writer(fh)
        writer.writerow(fieldnames)
        for row in data:
            writer.writerow(row)
        fh.seek(0)
        return fh

    def _create_patch (self, name, spec=True):
        patcher = unittest.mock.patch(name, autospec=spec, spec_set=spec)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def _get_rows_from_csv (self, fh):
        rows = []
        fh.seek(0)
        reader = csv.reader(fh)
        for row in reader:
            rows.append(tuple(row))
        return rows[1:]
