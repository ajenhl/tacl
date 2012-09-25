import logging
import os

from text import Text


class Corpus (object):

    def __init__ (self, path):
        self._path = os.path.abspath(path)
        self._texts = self._load_texts(self._path)

    def _load_texts (self, path):
        """Returns a list of `Text`\s in this corpus.

        :param path: absolute path of the corpus
        :type path: `str`
        :rtype: `list`

        """
        texts = []
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            texts.append(Text(file_path))
        return texts

    def ngrams (self, size):
        """Returns a set of n-grams of size `size` for this corpus.

        :param size: size of the n-gram
        :type size: `int`
        :rtype: `set`

        """
        ngrams = set()
        for text in self._texts:
            logging.debug('Generating set of n-grams for text %s' % text.path)
            ngrams = ngrams | text.ngrams(size)
        return ngrams
