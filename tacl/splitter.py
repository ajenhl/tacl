"""Module containing the Splitter class."""

import logging
import os
import shutil

from lxml import etree

from . import constants
from .exceptions import MalformedSplitConfigurationError


class Splitter:

    def __init__(self, corpus):
        """Initialise a Splitter object.

        :param corpus: corpus containing works to split
        :type corpus: `Corpus`

        """
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus

    def split(self, conf_path):
        """Split a work into one or more works each containing a part or parts
        of the source text.

        `conf_path` (minus any extension) provides the name of the
        work to be split.

        The output works are written to the corpus specified for the
        Splitter instance.

        :param conf_path: path to split configuration file
        :type conf_path: `str`

        """
        self._logger.debug("Using split configuration {}".format(conf_path))
        in_work_name = os.path.splitext(os.path.basename(conf_path))[0]
        in_work_path = os.path.join(self._corpus.path, in_work_name)
        if not os.path.exists(in_work_path):
            raise MalformedSplitConfigurationError(
                constants.SPLIT_WORK_NOT_IN_CORPUS_ERROR.format(in_work_name))
        config = etree.parse(conf_path)
        witnesses = list(self._corpus.get_witnesses(in_work_name))
        sigla = [witness.siglum for witness in witnesses]
        for out_work in config.xpath('/splits/work'):
            self.split_work(in_work_name, out_work, witnesses, sigla)
        root = config.getroot()
        if root.get('delete') == 'true':
            try:
                shutil.rmtree(in_work_path)
            except OSError as e:
                self._logger.error(constants.SPLIT_DELETE_FAILED.format(
                    in_work_name, e))

    def split_work(self, in_work_name, out_work, witnesses, sigla):
        out_work_name = out_work[0].text
        out_work_path = os.path.join(self._corpus.path, out_work_name)
        if os.path.exists(out_work_path):
            raise MalformedSplitConfigurationError(
                constants.SPLIT_OUTPUT_DIRECTORY_EXISTS.format(out_work_path,
                                                               in_work_name))
        os.mkdir(out_work_path)
        if out_work.get('rename', 'false') == 'true':
            parts = None
        else:
            parts = out_work[1][0:]
        for witness in witnesses:
            source_text = witness.content
            output_text = []
            siglum = witness.siglum
            if parts is None:
                output_text.append(witness.content)
            else:
                for part in parts:
                    if part[0].tag != 'witnesses':
                        raise MalformedSplitConfigurationError(
                            constants.SPLIT_MISSING_WITNESSES.format(
                                in_work_name))
                    witness_refs = part[0].text.split(',')
                    for witness_ref in witness_refs:
                        if witness_ref != 'ALL' and witness_ref not in sigla:
                            raise MalformedSplitConfigurationError(
                                constants.SPLIT_INVALID_WITNESS.format(
                                    witness_ref, in_work_name))
                    if witness_refs[0] == 'ALL' or siglum in witness_refs:
                        source_text, output_text = self._split_part(
                            in_work_name, part, siglum, source_text,
                            output_text)
            if output_text:
                output_path = os.path.join(out_work_path, '{}.txt'.format(
                    siglum))
                with open(output_path, 'w', encoding='utf-8') as fh:
                    fh.write(''.join(output_text))

    def _split_part(self, source_work, part, siglum, source_text, output_text):
        if part[1].tag == 'start':
            start_text = part[1].text
            end_text = part[2].text
            try:
                start_index = source_text.index(start_text)
            except ValueError:
                raise MalformedSplitConfigurationError(
                    constants.SPLIT_MISSING_START_STRING.format(
                        start_text, source_work, siglum))
            try:
                end_index = source_text.index(end_text)
            except ValueError:
                raise MalformedSplitConfigurationError(
                    constants.SPLIT_MISSING_END_STRING.format(
                        end_text, source_work, siglum))
            if end_index < start_index:
                raise MalformedSplitConfigurationError(
                    constants.SPLIT_MIXED_START_END_STRINGS.format(
                        start_text, end_text, source_work, siglum))
            end_index += len(end_text)
        elif part[1].tag == 'whole':
            whole_text = part[1].text
            try:
                start_index = source_text.index(whole_text)
            except ValueError:
                raise MalformedSplitConfigurationError(
                    constants.SPLIT_MISSING_WHOLE_STRING.format(
                        whole_text, source_work, siglum))
            end_index = start_index + len(whole_text)
        output_text.append(source_text[start_index:end_index])
        source_text = source_text[:start_index] + \
            source_text[end_index:]
        return source_text, output_text
