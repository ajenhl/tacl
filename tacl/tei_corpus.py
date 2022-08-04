"""Module containing the TEICorpus class."""

import logging
import os
import re

from lxml import etree
from pkg_resources import resource_filename

from . import constants
from .exceptions import TACLError


LEAVE_UNNAMED_DIVS = 'leave'
MERGE_UNNAMED_DIVS_TO_PRECEDING = 'merge_to_preceding'
REMOVE_UNNAMED_DIVS = 'delete'
TEI_CORPUS_XML = '''<teiCorpus xmlns="http://www.tei-c.org/ns/1.0" xmlns:cb="http://www.cbeta.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title/>
        <author/>
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
ns = etree.FunctionNamespace(constants.NAMESPACES['tacl'])


@ns
def char_from_codepoint(context, codepoint):
    """XPath Extension function to return a Unicode character from a
    Unicode codepoint.

    The codepoint is provided as a string starting with U+ and
    followed by a hexadecimal number.

    """
    return chr(int(codepoint[2:], base=16))


class TEICorpus:

    """A TEICorpus represents a collection of TEI XML documents.

    The CBETA works are TEI XML that have certain quirks that make
    them difficult to use directly in TACL's stripping process. This
    class provides a tidy method to deal with these quirks; in
    particular it consolidates multiple XML files for a single work
    into one XML file.

    This class must not be instantiated directly; rather a subclass
    appropriate to the source should be used.

    """

    xslt = ''

    def __init__(self, input_dir, output_dir):
        self._logger = logging.getLogger(__name__)
        self._input_dir = os.path.abspath(input_dir)
        self._output_dir = os.path.abspath(output_dir)
        xslt_filename = resource_filename(__name__, 'assets/xslt/{}'.format(
            self.xslt))
        self.transform = etree.XSLT(etree.parse(xslt_filename))

    def _assemble_parts(self, work, paths):
        parts = list(paths.keys())
        parts.sort()
        # If the whitespace between tags in the supplied document is
        # not removed, pretty-printing will fail to handle the added
        # documents nicely.
        parser = etree.XMLParser(remove_blank_text=True)
        corpus_root = etree.XML(TEI_CORPUS_XML, parser)
        for index, part in enumerate(parts):
            # Convert each part into the standard format.
            xml_part = self._tidy(work, paths[part])
            # Add each part in turn to the skeleton TEICorpus document.
            corpus_root.append(xml_part)
        return corpus_root

    def _assemble_part_list(self):
        # The CBETA files are organised into directories, and each
        # work may be in multiple numbered parts. Crucially, these
        # parts may be split over multiple directories. Since it is
        # too memory intensive to store all of the lxml
        # representations of the XML files at once, before joining the
        # parts together, assemble the filenames into groups and then
        # process them one by one.
        self._logger.debug('Assembling all parts into coherent works.')
        works = {}
        for dirpath, dirnames, filenames in os.walk(self._input_dir):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.xml':
                    work, part_label = self._extract_work(filename)
                    if work is None:
                        self._logger.warning('Skipping file "{}"'.format(
                            filename))
                    else:
                        work = '{}.xml'.format(work)
                        work_parts = works.setdefault(work, {})
                        work_parts[part_label] = os.path.join(
                            dirpath, filename)
        self._logger.debug('Finished assembling parts.')
        return works

    def _extract_work(self, filename):
        raise NotImplementedError

    def get_witnesses(self, source_tree):
        """Returns a sorted list of all witnesses of readings in
        `source_tree`, and the elements that bear @wit attributes.

        :param source_tree: XML tree of source document
        :type source_tree: `etree._ElementTree`
        :rtype: `tuple` of `list`s

        """
        witnesses = set()
        bearers = source_tree.xpath('//tei:app/tei:*[@wit]',
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
            xml_id = 'wit{}'.format(index + 1)
            wit.set(constants.XML + 'id', xml_id)
            wit.text = siglum
            full_siglum = '【{}】'.format(siglum)
            self._update_refs(root, bearers, 'wit', full_siglum, xml_id)
        return root

    def _output_tree(self, filename, tree, seen_filenames=None):
        """Saves the TEI XML document `tree` as `filename` in the output
        directory."""
        if seen_filenames is None:
            seen_filenames = {}
        # Remove characters that Windows cannot handle in filenames,
        # some of which may appear in CBETA's composition forms for
        # characters not yet in Unicode. Further remove characters
        # that will be interpreted as regular expression characters,
        # which causes problems when used in
        # tacl.Corpus.get_witnesses().
        filename = filename.translate(str.maketrans('', '', '[]\\/<>?*+":|'))
        output_path = os.path.join(self._output_dir, filename)
        if output_path in seen_filenames:
            root, ext = os.path.splitext(output_path)
            if seen_filenames[output_path] == 1:
                os.rename(output_path, '{}-{}{}'.format(
                    root, str(seen_filenames[output_path]), ext))
            seen_filenames[output_path] += 1
            output_path = '{}-{}{}'.format(
                root, str(seen_filenames[output_path]), ext)
        else:
            seen_filenames[output_path] = 1
        if os.path.exists(output_path):
            raise TACLError('Already created output file at {}.'.format(
                output_path))
        self._logger.debug('Serialising XML tree to output file at {}.'.format(
            output_path))
        tree.write(output_path, encoding='utf-8', pretty_print=True)
        return seen_filenames

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
                'tei:TEI[1]/tei:teiHeader/tei:fileDesc/tei:titleStmt/'
                'tei:title', namespaces=constants.NAMESPACES)[0].text
        except IndexError:
            pass
        try:
            title_stmt[1].text = root.xpath(
                'tei:TEI[1]/tei:teiHeader/tei:fileDesc/tei:titleStmt/'
                'tei:author', namespaces=constants.NAMESPACES)[0].text
        except IndexError:
            pass
        return root

    def _postprocess(self, work, tree):
        """Post-process the XML document `tree`."""
        pp_func = '_postprocess_{}'.format(work)
        if hasattr(self, pp_func):
            getattr(self, pp_func)(work, tree)
        else:
            self._output_tree('{}.xml'.format(work), tree)

    def tidy(self):
        if not os.path.exists(self._output_dir):
            try:
                os.makedirs(self._output_dir)
            except OSError as err:
                self._logger.error(
                    'Could not create output directory: {}'.format(err))
                raise
        works = self._assemble_part_list()
        for work_filename, paths in sorted(works.items()):
            self._logger.debug('Tidying {}'.format(work_filename))
            work = os.path.splitext(work_filename)[0]
            root = self._assemble_parts(work_filename, paths)
            root = self._populate_header(root)
            root = self._handle_resps(root)
            root = self._handle_witnesses(root)
            tree = etree.ElementTree(root)
            self._output_tree('{}-original.xml'.format(work), tree)
            self._postprocess(work, tree)

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


class TEICorpusCBETAGitHub (TEICorpus):

    """A TEICorpus subclass where the source files are formatted as per
    the CBETA GitHub repository at
    https://github.com/cbeta-org/xml-p5.git (TEI P5)"""

    work_pattern = re.compile(
        r'^(?P<prefix>[A-Z]{1,2})\d+n(?P<number>[A-Z]?\d+)(?P<part>[A-Za-z]?)$')
    xslt = 'prepare_tei_cbeta_github.xsl'

    def __init__(self, *args):
        super().__init__(*args)
        div_xslt = resource_filename(
            __name__, 'assets/xslt/CBETA_extract_div.xsl')
        self._transform_div = etree.XSLT(etree.parse(div_xslt))
        remove_divs_xslt = resource_filename(
            __name__, 'assets/xslt/CBETA_remove_divs.xsl')
        self._remove_divs = etree.XSLT(etree.parse(remove_divs_xslt))

    def _extract_divs(self, work, tree, div_types, exclude=None):
        """Writes out to files the individual parts of a work corresponding to
        various types of cb:div.

        After a div type has been extracted, it must be removed from
        the tree so that future extractions/manipulations do not
        include that material.

        """
        for div_type, label in div_types:
            divs = tree.xpath('//cb:div[@type="{}"]'.format(div_type),
                              namespaces=constants.NAMESPACES)
            for position, div in enumerate(divs):
                subtree = self._transform_div(tree, position=str(position),
                                              div_type='"{}"'.format(div_type))
                subtree = self._remove_subdivs(subtree, exclude)
                try:
                    title = '-' + self._get_mulu(
                        subtree.getroot(),
                        '//tei:body/cb:div/cb:mulu[1]/text()')
                except IndexError:
                    title = ''
                filename = '{}-{}-{}{}.xml'.format(work, label, position + 1,
                                                   title)
                self._output_tree(filename, subtree)
            tree = self._remove_divs(tree, div_type='"{}"'.format(div_type))
        return tree

    def _extract_work(self, filename):
        """Returns the name of the work in `filename`.

        Some works are divided into multiple parts that need to be
        joined together.

        :param filename: filename of TEI
        :type filename: `str`
        :rtype: `tuple` of `str`

        """
        basename = os.path.splitext(os.path.basename(filename))[0]
        match = self.work_pattern.search(basename)
        if match is None:
            self._logger.warning('Found an anomalous filename "{}"'.format(
                filename))
            return None, None
        work = '{}{}'.format(match.group('prefix'), match.group('number'))
        if work == 'T0220':
            part = match.group('part')
        else:
            work = '{}{}'.format(work, match.group('part'))
            part = None
        return work, part

    def _get_mulu(self, element, xpath):
        mulu = element.xpath(xpath, namespaces=constants.NAMESPACES)[0]
        mulu = mulu.replace(' ', '-')
        mulu = mulu.replace(os.path.sep, '|')
        return mulu

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
            xml_id = 'resp{}'.format(index + 1)
            resp_stmt.set(constants.XML + 'id', xml_id)
            resp = etree.SubElement(resp_stmt, TEI + 'resp')
            resp.text = resp_resp
            name = etree.SubElement(resp_stmt, TEI + 'name')
            name.text = resp_name
            resp_data = '{{{}|{}}}'.format(resp_resp, resp_name)
            self._update_refs(root, bearers, 'resp', resp_data, xml_id)
        return root

    def _postprocess(self, work, tree):
        """Post-process the XML document `root`."""
        div_types = [('xu', 'xu'), ('w', 'endmatter')]
        tree = self._extract_divs(work, tree, div_types)
        super()._postprocess(work, tree)

    def _postprocess_div_mulu(self, work, tree, div_type,
                              treatment=LEAVE_UNNAMED_DIVS, exclude=None):
        divs = tree.xpath('//cb:div[@type="{}"]'.format(div_type),
                          namespaces=constants.NAMESPACES)
        seen_filenames = {}
        for position, div in enumerate(divs):
            div_tree = self._transform_div(tree, position=str(position),
                                           div_type='"{}"'.format(div_type),
                                           treatment='"{}"'.format(treatment))
            div_tree = self._remove_subdivs(div_tree, exclude)
            try:
                title = self._get_mulu(div, 'cb:mulu[1]/text()')
            except IndexError:
                if treatment in (MERGE_UNNAMED_DIVS_TO_PRECEDING,
                                 REMOVE_UNNAMED_DIVS):
                    continue
                title = 'unnamed-{}'.format(position + 1)
            div_filename = '{}-{}.xml'.format(work, title)
            seen_filenames = self._output_tree(div_filename, div_tree,
                                               seen_filenames)

    def _postprocess_T0001(self, work, tree):
        """Post-process the XML document T0001.xml.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'jing')

    def _postprocess_T0026(self, work, tree):
        """Post-process the XML document T0026.xml.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'jing')

    def _postprocess_T0101(self, work, tree):
        """Post-process the XML document T0101.xml.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'jing')

    def _postprocess_T0125(self, work, tree):
        """Post-process the XML document T0125.xml.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu content for that div and the
        cb:mulu of its containing cb:div[@type='pin']. Where a
        cb:div[@type='pin'] does not have any subdivisions, that div
        will be its own file.

        """
        pin_divs = tree.xpath('//cb:div[@type="pin"]',
                              namespaces=constants.NAMESPACES)
        seen_filenames = {}
        for position, div in enumerate(pin_divs):
            if div.xpath('cb:div[@type="jing"]',
                         namespaces=constants.NAMESPACES):
                continue
            div_tree = self._transform_div(tree, position=str(position),
                                           div_type='"pin"')
            mulu = self._get_mulu(div, 'cb:mulu[1]/text()')
            div_filename = '{}-{}.xml'.format(work, mulu)
            seen_filenames = self._output_tree(div_filename, div_tree,
                                               seen_filenames)
        jing_divs = tree.xpath('//cb:div[@type="jing"]',
                               namespaces=constants.NAMESPACES)
        for position, div in enumerate(jing_divs):
            div_tree = self._transform_div(tree, position=str(position),
                                           div_type='"jing"')
            pin_mulu = self._get_mulu(div, '../cb:mulu[1]/text()')
            jing_mulu = self._get_mulu(div, 'cb:mulu[1]/text()')
            div_filename = '{}-{}-{}.xml'.format(work, pin_mulu, jing_mulu)
            self._output_tree(div_filename, div_tree)

    def _postprocess_T0150A(self, work, tree):
        """Post-process the XML document T0150A.xml.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'jing')

    def _postprocess_T0152(self, work, tree):
        """Post-process the XML document T0152.xml.

        Extract the first (should be only) cb:div[@type='other'] into
        its own file.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu content for that div.

        """
        div_tree = self._transform_div(tree, position='0', div_type='"other"')
        div_tree = self._remove_subdivs(div_tree, ['jing'])
        div_filename = '{}-0.xml'.format(work)
        self._output_tree(div_filename, div_tree)
        self._postprocess_div_mulu(work, tree, 'jing')

    def _postprocess_T0154(self, work, tree):
        """Post-process the XML document T0154.xml.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu number and the head.

        """
        divs = tree.xpath('//cb:div[@type="jing"]',
                          namespaces=constants.NAMESPACES)
        seen_filenames = {}
        for position, div in enumerate(divs):
            div_tree = self._transform_div(tree, position=str(position),
                                           div_type='"jing"')
            number = div.xpath('cb:mulu[1]/@n',
                               namespaces=constants.NAMESPACES)[0]
            title = ''.join(div.xpath(
                'tei:head[1]/text() | tei:head[1]/tei:app/tei:lem/text()',
                namespaces=constants.NAMESPACES))
            div_filename = '{}-{}-{}.xml'.format(work, number, title)
            seen_filenames = self._output_tree(div_filename, div_tree,
                                               seen_filenames)

    def _postprocess_T0186(self, work, tree):
        """Post-process the XML document T0186.xml.

        Divide into two files, one containing all of the tei:l
        material, and one the rest.

        """
        xslt_filename = resource_filename(
            __name__, 'assets/xslt/CBETA_extract_verse.xsl')
        extract_verse = etree.XSLT(etree.parse(xslt_filename))
        verse_tree = extract_verse(tree)
        verse_filename = '{}-verses.xml'.format(work)
        self._output_tree(verse_filename, verse_tree)
        prose_tree = extract_verse(tree, inverse='1')
        prose_filename = '{}-ex-verses.xml'.format(work)
        self._output_tree(prose_filename, prose_tree)

    def _postprocess_T0220(self, work, tree):
        """Post-process the XML document T0220.xml.

        Divide into multiple files, one for each cb:div[@type='hui'],
        named according to its position. This is complicated by the
        fact that one of the parts (T0220b) is meant to be entirely
        within the single hui of T0220a but does not have any
        containing div.

        """
        xslt_filename = resource_filename(
            __name__, 'assets/xslt/CBETA_T0220_reparent_divs.xsl')
        move_non_hui_divs = etree.XSLT(etree.parse(xslt_filename))
        tree = move_non_hui_divs(tree)
        divs = tree.xpath('//cb:div[@type="hui"]',
                          namespaces=constants.NAMESPACES)
        for position, div in enumerate(divs):
            div_tree = self._transform_div(tree, position=str(position),
                                           div_type='"hui"')
            div_filename = '{}-{}.xml'.format(work, position + 1)
            self._output_tree(div_filename, div_tree)

    def _postprocess_T0225(self, work, tree):
        """Post-process the XML document T0225.xml.

        Divide into two files, one containing all of the
        tei:note[@place='inline'] material, and one the rest.

        """
        xslt_filename = resource_filename(
            __name__, 'assets/xslt/CBETA_extract_commentary.xsl')
        extract_commentary = etree.XSLT(etree.parse(xslt_filename))
        commentary_tree = extract_commentary(tree)
        commentary_filename = '{}-commentary.xml'.format(work)
        self._output_tree(commentary_filename, commentary_tree)
        ex_commentary_tree = extract_commentary(tree, inverse='1')
        ex_commentary_filename = '{}-ex-commentary.xml'.format(work)
        self._output_tree(ex_commentary_filename, ex_commentary_tree)

    def _postprocess_T0310(self, work, tree):
        """Post-process the XML document T0310.xml.

        Divide into multiple files, one for each cb:div[@type='hui'],
        named according to the cb:mulu content for that div.

        The original markup has an extraneous cb:div[@type='hui'] that
        does not have a cb:mulu child; this needs to first be removed
        and its contents incorporated into the preceding
        cb:div[@type='hui'].

        """
        self._postprocess_div_mulu(work, tree, 'hui',
                                   MERGE_UNNAMED_DIVS_TO_PRECEDING)

    def _postprocess_T0328(self, work, tree):
        """Post-process the XML document T0328.xml.

        Divide into two files, one containing all of the tei:l
        material, and one the rest.

        """
        xslt_filename = resource_filename(
            __name__, 'assets/xslt/CBETA_extract_verse.xsl')
        extract_verse = etree.XSLT(etree.parse(xslt_filename))
        verse_tree = extract_verse(tree)
        verse_filename = '{}-verses.xml'.format(work)
        self._output_tree(verse_filename, verse_tree)
        prose_tree = extract_verse(tree, inverse='1')
        prose_filename = '{}-ex-verses.xml'.format(work)
        self._output_tree(prose_filename, prose_tree)

    def _postprocess_T0397(self, work, tree):
        """Post-process the XML document T0397.xml.

        Divide into multiple files, one for each cb:div[@type='other'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'other',
                                   MERGE_UNNAMED_DIVS_TO_PRECEDING)

    def _postprocess_T0418(self, work, tree):
        """Post-process the XML document T0418.xml"

        Divide into two files, one containing all of the tei:l
        material, and one the rest.

        """
        # There are verse elements within tei:app/tei:rdg that occur
        # within a prose context and have no markup specifying that
        # they are verse, so add that in.
        xslt_filename = resource_filename(
            __name__, 'assets/xslt/CBETA_T0418_fix_verse.xsl')
        fix_verse = etree.XSLT(etree.parse(xslt_filename))
        tree = fix_verse(tree)
        xslt_filename = resource_filename(
            __name__, 'assets/xslt/CBETA_extract_verse.xsl')
        extract_verse = etree.XSLT(etree.parse(xslt_filename))
        verse_tree = extract_verse(tree)
        verse_filename = '{}-revised-verses.xml'.format(work)
        self._output_tree(verse_filename, verse_tree)
        prose_tree = extract_verse(tree, inverse='1')
        prose_filename = '{}-ex-verses.xml'.format(work)
        self._output_tree(prose_filename, prose_tree)

    def _postprocess_T0664(self, work, tree):
        """Post-process the XML document T0664.xml.

        Divide into multiple files, one for each cb:div[@type='pin'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'pin')

    def _postprocess_T1331(self, work, tree):
        """Post-process the XML document T1331.xml.

        Divide into multiple files, one for each cb:div[@type='jing'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'jing')

    def _postprocess_T1361(self, work, tree):
        """Post-process the XML document T1361.xml.

        Divide into two files: the cb:div[@type='jing'] and the
        cb:div[@type='廣釋'].

        """
        div_tree = self._transform_div(tree, position='0', div_type='jing')
        div_filename = '{}-root.xml'.format(work)
        self._output_tree(div_filename, div_tree)
        div_tree = self._transform_div(tree, position='0', div_type='廣釋')
        div_filename = '{}-廣釋.xml'.format(work)
        self._output_tree(div_filename, div_tree)

    def _postprocess_T1646(self, work, tree):
        """Post-process the XML document T0664.xml.

        Divide into multiple files, one for each cb:div[@type='pin'],
        named according to the cb:mulu content for that div.

        """
        self._postprocess_div_mulu(work, tree, 'pin')

    def _postprocess_T2102(self, work, tree):
        self._postprocess_div_mulu(
            work, tree, 'other', treatment=REMOVE_UNNAMED_DIVS,
            exclude=['other'])

    def _postprocess_T2145(self, work, tree):
        div_types = [('other', 'other')]
        self._extract_divs(work, tree, div_types, exclude=['other'])

    def _remove_subdivs(self, tree, exclude):
        exclude = exclude or []
        for div_type in exclude:
            xpath = '//cb:div[@type="{}"][ancestor::cb:div]'.format(div_type)
            for div in tree.xpath(xpath, namespaces=constants.NAMESPACES):
                div.getparent().remove(div)
        return tree

    def _tidy(self, work, file_path):
        """Transforms the file at `file_path` into simpler XML and returns
        that."""
        output_file = os.path.join(self._output_dir, work)
        self._logger.info('Tidying file {} into {}'.format(
            file_path, output_file))
        try:
            tei_doc = etree.parse(file_path)
        except etree.XMLSyntaxError as err:
            self._logger.error('XML file "{}" is invalid: {}'.format(
                file_path, err))
            raise
        return self.transform(tei_doc).getroot()
