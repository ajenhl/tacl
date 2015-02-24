"""Module containing the TEICorpus class."""

from copy import deepcopy
import logging
import os
import re

from lxml import etree


text_name_pattern = re.compile(
    r'^(?P<prefix>[A-Z]{1,2})\d+n(?P<text>[^_\.]+)_(?P<part>\d+)$')

# XSLT to transform a P4 TEI document with a DTD, external entity
# references, and insanely complex gaiji elements into a P4 TEI
# document with no DTD or external references and all gaiji elements
# replaced with the best representation available, encoded in UTF-8.
SIMPLIFY_XSLT = '''
<xsl:stylesheet extension-element-prefixes="fn my str"
                version="1.0"
                xmlns:fn="http://exslt.org/functions"
                xmlns:my="urn:foo"
                xmlns:str="http://exslt.org/strings"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output encoding="UTF-8" method="xml" />

  <xsl:strip-space elements="*" />

  <xsl:template match="gaiji">
    <xsl:choose>
      <xsl:when test="@des">
        <xsl:value-of select="@des" />
      </xsl:when>
      <xsl:when test="@uni">
        <xsl:value-of select="my:decode-codepoint(@uni)" />
      </xsl:when>
      <xsl:when test="@udia">
        <xsl:value-of select="@udia" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>GAIJI WITHOUT REPRESENTATION</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <!-- The following functions are by Aristotle Pagaltzis, from
       http://plasmasturm.org/log/386/ -->
  <fn:function name="my:hex2num">
    <xsl:param name="hexstr" />
    <xsl:variable name="head"
                  select="substring( $hexstr, 1, string-length( $hexstr ) - 1 )"
    />
    <xsl:variable name="nybble"
                  select="substring( $hexstr, string-length( $hexstr ) )" />
    <xsl:choose>
      <xsl:when test="string-length( $hexstr ) = 0">
        <fn:result select="0" />
      </xsl:when>
      <xsl:when test="string( number( $nybble ) ) = 'NaN'">
        <fn:result select="
          my:hex2num( $head ) * 16
          + number( concat( 1, translate( $nybble, 'ABCDEF', '012345' ) ) )
        "/>
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="my:hex2num( $head ) * 16 + number( $nybble )" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:num2hex">
    <xsl:param name="num" />
    <xsl:variable name="nybble" select="$num mod 16" />
    <xsl:variable name="head" select="floor( $num div 16 )" />
    <xsl:variable name="rest">
      <xsl:if test="not( $head = 0 )">
        <xsl:value-of select="my:num2hex( $head )"/>
      </xsl:if>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$nybble > 9">
        <fn:result select="concat(
          $rest,
          translate( substring( $nybble, 2 ), '012345', 'ABCDEF' )
        )"/>
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="concat( $rest, $nybble )" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:char-to-utf8bytes">
    <xsl:param name="codepoint" />
    <xsl:choose>
      <xsl:when test="$codepoint > 65536">
        <fn:result select="
            ( ( floor( $codepoint div 262144 ) mod  8 + 240 ) * 16777216 )
          + ( ( floor( $codepoint div   4096 ) mod 64 + 128 ) *    65536 )
          + ( ( floor( $codepoint div     64 ) mod 64 + 128 ) *      256 )
          + ( ( floor( $codepoint div      1 ) mod 64 + 128 ) *        1 )
        " />
      </xsl:when>
      <xsl:when test="$codepoint > 2048">
        <fn:result select="
            ( ( floor( $codepoint div   4096 ) mod 16 + 224 ) *    65536 )
          + ( ( floor( $codepoint div     64 ) mod 64 + 128 ) *      256 )
          + ( ( floor( $codepoint div      1 ) mod 64 + 128 ) *        1 )
        " />
      </xsl:when>
      <xsl:when test="$codepoint > 128">
        <fn:result select="
            ( ( floor( $codepoint div     64 ) mod 32 + 192 ) *      256 )
          + ( ( floor( $codepoint div      1 ) mod 64 + 128 ) *        1 )
        " />
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="$codepoint" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:percentify">
    <xsl:param name="str" />
    <xsl:choose>
      <xsl:when test="string-length( $str ) > 2">
        <fn:result select="concat(
          '%',
          substring( $str, 1, 2 ),
          my:percentify( substring( $str, 3 ) )
        )" />
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="concat( '%', $str )" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:decode-codepoint">
    <xsl:param name="codepoint" />
    <fn:result
      select="str:decode-uri( my:percentify(
        my:num2hex( my:char-to-utf8bytes(
          my:hex2num( $codepoint )
        ) )
      ) )"
    />
  </fn:function>

</xsl:stylesheet>
'''

