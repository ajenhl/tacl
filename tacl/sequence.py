"""Module containing the Sequence and SequenceReport classes."""

import logging
import os
import re

from Bio import pairwise2
import pandas as pd

from . import constants
from .report import Report
from .text import Text


class Sequence:

    """Class to format supplied sequences using simple HTML span markup."""

    def __init__(self, alignment, substitutes, start_index):
        self._alignment = alignment
        self._substitutes = substitutes
        self._start_index = start_index

    def _format_alignment(self, a1, a2):
        """Returns `a1` marked up with HTML spans around characters that are
        also at the same index in `a2`.

        :param a1: text sequence from one witness
        :type a1: `str`
        :param a2: text sequence from another witness
        :type a2: `str`
        :rtype: `str`

        """
        html = []
        for index, char in enumerate(a1):
            output = self._substitutes.get(char, char)
            if a2[index] == char:
                html.append('<span class="match">{}</span>'.format(output))
            elif char != '-':
                html.append(output)
        return ''.join(html)

    def render(self):
        """Returns a tuple of HTML fragments rendering each element of the
        sequence."""
        f1 = self._format_alignment(self._alignment[0], self._alignment[1])
        f2 = self._format_alignment(self._alignment[1], self._alignment[0])
        return f1, f2

    @property
    def start_index(self):
        return self._start_index


