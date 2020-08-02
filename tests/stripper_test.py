#!/usr/bin/env python3

import unittest

from lxml import etree

import tacl


class StripTestCase (unittest.TestCase):

    def setUp(self):
        self.stripper = tacl.Stripper('.', '.')

    def test_byline(self):
        """Tests that byline elements are stripped without content."""
        input_xml = '''
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0" xmlns:cb="http://www.cbeta.org/ns/1.0" xml:id="T13n0397">
<TEI><text><body>
<byline cb:type="Translator">北涼天竺三藏曇無讖於姑臧譯</byline>
</body></text></TEI>
</teiCorpus>'''
        expected_output = ''
        self._transform_equality(input_xml, expected_output)

    def test_foreign(self):
        """Tests that foreign elements with @place="foot" are stripped without
        content."""
        foreign_data = (
            ('<foreign xmlns="http://www.tei-c.org/ns/1.0" n="0018011" '
             'resp="Taisho" lang="san">Saalva</foreign>', 'Saalva'),
            ('<foreign xmlns="http://www.tei-c.org/ns/1.0" n="0018011" '
             'resp="Taisho" lang="san" place="foot">Saalva</foreign>', ''),
        )
        for input_xml, expected_output in foreign_data:
            self._transform_equality(input_xml, expected_output)

    def test_get_witnesses(self):
        input_xml = '''
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Taisho Tripitaka, Electronic version, No. 0001 長阿含經</title>
        <author>後秦 佛陀耶舍共竺佛念譯</author>
      </titleStmt>
      <sourceDesc>
        <listWit>
          <witness xml:id="wit1">CBETA</witness>
          <witness xml:id="wit2">宋</witness>
          <witness xml:id="wit3">明</witness>
        </listWit>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
  <TEI>
    <teiHeader>
    </teiHeader>
    <text>
    </text>
  </TEI>
</teiCorpus>'''
        actual_witnesses = self.stripper.get_witnesses(etree.XML(input_xml))
        expected_witnesses = [('CBETA', 'wit1'), ('宋', 'wit2'), ('明', 'wit3')]
        self.assertEqual(actual_witnesses, expected_witnesses)

    def test_get_witnesses_no_witnesses(self):
        input_xml = '''
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Taisho Tripitaka, Electronic version, No. 0001 長阿含經</title>
        <author>後秦 佛陀耶舍共竺佛念譯</author>
      </titleStmt>
    </fileDesc>
  </teiHeader>
  <TEI>
    <teiHeader>
    </teiHeader>
    <text>
    </text>
  </TEI>
</teiCorpus>'''
        actual_witnesses = self.stripper.get_witnesses(etree.XML(input_xml))
        expected_witnesses = [(tacl.constants.BASE_WITNESS,
                               tacl.constants.BASE_WITNESS_ID)]
        self.assertEqual(actual_witnesses, expected_witnesses)

    def test_jhead(self):
        """Tests that cb:jhead elements are stripped without content."""
        input_xml = '''
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0" xmlns:cb="http://www.cbeta.org/ns/1.0" xml:id="T13n0397">
<TEI><text><body>
<cb:jhead>大方等大集經卷第一</cb:jhead>
</body></text></TEI>
</teiCorpus>'''
        expected_output = ''
        self._transform_equality(input_xml, expected_output)

    def test_juan(self):
        """Tests that cb:juan elements are stripped without content."""
        input_xml = '<cb:juan xmlns:cb="http://www.cbeta.org/ns/1.0" n="001" fun="close">大方等大集經卷第一</cb:juan>'
        expected_output = ''
        self._transform_equality(input_xml, expected_output)

    def test_mulu(self):
        """Tests that cb:mulu elements are stripped."""
        input_xml = '<cb:mulu xmlns:cb="http://www.cbeta.org/ns/1.0">1 大本經</cb:mulu>'
        expected_output = ''
        self._transform_equality(input_xml, expected_output)

    def test_no_header(self):
        """Tests that the TEI header is stripped."""
        input_xml = '''
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0">
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
  <TEI>
    <teiHeader>
      <fileDesc>
        <titleStmt>
          <title>Taisho Tripitaka, Electronic version, No. 0001 長阿含經</title>
          <author>後秦 佛陀耶舍共竺佛念譯</author>
        </titleStmt>
      </fileDesc>
    </teiHeader>
    <text>
    </text>
  </TEI>
</teiCorpus>'''
        expected_output = ''
        self._transform_equality(input_xml, expected_output)

    def test_note(self):
        """Tests that notes, unless inline, are stripped."""
        input_xml = '''
<body xmlns="http://www.tei-c.org/ns/1.0">
  <p>苑。其為典也。淵博弘富。<note n="0001005" resp="Taisho" place="foot text" type="orig">韞＝溫【宋】【元】</note></p>
  <p><note place="inline">釋。秦言能在直樹林。故名釋。釋。秦言亦言直</note></p>
</body>'''
        expected_output = '''
苑。其為典也。淵博弘富。
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        self._transform_equality(input_xml, expected_output)

    def test_title(self):
        """Tests that tei:title is stripped entirely."""
        input_xml = (
            '<body xmlns="http://www.tei-c.org/ns/1.0">'
            '<head>（一一）<title><note n="0057008" resp="#resp4" type="orig" '
            'place="foot text">〔佛說長阿含〕－【三】</note><note n="0057008" '
            'resp="#resp1" type="mod">佛說長阿含【大】，〔－〕【宋】【元】【明】'
            '</note>佛說長阿含</title>第二分增</head></body>')
        expected_output = '（一一）第二分增'
        self._transform_equality(input_xml, expected_output)

    def test_tt(self):
        """Tests that tt is stripped down to the content of
        t[@lang='chi']."""
        input_xml = (
            '<tt xmlns="http://www.cbeta.org/ns/1.0" n="0001011" type="app">'
            '<t resp="Taisho" xml:lang="zh">長阿含經</t><t resp="Taisho" '
            'xml:lang="sa" place="foot">Dīrgha-āgama</t><t resp="Taisho" '
            'xml:lang="pi" place="foot">Dīgha-nikāya</t></tt>')
        expected_output = '長阿含經'
        self._transform_equality(input_xml, expected_output)

    def test_variants(self):
        """Tests that lem/rdg is stripped when it doesn't match the supplied
        witness name."""
        input_xml = '''<body xmlns="http://www.tei-c.org/ns/1.0">
  <p><app n="0083004"><lem>釋。秦言能在直樹林。故名釋。釋。秦言亦言直</lem><rdg resp="Taisho" wit="#wit1 #wit2">在直樹林故名釋懿</rdg><rdg resp="Taisho" wit="#wit3">佛法</rdg></app></p>
</body>'''
        # With the base witness name provided (ie, use the lem).
        expected_output = '''
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        self._transform_equality(input_xml, expected_output,
                                 witness_ref="'{}'".format(
                                     tacl.constants.BASE_WITNESS_ID))
        # With a witness ref provided that occurs in a rdg.
        expected_output = '''
在直樹林故名釋懿'''
        self._transform_equality(input_xml, expected_output,
                                 witness_id="'wit2'")
        # With a witness name provided that occurs in a rdg.
        expected_output = '''
佛法'''
        self._transform_equality(input_xml, expected_output,
                                 witness_id="'wit3'")
        # A particular witness may not be listed either in the lem or
        # a rdg, in which case the lem must be used.
        expected_output = '''
釋。秦言能在直樹林。故名釋。釋。秦言亦言直'''
        self._transform_equality(input_xml, expected_output,
                                 witness_id="'wit4'")

    def _transform_equality(self, input_xml, expected_output, **kwargs):
        actual_output = str(self.stripper.transform(etree.XML(input_xml),
                                                    **kwargs))
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
