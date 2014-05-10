TACL
====

tacl is a tool for performing basic text analysis on the texts
available from the `Chinese Buddhist Electronic Text Association`_
(CBETA). It is largely generic, however, and can operate with minor
modifications on other corpora.

The code is developed at https://github.com/ajenhl/tacl/ and the
documentation is available at http://tacl.readthedocs.org/en/latest/ -
Read the Docs unfortunately does not display the script usage
documentation, but running the commands under `Usage` below gives the
same information.


Installation
------------

Using `Python 3`_ (minimum version 3.3), run ``python setup.py
install``. Requires `SQLite`_, the `lxml`_ XML library and the
`pandas`_ data analysis library.


Usage
-----

Run ``tacl -h`` for a listing of available subcommands, and ``tacl
<subcommand> -h`` for help on a specific subcommand.


.. _Chinese Buddhist Electronic Text Association: http://www.cbeta.org/
.. _Python 3: http://www.python.org/
.. _SQLite: http://www.sqlite.org/
.. _lxml: http://lxml.de/
.. _pandas: http://pandas.pydata.org/
