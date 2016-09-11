"""Module containing the TEICorpus class."""

import logging
import os
import re

from lxml import etree
from pkg_resources import resource_filename

from . import constants


TEI_CORPUS_XML = '''<teiCorpus xmlns="http://www.tei-c.org/ns/1.0" xmlns:cb="http://www.cbeta.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title></title>
        <author></author>
      </titleStmt>
      <publicationStmt>
        <p>Compiled from source TEI document(s) published by CBETA.</p>
      </publicationStmt>
      <sourceDesc>
        <bibl>CBETA TEI document(s).</bibl>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
</teiCorpus>'''
TEI = '{{{}}}'.format(constants.NAMESPACES['tei'])
resp_splitter = re.compile(r'\{|\}')
witnesses_splitter = re.compile(r'【|】')


class TEICorpus:

    """A TEICorpus represents a collection of TEI XML documents.

    The CBETA texts are TEI XML that have certain quirks that make
    them difficult to use directly in TACL's stripping process. This
    class provides a tidy method to deal with these quirks; in
    particular it consolidates multiple XML files for a single text
    into one XML file.

    This class must not be instantiated directly; rather a subclass
    appropriate to the source texts should be used.

    """

    xslt = ''

    def __init__(self, input_dir, output_dir):
        self._logger = logging.getLogger(__name__)
        self._input_dir = os.path.abspath(input_dir)
        self._output_dir = os.path.abspath(output_dir)
        xslt_filename = resource_filename(__name__, 'assets/xslt/{}'.format(
            self.xslt))
        self.transform = etree.XSLT(etree.parse(xslt_filename))

    def _assemble_parts(self, text_name, paths):
        parts = list(paths.keys())
        parts.sort()
        # If the whitespace between tags in the supplied document is
        # not removed, pretty-printing will fail to handle the added
        # documents nicely.
        parser = etree.XMLParser(remove_blank_text=True)
        corpus_root = etree.XML(TEI_CORPUS_XML, parser)
        for index, part in enumerate(parts):
            # Convert each part into the standard format.
            xml_part = self._tidy(text_name, paths[part])
            # Add each part in turn to the skeleton TEICorpus document.
            corpus_root.append(xml_part)
        return corpus_root

    def _assemble_part_list(self):
        # The CBETA texts are organised into directories, and each
        # text may be in multiple numbered parts. Crucially, these
        # parts may be split over multiple directories. Since it is
        # too memory intensive to store all of the lxml
        # representations of the XML files at once, before joining the
        # parts together, assemble the filenames into groups and then
        # process them one by one.
        texts = {}
        for dirpath, dirnames, filenames in os.walk(self._input_dir):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.xml':
                    text_name, part_label = self._extract_text_name(filename)
                    if text_name is None:
                        self._logger.warning('Skipping file "{}"'.format(
                            filename))
                    else:
                        text_name = '{}.xml'.format(text_name)
                        text_parts = texts.setdefault(text_name, {})
                        text_parts[part_label] = os.path.join(
                            dirpath, filename)
        return texts

    def _extract_text_name(self, filename):
        raise NotImplementedError

    def get_witnesses(self, source_tree):
        """Returns a sorted list of all witnesses of variant readings in
        `source_tree`, and the elements that bear @wit attributes.

        :param source_tree: XML tree of source document
        :type source_tree: `etree._ElementTree`
        :rtype: `tuple` of `list`s

        """
        witnesses = set()
        # Only get witnesses from tei:rdg, not tei:lem also, because a
        # witness may only be the source for the base reading, in
        # which case it is pointless to create a separate text for it
        # - everything will be encompassed in the artificial base
        # witness.
        bearers = source_tree.xpath('//tei:app/tei:rdg[@wit]',
                                    namespaces=constants.NAMESPACES)
        for bearer in bearers:
            for witness in witnesses_splitter.split(bearer.get('wit')):
                if witness:
                    witnesses.add(witness)
        return sorted(witnesses), bearers

    def _handle_resps(self, root):
        raise NotImplementedError

    def _handle_witnesses(self, root):
        """Returns `root` with a witness list added to the TEI header and @wit
        values changed to references."""
        witnesses, bearers = self.get_witnesses(root)
        if not witnesses:
            return root
        source_desc = root.xpath(
            '/tei:teiCorpus/tei:teiHeader/tei:fileDesc/tei:sourceDesc',
            namespaces=constants.NAMESPACES)[0]
        wit_list = etree.SubElement(source_desc, TEI + 'listWit')
        for index, siglum in enumerate(witnesses):
            wit = etree.SubElement(wit_list, TEI + 'witness')
            xml_id = 'wit{}'.format(index+1)
            wit.set(constants.XML + 'id', xml_id)
            wit.text = siglum
            full_siglum = '【{}】'.format(siglum)
            self._update_refs(root, bearers, 'wit', full_siglum, xml_id)
        return root

    def _output_text(self, text_name, root):
        """Saves the TEI XML document `root` at the path `text_name`."""
        output_filename = os.path.join(self._output_dir, text_name)
        tree = etree.ElementTree(root)
        tree.write(output_filename, encoding='utf-8', pretty_print=True)

    def _populate_header(self, root):
        """Populate the teiHeader of the teiCorpus with useful information
        from the teiHeader of the first TEI part."""
        # If this gets more complicated, it should be handled via an XSLT.
        title_stmt = root.xpath(
            'tei:teiHeader/tei:fileDesc/tei:titleStmt',
            namespaces=constants.NAMESPACES)[0]
        # There is no guarantee that a title or author is specified,
        # in which case do nothing.
        try:
            title_stmt[0].text = root.xpath(
                'tei:TEI[1]/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title',
                namespaces=constants.NAMESPACES)[0].text
        except IndexError:
            pass
        try:
            title_stmt[1].text = root.xpath(
                'tei:TEI[1]/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author',
                namespaces=constants.NAMESPACES)[0].text
        except IndexError:
            pass
        return root

    def tidy(self):
        if not os.path.exists(self._output_dir):
            try:
                os.makedirs(self._output_dir)
            except OSError as err:
                self._logger.error(
                    'Could not create output directory: {}'.format(err))
                raise
        texts = self._assemble_part_list()
        for text_name, paths in texts.items():
            root = self._assemble_parts(text_name, paths)
            root = self._populate_header(root)
            root = self._handle_resps(root)
            root = self._handle_witnesses(root)
            self._output_text(text_name, root)

    def _tidy(self, *args, **kwargs):
        raise NotImplementedError

    def _update_refs(self, root, bearers, attribute, ref_text, xml_id):
        """Change `ref_text` on `bearers` to xml:id references.

        :param root: root of TEI document
        :type root: `etree._Element`
        :param bearers: elements bearing `attribute`
        :param attribute: attribute to update
        :type attribute: `str`
        :param ref_text: text to replace
        :type ref_text: `str`
        :param xml_id: xml:id
        :type xml_id: `str`

        """
        ref = ' #{} '.format(xml_id)
        for bearer in bearers:
            attribute_text = bearer.get(attribute).replace(ref_text, ref)
            refs = ' '.join(sorted(attribute_text.strip().split()))
            bearer.set(attribute, refs)


