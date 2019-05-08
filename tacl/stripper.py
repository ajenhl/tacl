"""Module containing the Stripper class."""

import logging
import os

from lxml import etree
from pkg_resources import resource_filename

from . import constants


class Stripper:

    """Class used for preprocessing a corpus of texts by stripping out all
    material that is not the textual material proper, and generating
    plain text witness files for each witness attested.

    The intention is to keep the stripped text as close in formatting
    to the original as possible, including whitespace.

    """

    def __init__(self, input_dir, output_dir):
        self._logger = logging.getLogger(__name__)
        self._input_dir = os.path.abspath(input_dir)
        self._output_dir = os.path.abspath(output_dir)
        xslt_filename = resource_filename(
            __name__, 'assets/xslt/strip_tei.xsl')
        self.transform = etree.XSLT(etree.parse(xslt_filename))

    def get_witnesses(self, source_tree):
        """Returns a list of all witnesses of variant readings in
        `source_tree` along with their XML ids.

        :param source_tree: XML tree of source document
        :type source_tree: `etree._ElementTree`
        :rtype: `list` of `tuple`

        """
        witnesses = []
        witness_elements = source_tree.xpath(
            '/tei:*/tei:teiHeader/tei:fileDesc/tei:sourceDesc/'
            'tei:listWit/tei:witness', namespaces=constants.NAMESPACES)
        for witness_element in witness_elements:
            witnesses.append((witness_element.text,
                              witness_element.get(constants.XML + 'id')))
        if not witnesses:
            witnesses = [(constants.BASE_WITNESS, constants.BASE_WITNESS_ID)]
        return witnesses

    def _output_file(self, work, witnesses):
        work_dir = os.path.join(self._output_dir, work)
        try:
            os.makedirs(work_dir)
        except OSError as err:
            logging.error('Could not create output directory: {}'.format(
                err))
            raise
        for witness in witnesses.keys():
            witness_file_path = os.path.join(
                work_dir, '{}.txt'.format(witness))
            with open(witness_file_path, 'wb') as output_file:
                output_file.write(witnesses[witness].encode('utf-8'))

    def strip_files(self):
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
                    work, witnesses = self.strip_file(
                        os.path.join(dirpath, filename))
                    self._output_file(work, witnesses)

    def strip_file(self, filename):
        file_path = os.path.join(self._input_dir, filename)
        work = os.path.splitext(os.path.basename(filename))[0]
        stripped_file_path = os.path.join(self._output_dir, work)
        self._logger.info('Stripping file {} into {}'.format(
            file_path, stripped_file_path))
        try:
            tei_doc = etree.parse(file_path)
        except etree.XMLSyntaxError:
            logging.warning('XML file "{}" is invalid'.format(filename))
            return
        witnesses = {}
        for witness, witness_id in self.get_witnesses(tei_doc):
            witness_param = "'{}'".format(witness_id)
            text = str(self.transform(tei_doc, witness_id=witness_param))
            witnesses[witness] = text
        return work, witnesses
