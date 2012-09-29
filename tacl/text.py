# -*- coding: utf-8 -*-

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
        timestamp = int(os.stat(self._path).st_mtime)
        self._id = self._manager.add_text(filename, timestamp, corpus_label)

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
        for size in range(minimum, maximum+1):
            self._generate_ngrams(text, size)

    def _generate_ngrams (self, text, size):
        """Generates the n-grams of size `size` from `text`.

        :param text: text to generate n-grams from
        :type text: `unicode`
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
            tokens = self.tokenizer.tokenize(text)
            for ngram in nltk.util.ingrams(tokens, size):
                self._manager.add_ngram(self._id, ''.join(ngram), size)
            self._manager.commit()