class SequenceReport (Report):

    _report_name = 'sequence'

    def __init__(self, corpus, tokenizer, results):
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus
        self._tokenizer = tokenizer
        self._matches = pd.read_csv(results, encoding='utf-8', na_filter=False)
        self._substitutes = {}
        self._char_code = 61440

    def generate(self, output_dir, minimum_size):
        """Generates sequence reports and writes them to the output directory.

        :param output_dir: directory to output reports to
        :type output_dir: `str`
        :param minimum_size: minimum size of n-grams to create sequences for
        :type minimum_size: `int`

        """
        self._output_dir = output_dir
        # Get a list of the files in the matches, grouped by label
        # (ordered by number of works).
        labels = list(self._matches.groupby([constants.LABEL_FIELDNAME])[
            constants.WORK_FIELDNAME].nunique().index)
        original_ngrams = self._matches[
            self._matches[
                constants.SIZE_FIELDNAME] >= minimum_size].sort_values(
                by=constants.SIZE_FIELDNAME, ascending=False)[
                    constants.NGRAM_FIELDNAME].unique()
        ngrams = []
        for original_ngram in original_ngrams:
            ngrams.append(self._get_text(Text(original_ngram,
                                              self._tokenizer)))
        # Generate sequences for each witness in every combination of
        # (different) labels.
        for index, primary_label in enumerate(labels):
            for secondary_label in labels[index+1:]:
                self._generate_sequences(primary_label, secondary_label,
                                         ngrams)

    def _generate_sequence(self, t1, t1_span, t2, t2_span, context_length,
                           covered_spans):
        """Returns an aligned sequence (or None) between extract `t1_span` of
        witness text `t1` and extract `t2_span` of witness text `t2`.

        Adds the span of the aligned sequence, if any, to
        `covered_spans` (which, being mutable, is modified in place
        without needing to be returned).

        This method repeats the alignment process, increasing the
        context length until the alignment score (the measure of how
        much the two sequences align) drops below a certain point or
        it is not possible to increase the context length.

        :param t1: text content of first witness
        :type t1: `str`
        :param t1_span: start and end indices within `t1` to align
        :type t1_span: 2-`tuple` of `int`
        :param t2: text content of second witness
        :type t2: `str`
        :param t2_span: start and end indices within `t2` to align
        :type t2_span: 2-`tuple` of `int`
        :param context_length: length of context on either side of
                               the spans to include in the sequence
        :type context_length: `int`
        :param covered_spans: lists of start and end indices for parts
                              of the texts already covered by a sequence
        :type covered_spans: `list` of two `list`s of 2-`tuple` of `int`

        """
        old_length = 0
        self._logger.debug('Match found; generating new sequence')
        while True:
            s1, span1 = self._get_text_sequence(t1, t1_span, context_length)
            s2, span2 = self._get_text_sequence(t2, t2_span, context_length)
            length = len(s1)
            alignment = pairwise2.align.globalms(
                s1, s2, constants.IDENTICAL_CHARACTER_SCORE,
                constants.DIFFERENT_CHARACTER_SCORE,
                constants.OPEN_GAP_PENALTY, constants.EXTEND_GAP_PENALTY)[0]
            context_length = length
            score = alignment[2] / length
            if not alignment:
                return None
            elif score < constants.SCORE_THRESHOLD or length == old_length:
                break
            else:
                self._logger.debug('Score: {}'.format(score))
            old_length = length
        covered_spans[0].append(span1)
        covered_spans[1].append(span2)
        return Sequence(alignment, self._reverse_substitutes, t1_span[0])

    def _generate_sequences(self, primary_label, secondary_label, ngrams):
        """Generates aligned sequences between each witness labelled
        `primary_label` and each witness labelled `secondary_label`,
        based around `ngrams`.

        :param primary_label: label for one side of the pairs of
                              witnesses to align
        :type primary_label: `str`
        :param secondary_label: label for the other side of the pairs
                                of witnesses to align
        :type secondary_label: `str`
        :param ngrams: n-grams to base sequences off
        :type ngrams: `list` of `str`

        """
        cols = [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME]
        primary_works = self._matches[self._matches[
            constants.LABEL_FIELDNAME] == primary_label][
                cols].drop_duplicates()
        secondary_works = self._matches[self._matches[
            constants.LABEL_FIELDNAME] == secondary_label][
                cols].drop_duplicates()
        for index, (work1, siglum1) in primary_works.iterrows():
            text1 = self._get_text(self._corpus.get_witness(work1, siglum1))
            label1 = '{}_{}'.format(work1, siglum1)
            for index, (work2, siglum2) in secondary_works.iterrows():
                text2 = self._get_text(self._corpus.get_witness(
                    work2, siglum2))
                label2 = '{}_{}'.format(work2, siglum2)
                self._generate_sequences_for_texts(label1, text1, label2,
                                                   text2, ngrams)

    def _generate_sequences_for_ngram(self, t1, t2, ngram, covered_spans):
        """Generates aligned sequences for the texts `t1` and `t2`, based
        around `ngram`.

        Does not generate sequences that occur within `covered_spans`.

        :param t1: text content of first witness
        :type t1: `str`
        :param t2: text content of second witness
        :type t2: `str`
        :param ngram: n-gram to base sequences on
        :type ngram: `str`
        :param covered_spans: lists of start and end indices for parts
                              of the texts already covered by a sequence
        :type covered_spans: `list` of two `list`s of 2-`tuple` of `int`

        """
        self._logger.debug('Generating sequences for n-gram "{}"'.format(
            ngram))
        pattern = re.compile(re.escape(ngram))
        context_length = len(ngram)
        t1_spans = [match.span() for match in pattern.finditer(t1)]
        t2_spans = [match.span() for match in pattern.finditer(t2)]
        sequences = []
        self._logger.debug(t1)
        for t1_span in t1_spans:
            for t2_span in t2_spans:
                if self._is_inside(t1_span, t2_span, covered_spans):
                    self._logger.debug(
                        'Skipping match due to existing coverage')
                    continue
                sequence = self._generate_sequence(
                    t1, t1_span, t2, t2_span, context_length, covered_spans)
                if sequence:
                    sequences.append(sequence)
        return sequences

    def _generate_sequences_for_texts(self, l1, t1, l2, t2, ngrams):
        """Generates and outputs aligned sequences for the texts `t1` and `t2`
        from `ngrams`.

        :param l1: label of first witness
        :type l1: `str`
        :param t1: text content of first witness
        :type t1: `str`
        :param l2: label of second witness
        :type l2: `str`
        :param t2: text content of second witness
        :type t2: `str`
        :param ngrams: n-grams to base sequences on
        :type ngrams: `list` of `str`

        """
        # self._subsitutes is gradually populated as each text is
        # processed, so this needs to be regenerated each time.
        self._reverse_substitutes = dict((v, k) for k, v in
                                         self._substitutes.items())
        sequences = []
        # Keep track of spans within each text that have been covered
        # by an aligned sequence, to ensure that they aren't reported
        # more than once. The first sub-list contains span indices for
        # text t1, the second for t2.
        covered_spans = [[], []]
        for ngram in ngrams:
            sequences.extend(self._generate_sequences_for_ngram(
                t1, t2, ngram, covered_spans))
        if sequences:
            sequences.sort(key=lambda x: x.start_index)
            context = {'l1': l1, 'l2': l2, 'sequences': sequences}
            report_name = '{}-{}.html'.format(l1, l2)
            os.makedirs(self._output_dir, exist_ok=True)
            self._write(context, self._output_dir, report_name)

    def _get_text(self, text):
        """Returns the text content of `text`, with all multi-character tokens
        replaced with a single character. Substitutions are recorded
        in self._substitutes.

        :param text: text to get content from
        :type text: `Text`
        :rtype: `str`

        """
        tokens = text.get_tokens()
        for i, token in enumerate(tokens):
            if len(token) > 1:
                char = chr(self._char_code)
                substitute = self._substitutes.setdefault(token, char)
                if substitute == char:
                    self._char_code += 1
                tokens[i] = substitute
        return self._tokenizer.joiner.join(tokens)

    def _get_text_sequence(self, text, span, context_length):
        """Returns the subset of `text` encompassed by `span`, plus
        `context_length` characters before and after.

        :param text: text to extract the sequence from
        :type text: `str`
        :param span: start and end indices within `text`
        :type span: 2-`tuple` of `int`
        :param context_length: length of context on either side of
                               `span` to include in the extract
        :type context_length: `int`

        """
        start = max(0, span[0] - context_length)
        end = min(len(text), span[1] + context_length)
        return text[start:end], (start, end)

    def _is_inside(self, span1, span2, covered_spans):
        """Returns True if both `span1` and `span2` fall within
        `covered_spans`.

        :param span1: start and end indices of a span
        :type span1: 2-`tuple` of `int`
        :param span2: start and end indices of a span
        :type span2: 2-`tuple` of `int`
        :param covered_spans: lists of start and end indices for parts
                              of the texts already covered by a sequence
        :type covered_spans: `list` of two `list`s of 2-`tuple` of `int`
        :rtype: `bool`

        """
        if self._is_span_inside(span1, covered_spans[0]) and \
           self._is_span_inside(span2, covered_spans[1]):
            return True
        return False

    def _is_span_inside(self, span, covered_spans):
        """Returns True if `span` falls within `covered_spans`.

        :param span: start and end indices of a span
        :type span: 2-`tuple` of `int`
        :param covered_spans: list of start and end indices for parts
                              of the text already covered by a sequence
        :type covered_spans: `list` of  2-`tuple` of `int`
        :rtype: `bool`

        """
        start = span[0]
        end = span[1]
        for c_start, c_end in covered_spans:
            if start >= c_start and end <= c_end:
                return True
        return False
