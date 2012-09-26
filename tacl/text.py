# -*- coding: utf-8 -*-

import nltk.tokenize
import nltk.util

from ngram import NGram


class Text (object):

    # A token is either a workaround (anything in square brackets, as
    # a whole), or a single character that is not a Chinese full stop,
    # parentheses, question mark, or whitespace character.
    tokenizer = nltk.tokenize.RegexpTokenizer(ur'\[[^]]*\]|[^。\(\)\?\s]')

    def __init__ (self, path):
        self._path = path

    def ngrams (self, size):
        """Returns a set of `NGram`\s of size `size` for this text.

        :param size: size of the n-gram
        :type size: `int`
        :rtype: `set`

        """
        ngrams = set()
        with open(self._path, 'rU') as fh:
            text = fh.read().decode('utf-8')
        tokens = self.tokenizer.tokenize(text)
        for ngram_tuple in nltk.util.ingrams(tokens, size):
            ngram = NGram(ngram_tuple)
            ngram.add_reference(self)
            ngrams.add(ngram)
        return ngrams

    @property
    def path (self):
        return self._path
