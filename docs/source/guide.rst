Guide to TACL
=============

Works and witnesses
-------------------

TACL operates on named works, each of which consists of one or more
plain text files. These files are stored in subdirectories (named
after the work) of the corpus directory. The work name is what is used
in catalogue files, and referenced in the "work" field in query
results.

Every work consists of one or more witnesses, each a file in the
work's subdirectory. The filename of each witness (minus the .txt
extension) is referenced in query results in the "siglum" field.

Each witness consists of the full textual content of that witness. In
the case of the CBETA corpus, this full text is derived from the
marked up variant readings in the source TEI XML.

All witnesses are automatically included in a query when a work is
labelled in a catalogue.


Results
-------

TACL outputs query results in `comma-separated values`_ (CSV)
format. Each record (line) represents the occurrence of an
n-gram in a witness. The fields in the results are::

   ngram
      The n-gram that is present in the witness

   size
      The size (or degree) of the n-gram

   work
      The name of the work in which the n-gram was found

   siglum
      The identifier of the particular witness of the work that bears
      the n-gram

   count
      The number of times the n-gram occurs in the witness

   label
      The label that was assigned to the work in the catalogue file
      used in making the query


.. _comma-separated values: http://en.wikipedia.org/wiki/Comma-separated_values
