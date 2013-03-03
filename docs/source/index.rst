.. TACL documentation master file, created by
   sphinx-quickstart on Sun Sep 30 19:40:33 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TACL's documentation!
================================

Requirements
------------

* `Python 3`_
* `lxml`_
* `SQLite3`_

Process
-------

The TACL suite of tools operates on a corpus of texts via an analysis
of their `n-grams`_. There are several steps in the preparation and
analysis of the corpus:

1. Preprocess the texts in the corpus in order to remove material
   that is not relevant to the analysis (the ``tacl strip``
   command). This creates modified files in a separate directory,
   and it is this directory and these files that are the considered
   the corpus for the remaining steps.
2. Generate the n-grams that will be used in the analysis (``tacl
   ngrams``). This is the slowest part of the entire process.
3. Categorise some or all of the texts in the corpus into two or more
   groups. These groups (identified by arbitrary, user-chosen labels)
   are defined in a catalogue file that is initially generated from
   the corpus (``tacl catalogue``).

   The catalogue file lists each filename (no path information) on its
   own line, followed optionally by whitespace and the label. If the
   label contains a space, it must be quoted.

   Texts that have no label are not used in an analysis.
4. Analyse the n-grams to find either the difference between (``tacl
   diff``) or intersection of (``tacl intersect``) the groups of texts
   as defined in a catalogue file.
5. Optionally perform functions on the results of a difference or
   intersection query, to limit the scope of the results (``tacl
   report``).

Another script, ``tacl-helper``, can be used to create sets of
catalogue files and prepare batches of commands for particular sets of
queries.


.. _Python 3: http://www.python.org/
.. _lxml: http://lxml.de/
.. _SQLite3: http://www.sqlite.org/
.. _n-grams: http://en.wikipedia.org/wiki/N-gram
