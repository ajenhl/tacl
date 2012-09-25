import nltk.util

from ngram import NGram


class Text (object):

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
            tokens = list(fh.read().decode('utf-8').replace('\n', ''))
        for ngram_tuple in nltk.util.ingrams(tokens, size):
            ngram = NGram(ngram_tuple)
            ngram.add_reference(self)
            ngrams.add(ngram)
        return ngrams

    @property
    def path (self):
        return self._path
