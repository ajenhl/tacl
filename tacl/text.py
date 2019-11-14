"""Module containing the Text and WitnessText classes."""

import collections
import hashlib
import os.path
import re


class Text:

    """Class for base text functionality (getting tokens, generating
    n-grams).

    Used for (snippets of) texts that are not witnesses.

    """

    def __init__(self, content, tokenizer):
        self._content = content
        self._tokenizer = tokenizer

    def excise(self, ngrams, replacement):
        """Returns the token content of this text with every occurrence of
        each n-gram in `ngrams` replaced with `replacement`.

        The replacing is performed on each n-gram by descending order
        of length.

        :param ngrams: n-grams to be replaced
        :type ngrams: `list` of `str`
        :param replacement: replacement string
        :type replacement: `str`
        :rtype: `str`

        """
        content = self.get_token_content()
        ngrams.sort(key=len, reverse=True)
        for ngram in ngrams:
            content = content.replace(ngram, replacement)
        return content

    @property
    def content(self):
        """Returns the content of this text.

        :rtype: `str`

        """
        return self._content

    def get_ngrams(self, minimum, maximum, skip_sizes=None):
        """Returns a generator supplying the n-grams (`minimum` <= n
        <= `maximum`) for this text.

        Each iteration of the generator supplies a tuple consisting of
        the size of the n-grams and a `collections.Counter` of the
        n-grams.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :param skip_sizes: sizes to not generate n-grams for
        :type skip_sizes: `list` of `int`
        :rtype: `generator`

        """
        skip_sizes = skip_sizes or []
        tokens = self.get_tokens()
        for size in range(minimum, maximum + 1):
            if size not in skip_sizes:
                ngrams = collections.Counter(self._ngrams(tokens, size))
                yield (size, ngrams)

    def get_token_content(self):
        """Returns a string of the tokens in this text joined using the
        tokenizer joiner string.

        :rtype: `str`

        """
        return self._tokenizer.joiner.join(self.get_tokens())

    def get_tokens(self):
        """Returns a list of tokens in this text.

        :rtype: `list` of `str`

        """
        return self._tokenizer.tokenize(self._content.replace(
            '\n', self._tokenizer.joiner))

    def _ngrams(self, sequence, degree):
        """Returns the n-grams generated from `sequence`.

        Based on the ngrams function from the Natural Language
        Toolkit.

        Each n-gram in the returned list is a string with whitespace
        removed.

        :param sequence: the source data to be converted into n-grams
        :type sequence: sequence
        :param degree: the degree of the n-grams
        :type degree: `int`
        :rtype: `list` of `str`

        """
        count = max(0, len(sequence) - degree + 1)
        return [self._tokenizer.joiner.join(sequence[i:i + degree])
                for i in range(count)]


class WitnessText (Text):

    """Class for the text of a witness. A witness has a work name and a
    siglum, and has a corresponding filename."""

    def __init__(self, work, siglum, content, tokenizer):
        super().__init__(content, tokenizer)
        self._work = work
        self._siglum = siglum
        self._filename = self.assemble_filename(work, siglum)

    @staticmethod
    def assemble_filename(work, siglum):
        return os.path.join(work, siglum + '.txt')

    def get_checksum(self):
        """Returns the checksum for the content of this text.

        :rtype: `str`

        """
        return hashlib.md5(self._content.encode('utf-8')).hexdigest()

    def get_filename(self):
        """Returns the filename of this text.

        :rtype: `str`

        """
        return self._filename

    @property
    def siglum(self):
        return self._siglum

    @property
    def work(self):
        return self._work


class FilteredWitnessText (WitnessText):

    """Class for the text of a witness that supplies only those n-grams
    that contain a supplied list of n-grams."""

    @staticmethod
    def get_filter_ngrams_pattern(filter_ngrams):
        """Returns a compiled regular expression matching on any of the
        n-grams in `filter_ngrams`.

        :param filter_ngrams: n-grams to use in regular expression
        :type filter_ngrams: `list` of `str`
        :rtype: `_sre.SRE_Pattern`

        """
        return re.compile('|'.join([re.escape(ngram) for ngram in
                                    filter_ngrams]))

    def get_ngrams(self, minimum, maximum, filter_ngrams):
        """Returns a generator supplying the n-grams (`minimum` <= n
        <= `maximum`) for this text.

        Each iteration of the generator supplies a tuple consisting of
        the size of the n-grams and a `collections.Counter` of the
        n-grams.

        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :param filter_ngrams: n-grams that must be contained by the generated
                              n-grams
        :type filter_ngrams: `list`
        :rtype: `generator`

        """
        tokens = self.get_tokens()
        filter_pattern = self.get_filter_ngrams_pattern(filter_ngrams)
        for size in range(minimum, maximum + 1):
            ngrams = collections.Counter(
                self._ngrams(tokens, size, filter_pattern))
            yield (size, ngrams)

    def _ngrams(self, sequence, degree, filter_ngrams):
        return [ngram for ngram in super()._ngrams(sequence, degree)
                if filter_ngrams.search(ngram)]
