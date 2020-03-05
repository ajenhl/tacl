from copy import deepcopy
import os.path

from lxml import etree

from . import constants
from .exceptions import TACLError


class WorkJoiner:

    def __init__(self, corpus_dir):
        self._corpus_dir = os.path.abspath(corpus_dir)

    def _add_work(self, tei_corpus, work):
        tree = etree.parse(self._get_work_path(work))
        tei_elements = tree.xpath('/tei:teiCorpus/tei:TEI',
                                  namespaces=constants.NAMESPACES)
        for tei_element in tei_elements:
            new_tei_element = deepcopy(tei_element)
            new_tei_element.attrib.pop(constants.XML + 'id', None)
            tei_corpus.append(new_tei_element)

    def _get_work_path(self, work):
        return os.path.join(self._corpus_dir, '{}.xml'.format(work))

    def join(self, output, works):
        output_path = self._get_work_path(output)
        if os.path.exists(output_path):
            raise TACLError(constants.JOIN_WORKS_EXISTING_OUTPUT_ERROR.format(
                output_path))
        tree = etree.parse(self._get_work_path(works[0]))
        tei_corpus = tree.getroot()
        for work in works[1:]:
            self._add_work(tei_corpus, work)
        tree.write(output_path, encoding='utf-8', pretty_print=True)
