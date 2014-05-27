Installation
============

tacl is available on `PyPI`_ and so can be installed (along with its
Python dependencies) using `pip`_. If problems occur, see
https://github.com/ajenhl/tacl/wiki/Installation for alternative
instructions.

Requirements
------------

* `Python 3`_ (minimum version 3.3)
* `lxml`_
* `pandas`_
* `SQLite3`_
* `biopython`_

On Windows, Python is packaged with the SQLite3 DLL, so the latter
need not be installed separately.

``lxml`` is used in generating suitable text files from XML source
documents (such as those provided by CBETA).

``pandas`` is used to manipulate results.

``biopython`` is used in creating side by side display of aligned text
matches.


.. _PyPI: https://pypi.python.org/pypi/tacl
.. _pip: https://pypi.python.org/pypi/pip
.. _Python 3: http://www.python.org/
.. _lxml: http://lxml.de/
.. _pandas: http://pandas.pydata.org/
.. _SQLite3: http://www.sqlite.org/
.. _biopython: http://biopython.org/
