"""Module containing the Text class."""

import collections
import hashlib


class BaseText:

    def __init__ (self, content, tokenizer):
        self._content = content
        self._tokenizer = tokenizer

    def get_content (self):
        """Returns the content of this text.

        :rtype: `str`

        """
        return self._content

    def get_ngrams (self, minimum, maximum):
        """Returns a generator supplying the n-grams (`minimum` <= n
        <= `maximum`) for this text.

        Each iteration of the generator supplies a tuple consisting of
        the size of the n-grams and a `collections.Counter` of the
        n-grams.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :rtype: `generator`

        """
        tokens = self.get_tokens()
        for size in range(minimum, maximum + 1):
            ngrams = collections.Counter(self._ngrams(tokens, size))
            yield (size, ngrams)

    def get_tokens (self):
        """Returns a list of tokens in this text."""
        return self._tokenizer.tokenize(self._content)

    def _ngrams (self, sequence, degree):
        """Returns the n-grams generated from `sequence`.

        Based on the ngrams function from the Natural Language
        Toolkit.

        Each n-gram in the returned list is a string with whitespace
        removed.

        :param sequence: the source data to be converted into n-grams
        :type sequence: sequence
        :param degree: the degree of the n-grams
        :type degree: int
        :rtype: `list` of `str`

        """
        count = max(0, len(sequence) - degree + 1)
        # The extra split and join are due to having to handle
        # whitespace within a CBETA token (eg, [(禾*尤)\n/上/日]).
        return [self._tokenizer.joiner.join(
            self._tokenizer.joiner.join(sequence[i:i+degree]).split())
                for i in range(count)]


class Text (BaseText):

    def __init__ (self, filename, content, tokenizer):
        super().__init__(content, tokenizer)
        self._filename = filename

    def get_checksum (self):
        """Returns the checksum for the content of this text.

        :rtype: `str`

        """
        return hashlib.md5(self._content.encode('utf-8')).hexdigest()

    def get_filename (self):
        """Returns the filename of this text.

        :rtype: `str`

        """
        return self._filename
