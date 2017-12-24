#!/usr/bin/env python3

import tacl
from .tacl_test_case import TaclTestCase


class SequenceReportTestCase (TaclTestCase):

    def test_get_text(self):
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        input_data = (
            ['AB', '2', 't1', 'wit1', '2', 'A']
        )
        fh = self._create_csv(input_data)
        sequence_report = tacl.SequenceReport(None, tokenizer, fh)
        text = tacl.WitnessText('t1', 'wit1', 'abc[A+B]d', tokenizer)
        actual_text = sequence_report._get_text(text)
        expected_text = 'abc{}d'.format(chr(61440))
        self.assertEqual(actual_text, expected_text)
