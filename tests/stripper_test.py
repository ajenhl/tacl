#!/usr/bin/env python3

import unittest

from lxml import etree

import tacl


class StripTestCase (unittest.TestCase):

    def setUp (self):
        self.transform = etree.XSLT(etree.XML(tacl.stripper.STRIP_XSLT))

    def test_gaiji (self):
        """Tests that the correct gaiji alternative is used."""
        gaiji_data = (
            ('''<gaiji uniflag='1' cb='Amacron' nor='AA' uni='0100'/>''', 'Ā'),
            ('''<gaiji uniflag='0' cb='CB00006' des='[(王*巨)/木]' uni='249B2' nor='璩' mojikyo='M021123' mofont='Mojikyo M104' mochar='6E82'/>''', '[(王*巨)/木]'),
            ('''<gaiji uniflag='' cb='SD-A440' cbdia='ka' udia='ka' sdchar='一'/>''', 'ka'),
            ('''<gaiji uniflag='' cb='RJ-CEBD' cbdia='yaa' udia='y&#x0101;' rjchar='彖'/>''', 'yā'),
            )
        for input_xml, expected_output in gaiji_data:
            actual_output = str(self.transform(etree.XML(input_xml)))
            self.assertEqual(expected_output, actual_output)

    def test_no_header (self):
        """Tests that the TEI header is stripped."""
        input_xml = '''
<TEI.2>
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Taisho Tripitaka, Electronic version, No. 0001 長阿含經</title>
        <author>後秦 佛陀耶舍共竺佛念譯</author>
      </titleStmt>
    </fileDesc>
    <encodingDesc>
      <projectDesc>
        <p lang="eng" type="ly">Text as provided by Mr. Hsiao Chen-Kuo, Text as provided by Mr. Chang Wen-Ming, Text as provided by Anonymous, USA</p>
        <p lang="chi" type="ly">蕭鎮國大德提供，張文明大德提供，北美某大德提供</p>
      </projectDesc>
    </encodingDesc>
    <profileDesc>
      <langUsage>
        <language id="pli">Pali</language>
        <language id="san">Sanskrit</language>
        <language id="eng">English</language>
        <language id="chi">Chinese</language>
      </langUsage>
    </profileDesc>
  </teiHeader>
  <text>
  </text>
</TEI.2>'''
        expected_output = ''
        actual_output = str(self.transform(etree.XML(input_xml)))
        self.assertEqual(expected_output, actual_output)

    def test_note (self):
        """Tests that notes, unless inline, are stripped."""
        input_xml = '''
<body>
  <p>苑。其為典也。淵博弘富。<note n="0001005" resp="Taisho" place="foot text" type="orig">韞＝溫【宋】【元】</note></p>
  <p><note place="inline">釋。秦言能在直樹林。故名釋。釋。秦言亦言直</note></p>
</body>'''
        expected_output = '''
苑。其為典也。淵博弘富。
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        actual_output = str(self.transform(etree.XML(input_xml)))
        self.assertEqual(expected_output, actual_output)

    def test_rdg (self):
        """Tests that rdg is stripped."""
        input_xml = '''
<body>
  <p><app n="0083004"><lem wit="【大】">釋。秦言能在直樹林。故名釋。釋。秦言亦言直</lem><rdg resp="Taisho" wit="【明】">在直樹林故名釋懿</rdg></app></p>
</body>'''
        expected_output = '''
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        actual_output = str(self.transform(etree.XML(input_xml)))
        self.assertEqual(expected_output, actual_output)

    def test_tt (self):
        """Tests that tt is stripped down to the content of
        t[@lang='chi']."""
        input_xml = '''<tt n="0001011" type="app"><t resp="Taisho" lang="chi">長阿含經</t><t resp="Taisho" lang="san" place="foot">Dīrgha-āgama</t><t resp="Taisho" lang="pli" place="foot">Dīgha-nikāya</t></tt>'''
        expected_output = '長阿含經'
        actual_output = str(self.transform(etree.XML(input_xml)))
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
