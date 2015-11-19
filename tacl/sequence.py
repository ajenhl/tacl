"""Module containing the Sequence and Sequencer classes."""

import logging
import os
import re

from Bio import pairwise2
from jinja2 import Environment, PackageLoader
import pandas as pd

from . import constants


class Sequence:

    def __init__ (self, alignment, substitutes):
        self._alignment = alignment
        self._substitutes = substitutes

    def _format_alignment (self, a1, a2):
        html = []
        for index, char in enumerate(a1):
            output = self._substitutes.get(char, char)
            if a2[index] == char:
                html.append('<span class="match">{}</span>'.format(output))
            elif char != '-':
                html.append(output)
        return ''.join(html)

    def render (self):
        """Returns a tuple of HTML fragments rendering each element of the
        sequence."""
        f1 = self._format_alignment(self._alignment[0], self._alignment[1])
        f2 = self._format_alignment(self._alignment[1], self._alignment[0])
        return f1, f2


class Sequencer:

    def __init__ (self, corpus, tokenizer, results, output_dir):
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus
        self._tokenizer = tokenizer
        self._matches = pd.read_csv(results, encoding='utf-8', na_filter=False)
        self._output_dir = output_dir

    def _generate_sequence (self, t1, t1_span, t2, t2_span, context_length,
                            covered_spans):
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
        return Sequence(alignment, self._r_substitutes)

    def generate_sequences (self, minimum_size):
        loader = PackageLoader('tacl', 'assets/templates')
        env = Environment(loader=loader)
        template = env.get_template('sequence.html')
        # Get a list of the files in the matches, grouped by label
        # (ordered by number of texts).
        labels = list(self._matches.groupby([constants.LABEL_FIELDNAME])[constants.NAME_FIELDNAME].nunique().index)
        ngrams = self._matches[self._matches[constants.SIZE_FIELDNAME] >= minimum_size].sort(constants.SIZE_FIELDNAME, ascending=False)[constants.NGRAM_FIELDNAME].unique()
        for index, primary_label in enumerate(labels):
            for secondary_label in labels[index+1:]:
                self._generate_sequences(primary_label, secondary_label, ngrams,
                                         template)

    def _generate_sequences (self, primary_label, secondary_label, ngrams,
                             template):
        self._substitutes = {}
        self._char_code = 61440
        cols = [constants.NAME_FIELDNAME, constants.SIGLUM_FIELDNAME]
        primary_texts = self._matches[self._matches[constants.LABEL_FIELDNAME] == primary_label][cols].drop_duplicates()
        secondary_texts = self._matches[self._matches[constants.LABEL_FIELDNAME] == secondary_label][cols].drop_duplicates()
        for index, (name1, siglum1) in primary_texts.iterrows():
            text1 = self._get_text(name1, siglum1)
            label1 = '{}_{}'.format(name1, siglum1)
            for index, (name2, siglum2) in secondary_texts.iterrows():
                text2 = self._get_text(name2, siglum2)
                label2 = '{}_{}'.format(name2, siglum2)
                self._generate_sequences_for_texts(label1, text1, label2, text2,
                                                   ngrams, template)

    def _generate_sequences_for_texts (self, l1, t1, l2, t2, ngrams, template):
        self._r_substitutes = dict((v, k) for k, v in self._substitutes.items())
        sequences = []
        covered_spans = [[], []]
        for ngram in ngrams:
            # Keep track of the spans within each text that have been
            # covered by a sequence, to ensure that they aren't
            # reported more than once.
            sequences.extend(self._generate_sequences_for_ngram(
                t1, t2, ngram, covered_spans))
        if sequences:
            html = template.render(l1=l1, l2=l2, sequences=sequences)
            os.makedirs(self._output_dir, exist_ok=True)
            output_name = os.path.join(self._output_dir,
                                       '{}-{}.html'.format(l1, l2))
            with open(output_name, 'w', encoding='utf-8') as fh:
                fh.write(html)

    def _generate_sequences_for_ngram (self, t1, t2, ngram, covered_spans):
        self._logger.debug('Generating sequences for n-gram "{}"'.format(ngram))
        pattern = re.compile(re.escape(ngram))
        context_length = len(ngram)
        t1_spans = [match.span() for match in pattern.finditer(t1)]
        t2_spans = [match.span() for match in pattern.finditer(t2)]
        sequences = []
        for t1_span in t1_spans:
            for t2_span in t2_spans:
                if self._is_inside(t1_span, t2_span, covered_spans):
                    self._logger.debug('Skipping match due to existing coverage')
                    continue
                sequence = self._generate_sequence(
                    t1, t1_span, t2, t2_span, context_length, covered_spans)
                if sequence:
                    sequences.append(sequence.render())
        return sequences

    def _get_text (self, name, siglum):
        """Returns the text identified by `name` and `siglum`, with all []
        tokens replaced with a single character. Substitutions are
        recorded in self._substitutes.

        """
        tokens = self._corpus.get_text(name, siglum).get_tokens()
        for i, token in enumerate(tokens):
            if len(token) > 1:
                char = chr(self._char_code)
                substitute = self._substitutes.setdefault(token, char)
                if substitute == char:
                    self._char_code += 1
                tokens[i] = substitute
        return self._tokenizer.joiner.join(tokens)

    def _get_text_sequence (self, text, span, context_length):
        start = max(0, span[0] - context_length)
        end = min(len(text), span[1] + context_length)
        return text[start:end], (start, end)

    def _is_inside (self, span1, span2, covered_spans):
        """Returns True if both `span1` and `span2` fall within
        `covered_spans`."""
        if self._is_span_inside(span1, covered_spans[0]) and \
           self._is_span_inside(span2, covered_spans[1]):
            return True
        return False

    def _is_span_inside (self, span, covered_spans):
        start = span[0]
        end = span[1]
        for c_start, c_end in covered_spans:
            if start >= c_start and end <= c_end:
                return True
        return False
