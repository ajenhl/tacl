class NGram (object):

    _cache = {}

    def __init__ (self, ngram):
        if not hasattr(self, '_initialised'):
            # Since __init__ is called even when self is retrieved
            # from NGram._cache, don't reset values.
            self._initialised = True
            self._ngram = ngram
            self._refs = {}

    def __new__ (cls, ngram):
        try:
            obj = NGram._cache[ngram]
        except KeyError:
            obj = object.__new__(cls)
            NGram._cache[ngram] = obj
        return obj

    def __unicode__ (self):
        return ''.join(self._ngram)

    def add_reference (self, text):
        """Adds a reference to `text` for this n-gram."""
        self._refs[text] = self._refs.get(text, 0) + 1

    def text_count (self, text):
        """Returns the count of references to this ngram in `text`.

        :rtype: `int`

        """
        return self._refs.get(text, 0)

    def text_counts (self):
        """Returns the counts for each text that references this ngram.

        :rtype: `dict`

        """
        return self._refs

    def total_count (self):
        """Returns the total count of references to this ngram.

        :rtype: `int`

        """
        total = 0
        for count in self._refs.values():
            total += count
        return total
