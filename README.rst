TACL
====

tacl is a tool for performing basic text analysis on the texts
available from the `Chinese Buddhist Electronic Text Association`_
(CBETA). It is largely generic, however, and can operate with minor
modifications on other corpora.

The code is developed at https://github.com/ajenhl/tacl/ and the
documentation is available at http://tacl.readthedocs.io/en/latest/.


Installation
------------

Using `Python 3`_ (minimum version 3.5), either run ``pip install
tacl`` or download the code manually and run ``python setup.py
install``. The dependencies are installed automatically when tacl is
installed with ``pip``. Note however that on Windows (and perhaps Mac
OS X) it is very likely that the dependencies that have non-Python
components will not build due to a missing compiler. In such a case,
follow the instructions at
https://github.com/ajenhl/tacl/wiki/Installation


Usage
-----

Run ``tacl -h`` for a listing of available subcommands, and ``tacl
<subcommand> -h`` for help on a specific subcommand.


.. _Chinese Buddhist Electronic Text Association: http://www.cbeta.org/
.. _Python 3: http://www.python.org/
.. _SQLite: http://www.sqlite.org/
.. _biopython: http://biopython.org/
.. _lxml: http://lxml.de/
.. _pandas: http://pandas.pydata.org/
