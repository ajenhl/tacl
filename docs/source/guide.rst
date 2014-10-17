Guide to TACL
=============

Texts and witnesses
-------------------

TACL operates on named texts, each of which consists of one or more
plain text files. These files are stored in subdirectories (named
after the text) of the corpus directory. The text name is what is used
in catalogue files, and referenced in the "text name" field in query
results.

Every text consists of one or more witnesses, each a file in the
text's subdirectory. The filename of each witness (minus the .txt
extension) is referenced in query results in the "siglum" field.

Each witness consists of the full textual content of that witness. In
the case of the CBETA corpus, this full text is derived from the
marked up variant readings in the source TEI XML.

All witnesses are automatically included in a query when a text is
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

   text name
      The name of the text in which the n-gram was found

   siglum
      The identifier of the particular witness of the text that bears
      the n-gram

   count
      The number of times the n-gram occurs in the witness

   label
      The label that was assigned to the text in the catalogue file
      used in making the query


.. _comma-separated values: http://en.wikipedia.org/wiki/Comma-separated_values
