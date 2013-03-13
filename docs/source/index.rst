.. TACL documentation master file, created by
   sphinx-quickstart on Sun Sep 30 19:40:33 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TACL's documentation!
================================

Contents:

.. toctree::
   :maxdepth: 1

   installation
   scripts/tacl
   scripts/tacl-helper


Introduction
------------

TACL is a tool for performing basic text analysis on a corpus of
texts. It can, with minor modifications, be used for any texts, though
it is designed specifically for the texts available from the `Chinese
Buddhist Electronic Text Association`_ (CBETA).

The basis of the analysis it enables is to divide up the corpus texts
into their consistuent `n-grams`_, and allow querying for the
differences and intersections of these n-grams between arbitrary
groupings of texts.


Process
-------

The TACL suite of tools operates on a corpus of texts via an analysis
of their `n-grams`_. There are several steps in the preparation and
analysis of the corpus:

1. Preprocess the texts in the corpus in order to remove material that
   is not relevant to the analysis (the :doc:`tacl strip
   </scripts/tacl-strip>` command). This creates modified files in a
   separate directory, and it is this directory and these files that
   are the considered the corpus for the remaining steps.
2. Generate the n-grams that will be used in the analysis (:doc:`tacl
   ngrams </scripts/tacl-ngrams>`). This is the slowest part of the
   entire process.
3. Categorise some or all of the texts in the corpus into two or more
   groups. These groups (identified by arbitrary, user-chosen labels)
   are defined in a catalogue file that is initially generated from
   the corpus (:doc:`tacl catalogue </scripts/tacl-catalogue>`).

   The catalogue file lists each filename (no path information) on its
   own line, followed optionally by whitespace and the label. If the
   label contains a space, it must be quoted.

   Texts that have no label are not used in an analysis.
4. Analyse the n-grams to find either the difference between
   (:doc:`tacl diff <scripts/tacl-diff>`) or intersection of
   (:doc:`tacl intersect </scripts/tacl-intersect>`) the groups of
   texts as defined in a catalogue file.
5. Optionally perform functions on the results of a difference or
   intersection query, to limit the scope of the results (:doc:`tacl
   report </scripts/tacl-report>`).

Another script, :doc:`tacl-helper </scripts/tacl-helper>`, can be used
to create sets of catalogue files and prepare batches of commands for
particular sets of queries.


.. _Chinese Buddhist Electronic Text Association: http://www.cbeta.org/
.. _n-grams: http://en.wikipedia.org/wiki/N-gram
