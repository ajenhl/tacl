# -*- coding: utf-8 -*-

import collections
import hashlib
import logging
import os
import re


class Tokenizer (object):

    """A tokenizer that splits a string using a regular expression.

    Based on the RegexpTokenizer from the Natural Language Toolkit.

    """

    def __init__ (self, pattern, flags=re.UNICODE | re.MULTILINE | re.DOTALL):
        try:
            self._regexp = re.compile(pattern, flags)
        except re.error as err:
            raise ValueError('Error in regular expression %r: %s' %
                             (pattern, err))

    def tokenize (self, text):
        return self._regexp.findall(text)


class Text (object):

    # A token is either a workaround (anything in square brackets, as
    # a whole), or a single character that is not a Chinese full stop,
    # parentheses, question mark, or whitespace character.
    tokenizer = Tokenizer(r'\[[^]]*\]|\w')

    def __init__ (self, filename, corpus_path, manager, corpus_label):
        self._filename = filename
        self._path = os.path.join(corpus_path, filename)
        self._manager = manager
        checksum = hashlib.md5(open(self._path, 'rb').read()).hexdigest()
        self._id = self._manager.add_text(filename, checksum, corpus_label)

    def generate_ngrams (self, minimum, maximum):
        """Generates the n-grams (`minimum` <= n <= `maximum`) for
        this text.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`

        """
        logging.debug('Generating n-grams (%d <= n <= %d) for %s' %
                      (minimum, maximum, self._filename))
        with open(self._path, encoding='utf-8') as fh:
            text = fh.read()
        tokens = self.tokenizer.tokenize(text)
        for size in range(minimum, maximum+1):
            self._generate_ngrams(tokens, size)

    def _generate_ngrams (self, tokens, size):
        """Generates the n-grams of size `size` from `text`.

        :param tokens: tokens to generate n-grams from
        :type tokens: `list`
        :param size: size of the n-gram
        :type size: `int`

        """
        # Check that there aren't already n-grams of this size in the
        # database, in which case there is no need to generate them
        # again.
        if self._manager.has_ngrams(self._id, size):
            logging.debug('%s already has %d-grams; not regenerating' %
                          (self._filename, size))
        else:
            logging.debug('Generating %d-grams for %s' % (size, self._filename))
            self._manager.add_text_ngram(self._id, size)
            counts = collections.Counter(self._ingrams(tokens, size))
            logging.debug('There are %d unique %d-grams' % (len(counts), size))
            for ngram, count in counts.items():
                self._manager.add_ngram(self._id, ''.join(ngram), size, count)
            self._manager.commit()

    def _ingrams (self, sequence, n):
        """Returns the n-grams generated from `sequence`, as an
        iterator.

        Base on the ingrams function from the Natural Language
        Toolkit.

        :param sequence: the source data to be converted into n-grams
        :type sequence: sequence or iter
        :param n: the degree of the n-grams
        :type n: int

        """
        sequence = iter(sequence)
        history = []
        while n > 1:
            history.append(next(sequence))
            n -= 1
        for item in sequence:
            history.append(item)
            yield tuple(history)
            del history[0]
