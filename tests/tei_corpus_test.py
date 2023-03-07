#!/usr/bin/env python3

import unittest

from lxml import etree

import tacl


class TEICorpusCBETAGitHubTestCase (unittest.TestCase):

    def setUp(self):
        self.corpus = tacl.TEICorpusCBETAGitHub('/', '/')

    def test_get_witnesses(self):
        """Tests that all of the witnesses of variant readings are extracted
        from a text."""
        input_xml = '''
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <encodingDesc>
      <tagsDecl>
        <namespace name="http://www.tei-c.org/ns/1.0">
          <tagUsage gi="rdg">
            <listWit>
              <witness xml:id="wit1">【宋】</witness>
              <witness xml:id="wit2">【大】</witness>
              <witness xml:id="wit3">【明】</witness>
              <witness xml:id="wit4">【三】</witness>
              <witness xml:id="wit5">【元】</witness>
            </listWit>
          </tagUsage>
        </namespace>
      </tagsDecl>
    </encodingDesc>
  </teiHeader>
</TEI>'''
        expected_witnesses = ['三', '元', '大', '宋', '明']
        actual_witnesses = self.corpus.get_witnesses(etree.XML(input_xml))[0]
        self.assertEqual(expected_witnesses, actual_witnesses)

    def test_get_resps(self):
        """Tests that all resps are extracted from a text."""
        input_xml = '''
<div xmlns="http://www.tei-c.org/ns/1.0" xmlns:cb="http://www.cbeta.org/ns/1.0">
  <note n="0001001" resp="{corrections|CBETA.say}{corrections|Taisho}">此序</note>
  <app><lem>長安</lem><rdg resp="{corrections|CBETA}">辯</rdg></app>
  <cb:tt type="app">
    <cb:t resp="{corrections|CBETA}" xml:lang="zh">長阿含經</cb:t>
    <cb:t resp="{other|CBETA}" xml:lang="sa">Dīrgha-āgama</cb:t>
  </cb:tt>
</div>
        '''
        expected_resps = [
            ('corrections', 'CBETA'), ('corrections', 'CBETA.say'),
            ('corrections', 'Taisho'), ('other', 'CBETA')]
        actual_resps = self.corpus.get_resps(etree.XML(input_xml))[0]
        self.assertEqual(expected_resps, actual_resps)

    def test_glyph(self):
        """Tests that the correct alternative for characters not in Unicode is
        used."""
        base_xml = '''\
        <TEI xmlns="http://www.tei-c.org/ns/1.0"
             xmlns:cb="http://www.cbeta.org/ns/1.0">
        <charDecl><char xml:id="CB00178">
        <charName>CBETA CHARACTER CB00178</charName>
        {}
        <mapping cb:dec="983218" type="PUA">U+F00B2</mapping>
        </char></charDecl>
        <p><g ref="#CB00178">㮈</g></p>
        </TEI>'''
        data = [
            ('<mapping type="unicode">U+3B88</mapping>', '㮈'),
            ('<mapping type="normal_unicode">U+3B88</mapping>', '㮈'),
            ('<charProp><localName>composition</localName><value>[木*奈]</value></charProp>',
             '[木*奈]'),
            ('<charProp><localName>Romanized form in CBETA transcription</localName><value>o.m</value></charProp><charProp><localName>Character in the Siddham font</localName><value>湡</value></charProp><charProp><localName>Romanized form in Unicode transcription</localName><value>oṃ</value></charProp>',
             'oṃ'),
            ('<charProp><localName>composition</localName><value>[木*奈]</value></charProp><charProp><localName>Romanized form in CBETA transcription</localName><value>o.m</value></charProp><charProp><localName>Character in the Siddham font</localName><value>湡</value></charProp><charProp><localName>Romanized form in Unicode transcription</localName><value>oṃ</value></charProp>',
             '[木*奈]'),
            ('<charProp><localName>Character in the Siddham font</localName><value>揨</value></charProp>',
             '揨'),
        ]
        for char_detail, expected_output in data:
            output_tree = self.corpus.transform(etree.XML(base_xml.format(
                char_detail)))
            actual_output = etree.tostring(output_tree.getroot(),
                                           method='text', encoding='unicode')
            self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