TEI_CORPUS_XML = '''<teiCorpus.2></teiCorpus.2>'''


class TEICorpus:

    """A TEICorpus represents a collection of TEI XML documents.

    The CBETA texts are TEI XML that have certain quirks that make
    them difficult to use directly in TACL's stripping process. This
    class provides a tidy method to deal with these quirks; in
    particular it consolidates multiple XML files for a single text
    into one XML file. This is most useful for variant handling, which
    requires that all of the variants used in a given text be known
    before processing the file(s) associated with that text.

    """

    def __init__ (self, input_dir, output_dir):
        self._logger = logging.getLogger(__name__)
        self._input_dir = os.path.abspath(input_dir)
        self._output_dir = os.path.abspath(output_dir)
        self._transform = etree.XSLT(etree.XML(SIMPLIFY_XSLT))
        self._texts = {}

    def _correct_entity_file (self, file_path):
        """Adds an unused entity declaration to the entity file for
        `file_path`, in the hopes that this will make it not cause a
        validation failure."""
        path, basename = os.path.split(file_path)
        entity_file = '{}.ent'.format(os.path.join(
                path, basename.split('_')[0]))
        with open(entity_file, 'rb') as input_file:
            text = input_file.read()
        with open(entity_file, 'wb') as output_file:
            output_file.write(text)
            output_file.write(b'<!ENTITY DUMMY_ENTITY "" >')

    def extract_text_name (self, filename):
        """Returns the name of the text in `filename`.

        Many texts are divided into multiple parts that need to be
        joined together.

        """
        basename = os.path.splitext(os.path.basename(filename))[0]
        match = text_name_pattern.search(basename)
        if match is None:
            self._logger.warning('Found an anomalous filename "{}"'.format(
                filename))
            return None, None
        text_name = '{}{}'.format(match.group('prefix'), match.group('text'))
        return text_name, int(match.group('part'))

    def _output_text (self, text_name, parts):
        """Saves a TEI XML document `text_name` that consists of all of the
        indidivual TEI XML source documents joined."""
        # Add each part in turn to the skeleton TEICorpus document.
        corpus_root = etree.XML(TEI_CORPUS_XML)
        for index, part in enumerate(parts):
            # Add the teiHeader for the first part as the
            # teiHeader of the teiCorpus.
            if index == 0:
                corpus_root.append(deepcopy(part[0]))
            corpus_root.append(part)
        tree = etree.ElementTree(corpus_root)
        output_filename = os.path.join(self._output_dir, text_name)
        tree.write(output_filename, encoding='utf-8', pretty_print=True)

    def tidy (self):
        if not os.path.exists(self._output_dir):
            try:
                os.makedirs(self._output_dir)
            except OSError as err:
                self._logger.error(
                    'Could not create output directory: {}'.format(err))
                raise
        # The CBETA texts are organised into directories, and each
        # text may be in multiple numbered parts. Crucially, these
        # parts may be split over multiple directories. Since it is
        # too memory intensive to store all of the lxml
        # representations of the XML files at once, before joining the
        # parts together, assemble the filenames into groups and then
        # process them one by one.
        for dirpath, dirnames, filenames in os.walk(self._input_dir):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.xml':
                    text_name, part_number = self.extract_text_name(filename)
                    if text_name is None:
                        self._logger.warning('Skipping file "{}"'.format(
                            filename))
                    else:
                        text_name = '{}.xml'.format(text_name)
                        text_parts = self._texts.setdefault(text_name, {})
                        text_parts[part_number] = os.path.join(
                            dirpath, filename)
        for text_name, paths in self._texts.items():
            parts = list(paths.keys())
            parts.sort()
            xml_parts = []
            for part in parts:
                xml_parts.append(self._tidy(text_name, paths[part]))
            self._output_text(text_name, xml_parts)

    def _tidy (self, text_name, file_path, tried=False):
        """Transforms the file at `file_path` into simpler XML and returns
        it."""
        output_file = os.path.join(self._output_dir, text_name)
        self._logger.info('Tidying file {} into {}'.format(
            file_path, output_file))
        try:
            tei_doc = etree.parse(file_path)
        except etree.XMLSyntaxError as err:
            self._logger.warning('XML file "{}" is invalid'.format(file_path))
            if tried:
                self._logger.error(
                    'XML file "{}" is irretrievably invalid: {}'.format(
                        file_path, err))
                raise
            self._logger.warning('Retrying after modifying entity file')
            self._correct_entity_file(file_path)
            xml = self._tidy(text_name, file_path, True)
        else:
            xml = self._transform(tei_doc).getroot()
        return xml
