# -*- coding: utf-8 -*-

import collections
import hashlib
import logging
import os

import nltk.tokenize
import nltk.util


class Text (object):

    # A token is either a workaround (anything in square brackets, as
    # a whole), or a single character that is not a Chinese full stop,
    # parentheses, question mark, or whitespace character.
    tokenizer = nltk.tokenize.RegexpTokenizer(ur'\[[^]]*\]|[^。\(\)\?\s]')

    def __init__ (self, filename, corpus_path, manager, corpus_label):
        self._filename = filename
        self._path = os.path.join(corpus_path, filename)
        self._manager = manager
        checksum = hashlib.md5(open(self._path, 'rU').read()).hexdigest()
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
        with open(self._path, 'rU') as fh:
            text = fh.read().decode('utf-8')
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
            counts = collections.Counter(nltk.util.ingrams(tokens, size))
            for ngram, count in counts.items():
                self._manager.add_ngram(self._id, ''.join(ngram), size, count)
            self._manager.commit()
