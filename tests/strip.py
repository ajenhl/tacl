# -*- coding: utf-8 -*-

import unittest

import tacl


class TestStrip (unittest.TestCase):

    def test_strip_line (self):
        stripper = tacl.Stripper('.', '.')
        data = (
            (u' Taisho Tripitaka Vol. 1, No. 7.', u''),
            (u'T0007_.01.0191b02: No.7[No.1(2),Nos.5,6]',
             u' No.7[No.1(2),Nos.5,6]'),
            (u'T0007_.01.0191b03: 《大般涅槃經》卷上',
             u' 《大般涅槃經》卷上'),
            (u'T0007_.01.0199c07: 三者波羅&M049171;國鹿', u' 三者波羅國鹿'),
            (u'T1023_.19.0715a08║尼經', u'尼經'),
            (u'T1023_.19.0715a04∥尼經', u'尼經'),
            )
        for input_line, expected_output in data:
            actual_output = stripper._strip_line(input_line)
            self.assertEqual(actual_output, expected_output)

if __name__ == '__main__':
    unittest.main()
