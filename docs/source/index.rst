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
   guide
   scripts/tacl
   scripts/tacl-jitc
   API <api/tacl>


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

The documentation here concentrates on the specifics of using
TACL. Michael Radich has written a `user's guide`_ that focuses on
"questions of Buddhological method bearing upon rigorous and effective
application of the tool to research questions".


Process
-------

The TACL suite of tools operates on a corpus of texts via an analysis
of their `n-grams`_. There are several steps in the preparation and
analysis of the corpus, as listed with example commands:

1. Preprocess the files in the corpus in order to remove material that
   is not relevant to the analysis (the :doc:`tacl prepare
   </scripts/tacl-prepare>` and :doc:`tacl strip
   </scripts/tacl-strip>` commands). This creates modified files in a
   separate directory, and it is this directory and these files that
   are the considered the corpus for the remaining steps. ::

       tacl prepare path/XML/dir path/prepared/dir
       tacl strip path/prepared/dir path/stripped/dir

   Note that the output format is simply plain text. If you already
   have plain text files, then this step is not necessary. The
   processing currently expects the style of TEI XML used by the CBETA
   corpus as per their `GitHub repository`_.

2. Generate the n-grams that will be used in the analysis (:doc:`tacl
   ngrams </scripts/tacl-ngrams>`). This is typically the slowest part
   of the entire process. ::

       tacl ngrams path/db/file path/stripped/dir 2 10

3. Categorise some or all of the works in the corpus into two or more
   groups. These groups (identified by arbitrary, user-chosen labels)
   are defined in a catalogue file that is initially generated from
   the corpus (:doc:`tacl catalogue </scripts/tacl-catalogue>`).

   The catalogue file lists each work on its own line, followed
   optionally by whitespace and the label. If the label contains a
   space, it must be quoted.

   Works that have no label are not used in an analysis. ::

       tacl catalogue -l "base" path/stripped/dir path/catalogue/file

   An example catalogue: ::

       T0237 Vaj
       T0097 AV
       T0667 P-ref
       T1461 P-ref
       T1559
       T2137

4. Analyse the n-grams to find either the difference between
   (:doc:`tacl diff <scripts/tacl-diff>`) or intersection of
   (:doc:`tacl intersect </scripts/tacl-intersect>`) the groups of
   works as defined in a catalogue file. ::

       tacl diff path/db/file path/stripped/dir path/catalogue/file > diff-results.csv

       tacl intersect path/db/file path/stripped/dir path/catalogue/file > intersect-results.csv

5. Optionally perform functions on the results of a difference or
   intersection query, to limit the scope of the results (:doc:`tacl
   results </scripts/tacl-results>`). ::

       tacl results --reduce --min-count 5 diff-results.csv > reduced-diff-results.csv

6. Display a side by side comparison of matching parts of pairs of
   texts in a set of intersection query results (:doc:`tacl align
   </scripts/tacl-align>`). ::

       tacl align path/stripped/dir path/output/dir intersect-results.csv

7. Display one text with the option to highlight matches from other
   texts in a set of intersection query results, producing a heatmap
   visualisation (:doc:`tacl highlight </scripts/tacl-highlight>`). ::

       tacl highlight path/stripped/dir intersect-results.csv text-name witness-siglum

Other tacl commands can be found using the command `tacl -h` or
reading the documentation for the :doc:`tacl </scripts/tacl>` script.

Those wishing to do sophisticated operations with catalogues may wish
to install `tacl-catalogue-manager`_.


.. _Chinese Buddhist Electronic Text Association: http://www.cbeta.org/
.. _n-grams: http://en.wikipedia.org/wiki/N-gram
.. _user's guide: http://dazangthings.nz/documents/3/TACL_users_guide.pdf
.. _GitHub repository: https://github.com/cbeta-org/xml-p5.git
.. _tacl-catalogue-manager: https://github.com/ajenhl/tacl-catalogue-manager
