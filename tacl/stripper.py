"""Module containing the Stripper class."""

import logging
import os
import re

from lxml import etree


BASE_WITNESS = 'base'
witnesses_splitter = re.compile(r'【|】')

STRIP_XSLT = '''
<xsl:stylesheet extension-element-prefixes="fn my str"
                version="1.0"
                xmlns:fn="http://exslt.org/functions"
                xmlns:my="urn:foo"
                xmlns:str="http://exslt.org/strings"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output encoding="UTF-8" method="text" />
  <xsl:strip-space elements="*" />

  <!-- For the edited/master text, pass BASE_WITNESS. -->
  <xsl:param name="witness" />
  <xsl:variable name="full_witness" select="concat('【', $witness, '】')" />

  <xsl:template match="div1|div2|lg|list|p">
    <xsl:call-template name="add_blank_line" />
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="foreign[@place='foot']" />

  <xsl:template match="head[@type='no']" />

  <xsl:template match="item">
    <xsl:text>   </xsl:text>
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="l">
    <xsl:text>   </xsl:text>
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="lb[not(local-name(following-sibling::node()[1])='lb')]">
    <xsl:call-template name="add_blank_line" />
  </xsl:template>

  <xsl:template match="lem">
    <xsl:if test="$witness = '{base}' or contains(@wit, $full_witness) or
                  not(../rdg[contains(@wit, $full_witness)])">
      <xsl:apply-templates />
    </xsl:if>
  </xsl:template>

  <xsl:template match="note" />

  <xsl:template match="note[@place = 'inline']">
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="rdg">
    <xsl:if test="contains(@wit, $full_witness)">
      <xsl:apply-templates />
    </xsl:if>
  </xsl:template>

  <xsl:template match="teiHeader" />

  <xsl:template match="text()">
    <xsl:value-of select="normalize-space()" />
  </xsl:template>

  <xsl:template match="t[not(@lang='chi')]" />

  <xsl:template name="add_blank_line">
    <xsl:text>
</xsl:text>
  </xsl:template>
</xsl:stylesheet>'''.format(base=BASE_WITNESS)


class Stripper:

    """Class used for preprocessing a corpus of texts by stripping out
    all material that is not the textual material proper.

    The intention is to keep the stripped text as close in formatting
    to the original as possible, including whitespace."""

    def __init__ (self, input_dir, output_dir):
        self._logger = logging.getLogger(__name__)
        self._input_dir = os.path.abspath(input_dir)
        self._output_dir = os.path.abspath(output_dir)
        self._transform = etree.XSLT(etree.XML(STRIP_XSLT))
        self._texts = {}

    def get_witnesses (self, source_tree):
        """Returns a list of all witnesses of variant readings in
        `source_tree`.

        :param source_tree: XML tree of source document
        :type source_tree: `etree._ElementTree`
        :rtype: `set`

        """
        witnesses = set([BASE_WITNESS])
        witness_values = source_tree.xpath('//app/rdg[@wit]/@wit')
        for witness_value in witness_values:
            for witness in witnesses_splitter.split(witness_value):
                if witness:
                    witnesses.add(witness)
        return witnesses

    def _output_file (self, text_name, witnesses):
        text_dir = os.path.join(self._output_dir, text_name)
        try:
            os.makedirs(text_dir)
        except OSError as err:
            logging.error('Could not create output directory: {}'.format(
                err))
            raise
        for witness in witnesses.keys():
            witness_file_path = os.path.join(
                text_dir, '{}.txt'.format(witness))
            with open(witness_file_path, 'wb') as output_file:
                output_file.write(witnesses[witness].encode('utf-8'))

    def strip_files (self):
        if not os.path.exists(self._output_dir):
            try:
                os.makedirs(self._output_dir)
            except OSError as err:
                self._logger.error(
                    'Could not create output directory: {}'.format(err))
                raise
        for dirpath, dirnames, filenames in os.walk(self._input_dir):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.xml':
                    text_name, witnesses = self.strip_file(
                        os.path.join(dirpath, filename))
                    self._output_file(text_name, witnesses)

    def strip_file (self, filename):
        file_path = os.path.join(self._input_dir, filename)
        text_name = os.path.splitext(os.path.basename(filename))[0]
        stripped_file_path = os.path.join(self._output_dir, text_name)
        self._logger.info('Stripping file {} into {}'.format(
                file_path, stripped_file_path))
        try:
            tei_doc = etree.parse(file_path)
        except etree.XMLSyntaxError:
            logging.warning('XML file "{}" is invalid'.format(filename))
            return
        text_witnesses = self._texts.setdefault(stripped_file_path, {})
        for witness in self.get_witnesses(tei_doc):
            witness_param = "'{}'".format(witness)
            text = str(self._transform(tei_doc, witness=witness_param))
            text_witnesses[witness] = text
        return text_name, text_witnesses
