#!/usr/bin/env python3

import unittest

import tacl
from .tacl_test_case import TaclTestCase


class ReportTestCase (TaclTestCase):

    def test_merge_slices (self):
        input_slices = [
            [4, 7], [6, 12], [4, 6], [13, 14], [1, 2], [12, 13], [15, 18]
        ]
        expected_slices = [[1, 2], [4, 14], [15, 18]]
        actual_slices = tacl.StatisticsReport._merge_slices(input_slices)
        self.assertEqual(actual_slices, expected_slices)


if __name__ == '__main__':
    unittest.main()