class TEICorpusCBETA2011 (TEICorpus):

    """A TEICorpus subclass where the source files are formatted as per
    the CBETA 2011 DVD release (TEI P4)."""

    text_name_pattern = re.compile(
        r'^(?P<prefix>[A-Z]{1,2})\d+n(?P<text>[^_\.]+)_(?P<part>\d+)$')
    xslt = 'prepare_tei_cbeta_2011.xsl'

    @staticmethod
    def _correct_entity_file(file_path):
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

    def _extract_text_name(self, filename):
        """Returns the name of the text in `filename`.

        Many texts are divided into multiple parts that need to be
        joined together.

        """
        basename = os.path.splitext(os.path.basename(filename))[0]
        match = self.text_name_pattern.search(basename)
        if match is None:
            self._logger.warning('Found an anomalous filename "{}"'.format(
                filename))
            return None, None
        text_name = '{}{}'.format(match.group('prefix'), match.group('text'))
        return text_name, int(match.group('part'))

    def _handle_resps(self, root):
        # Resp information is not extracted for 2011 CBETA files.
        return root

    def _tidy(self, text_name, file_path, tried=False):
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
            xml = self.transform(tei_doc).getroot()
        return xml


class TEICorpusCBETAGitHub (TEICorpus):

    """A TEICorpus subclass where the source files are formatted as per
    the CBETA GitHub repository at
    https://github.com/cbeta-org/xml-p5.git (TEI P5)"""

    text_name_pattern = re.compile(
        r'^(?P<prefix>[A-Z]{1,2})\d+n(?P<text>[A-Z]?\d+)(?P<part>[A-Za-z]?)$')
    xslt = 'prepare_tei_cbeta_github.xsl'

    def _extract_text_name(self, filename):
        """Returns the name of the text in `filename`.

        Some texts are divided into multiple parts that need to be
        joined together.

        :param filename: filename of TEI
        :type filename: `str`
        :rtype: `tuple` of `str`

        """
        basename = os.path.splitext(os.path.basename(filename))[0]
        match = self.text_name_pattern.search(basename)
        if match is None:
            self._logger.warning('Found an anomalous filename "{}"'.format(
                filename))
            return None, None
        text_name = '{}{}'.format(match.group('prefix'), match.group('text'))
        return text_name, match.group('part')

    def get_resps(self, source_tree):
        """Returns a sorted list of all resps in `source_tree`, and the
        elements that bear @resp attributes.

        :param source_tree: XML tree of source document
        :type source_tree: `etree._ElementTree`
        :rtype: `tuple` of `lists`

        """
        resps = set()
        bearers = source_tree.xpath('//*[@resp]',
                                    namespaces=constants.NAMESPACES)
        for bearer in bearers:
            for resp in resp_splitter.split(bearer.get('resp')):
                if resp:
                    resps.add(tuple(resp.split('|', maxsplit=1)))
        return sorted(resps), bearers

    def _handle_resps(self, root):
        """Returns `root` with a resp list added to the TEI header and @resp
        values changed to references."""
        resps, bearers = self.get_resps(root)
        if not resps:
            return root
        file_desc = root.xpath(
            '/tei:teiCorpus/tei:teiHeader/tei:fileDesc',
            namespaces=constants.NAMESPACES)[0]
        edition_stmt = etree.Element(TEI + 'editionStmt')
        file_desc.insert(1, edition_stmt)
        for index, (resp_resp, resp_name) in enumerate(resps):
            resp_stmt = etree.SubElement(edition_stmt, TEI + 'respStmt')
            xml_id = 'resp{}'.format(index+1)
            resp_stmt.set(constants.XML + 'id', xml_id)
            resp = etree.SubElement(resp_stmt, TEI + 'resp')
            resp.text = resp_resp
            name = etree.SubElement(resp_stmt, TEI + 'name')
            name.text = resp_name
            resp_data = '{{{}|{}}}'.format(resp_resp, resp_name)
            self._update_refs(root, bearers, 'resp', resp_data, xml_id)
        return root

    def _tidy(self, text_name, file_path):
        """Transforms the file at `file_path` into simpler XML and returns
        that.

        """
        output_file = os.path.join(self._output_dir, text_name)
        self._logger.info('Tidying file {} into {}'.format(
            file_path, output_file))
        try:
            tei_doc = etree.parse(file_path)
        except etree.XMLSyntaxError as err:
            self._logger.error('XML file "{}" is invalid: {}'.format(
                file_path, err))
            raise
        return self.transform(tei_doc).getroot()
