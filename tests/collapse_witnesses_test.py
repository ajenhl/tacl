#!/usr/bin/env python3

import io

from tacl.command.tacl_helper_script import _collapse_witnesses
from .tacl_test_case import TaclTestCase


class CollapseWitnessesTestCase (TaclTestCase):

    def test_collapse_witnesses (self):
        input_data = (
            ['一佛國所至到', '6', 'T0223', 'base', '2', 'KJ'],
            ['一佛國所至到', '6', 'T0223', '元', '2', 'KJ'],
            ['一佛國所至到', '6', 'T0223', '大', '1', 'KJ'],
            ['龜鴿', '2', 'T1509', '麗乙', '1', 'KJ'],
            ['龜鴿', '2', 'T1509', 'base', '1', 'KJ'],
            ['一佛國所至到', '6', 'T1509', '大', '1', 'KJ'],
            ['龜茲國鳩摩羅什', '7', 'T1207', 'base', '3', 'PP'],
            ['龜茲國鳩摩羅什', '7', 'T1207', '大', '3', 'PP'],
        )
        fh = self._create_csv(input_data)
        expected_rows = [
            ('一佛國所至到', '6', 'T0223', 'base 元', '2', 'KJ'),
            ('一佛國所至到', '6', 'T0223', '大', '1', 'KJ'),
            ('龜鴿', '2', 'T1509', 'base 麗乙', '1', 'KJ'),
            ('一佛國所至到', '6', 'T1509', '大', '1', 'KJ'),
            ('龜茲國鳩摩羅什', '7', 'T1207', 'base 大', '3', 'PP'),
        ]
        actual_rows = self._get_rows_from_csv(
            _collapse_witnesses(fh, io.StringIO(newline='')))
        self.assertEqual(set(actual_rows), set(expected_rows))
