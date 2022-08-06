"""Module containing the Corpus class."""

import glob
import logging
import os

from .text import WitnessText


class Corpus:

    """A Corpus represents a collection of `WitnessText`s.

    A Corpus is built from a directory that contains the text files
    that become `WitnessText` objects.

    """

    def __init__(self, path, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._path = os.path.abspath(path)
        self._tokenizer = tokenizer

    @property
    def path(self):
        """Returns the absolute path to this corpus.

        :rtype: `str`

        """
        return self._path

    def get_sigla(self, work):
        """Returns a list of all of the sigla for `work`.

        :param work: name of work
        :type work: `str`
        :rtype: `list` of `str`

        """
        return [os.path.splitext(os.path.basename(path))[0]
                for path in glob.glob(os.path.join(self._path, work, '*.txt'))]

    def get_witness(self, work, siglum, text_class=WitnessText):
        """Returns a `WitnessText` representing the file associated with
        `work` and `siglum`.

        Combined, `work` and `siglum` form the basis of a filename for
        retrieving the text.

        :param work: name of work
        :type work: `str`
        :param siglum: siglum of witness
        :type siglum: `str`
        :param text_class: class to use to represent the witness
        :type text_class: subclass of `Text`
        :rtype: `text_class`

        """
        filename = os.path.join(work, siglum + '.txt')
        self._logger.debug('Creating WitnessText object from {}'.format(
            filename))
        with open(os.path.join(self._path, filename), encoding='utf-8') \
                as fh:
            try:
                content = fh.read()
            except Exception:
                self._logger.error('Failed to read witness text {}'.format(
                    filename))
                raise
        return text_class(work, siglum, content, self._tokenizer)

    def get_witnesses(self, name='*', text_class=WitnessText):
        """Returns a generator supplying `WitnessText` objects for each work
        in the corpus.

        If `name` is specified, return a generator for only those
        witnesses of the specified work.

        :param name: optional name of work to limit witnesses to
        :type name: `str`
        :param text_class: class to use to represent the witness
        :type text_class: subclass of `Text`
        :rtype: `generator` of `text_class` objects

        """
        for filepath in glob.glob(os.path.join(self._path, name, '*.txt')):
            if os.path.isfile(filepath):
                name = os.path.split(os.path.split(filepath)[0])[1]
                siglum = os.path.splitext(os.path.basename(filepath))[0]
                yield self.get_witness(name, siglum, text_class)

    def get_works(self, pattern='*'):
        """Returns a list of the names of all works in the corpus that match
        `pattern`.

        :param pattern: glob pattern of work names to match on
        :type pattern: `str`
        :rtype: `list` of `str`

        """
        return [os.path.split(filepath)[1] for filepath in
                glob.glob(os.path.join(self._path, pattern))
                if os.path.isdir(filepath)]

    def normalise(self, mapping, output_dir):
        """Creates a normalised copy of this corpus in `output_dir`.

        `output_dir` must not already exist.

        :param mapping: mapping between variant and normalised forms
        :type mapping: `tacl.VariantMapping`
        :param output_dir: directory to output normalised corpus to
        :type output_dir: `str`

        """
        os.makedirs(output_dir)
        for work in self.get_works():
            work_dir = os.path.join(output_dir, work)
            os.mkdir(work_dir)
            for witness in self.get_witnesses(work):
                witness_path = os.path.join(output_dir, witness.get_filename())
                content = witness.get_token_content()
                normalised_content = mapping.normalise(content)
                with open(witness_path, 'w') as fh:
                    fh.write(normalised_content)
