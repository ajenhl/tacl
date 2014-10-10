#!/usr/bin/env python3

import unittest

from lxml import etree

import tacl


class StripTestCase (unittest.TestCase):

    def setUp (self):
        self.transform = etree.XSLT(etree.XML(tacl.stripper.STRIP_XSLT))

    def test_get_witnesses (self):
        """Tests that all of the witnesses of variant readings are extracted
        from a text.

        """
        stripper = tacl.Stripper('.', '.')
        input_xml = '''
<div>
  <app><lem wit="【CBETA】">念</lem><rdg wit="【大】">忘</rdg></app>
  <app n="0001008"><lem wit="【大】">閹</lem><rdg resp="Taisho" wit="【宋】【元】">掩</rdg></app>
  <app n="0001012"><lem wit="【大】">後秦弘始年</lem><rdg resp="Taisho" wit="【宋】【元】【明】">姚秦三藏法師</rdg></app>
  <app><lem with="【三】">毗</lem><rdg wit="【大】">毘</rdg></app>
</div>
        '''
        expected_witnesses = set(('大', '宋', '元', '明',
                                  tacl.stripper.BASE_WITNESS))
        actual_witnesses = stripper.get_witnesses(etree.XML(input_xml))
        self.assertEqual(expected_witnesses, actual_witnesses)

    def test_foreign (self):
        """Tests that foreign elements with @place="foot" are stripped."""
        foreign_data = (
            ('<foreign n="0018011" resp="Taisho" lang="san">Saalva</foreign>',
             'Saalva'),
            ('<foreign n="0018011" resp="Taisho" lang="san" place="foot">Saalva</foreign>',
             ''),
            )
        for input_xml, expected_output in foreign_data:
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

    def test_tt (self):
        """Tests that tt is stripped down to the content of
        t[@lang='chi']."""
        input_xml = '''<tt n="0001011" type="app"><t resp="Taisho" lang="chi">長阿含經</t><t resp="Taisho" lang="san" place="foot">Dīrgha-āgama</t><t resp="Taisho" lang="pli" place="foot">Dīgha-nikāya</t></tt>'''
        expected_output = '長阿含經'
        actual_output = str(self.transform(etree.XML(input_xml)))
        self.assertEqual(expected_output, actual_output)

    def test_variants (self):
        """Tests that lem/rdg is stripped when it doesn't match the supplied
        witness name."""
        input_xml = '''
<body>
  <p><app n="0083004"><lem wit="【大】">釋。秦言能在直樹林。故名釋。釋。秦言亦言直</lem><rdg resp="Taisho" wit="【明】【？】">在直樹林故名釋懿</rdg><rdg resp="Taisho" wit="【甲】">佛法</rdg></app></p>
</body>'''
        # With the base witness name provided (ie, use the lem).
        expected_output = '''
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        actual_output = str(
            self.transform(etree.XML(input_xml),
                           witness="'{}'".format(tacl.stripper.BASE_WITNESS)))
        self.assertEqual(expected_output, actual_output)
        # With a witness name provided that occurs in a rdg.
        expected_output = '''
在直樹林故名釋懿'''
        actual_output = str(self.transform(etree.XML(input_xml),
                                           witness="'明'"))
        self.assertEqual(expected_output, actual_output)
        # With a witness name provided that occurs in the lem.
        expected_output = '''
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        actual_output = str(self.transform(etree.XML(input_xml),
                                           witness="'大'"))
        self.assertEqual(expected_output, actual_output)
        # A particular witness may not be listed either in the lem or
        # a rdg, in which case the lem must be used.
        expected_output = '''
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        actual_output = str(self.transform(etree.XML(input_xml),
                                           witness="'元'"))
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
