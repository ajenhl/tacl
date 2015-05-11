#!/usr/bin/env python3

import unittest

from lxml import etree

import tacl


class TEICorpusTestCase (unittest.TestCase):

    def setUp (self):
        self.transform = etree.XSLT(etree.XML(tacl.tei_corpus.SIMPLIFY_XSLT))

    def test_gaiji (self):
        """Tests that the correct gaiji alternative is used."""
        gaiji_data = (
            ('''<p><gaiji uniflag='1' cb='Amacron' nor='AA' uni='0100'/></p>''', 'Ā'),
            ('''<p><gaiji uniflag='0' cb='CB00006' des='[(王*巨)/木]' uni='249B2' nor='璩' mojikyo='M021123' mofont='Mojikyo M104' mochar='6E82'/></p>''', '[(王*巨)/木]'),
            ('''<p><gaiji uniflag='' cb='SD-A440' cbdia='ka' udia='ka' sdchar='一'/></p>''', 'ka'),
            ('''<p><gaiji uniflag='' cb='RJ-CEBD' cbdia='yaa' udia='y&#x0101;' rjchar='彖'/></p>''', 'yā'),
            )
        for input_xml, expected_output in gaiji_data:
            actual_output = etree.tostring(self.transform(etree.XML(input_xml)).getroot(), method='text', encoding='unicode')
            self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
