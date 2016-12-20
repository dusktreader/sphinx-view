Quickstart
==========

Requirements
------------

* Python 3.5

Note on Requirements
....................

I do not currently plan to support python 2. The original author is a die-hard
believer in python 3, and has plenty of more interesting hobbies than getting
this package to work in python 3 as well. As for older versions of python 3, I
plan to eventually add support going back no farther than python 3.3

Installation
------------

Install from pypi
.................
This will install the latest release of flask-praetorian from pypi via pip::

$ pip install sphinx-view

Install latest version from github
..................................
If you would like a version other than the latest published on pypi, you may
do so by cloning the git repostiory::

$ git clone https://github.com/dusktreader/sphinx-view.git

Next, checkout the branch or tag that you wish to use::

$ cd sphinx-view
$ git checkout integration

Finally, use pip to install from the local directory::

$ pip install .

.. note::

    sphinx-view does not support distutils or setuptools because the
    author has very strong feelings about python packaging and the role pip
    plays in taking us into a bright new future of standardized and usable
    python packaging

View a single document
----------------------
Just execute ``sphinx-view`` targeting the file you wish to view in a browser::

$ sphinx-view README.rst

A new page will open in your browser showing the html rendered document.

sphinx-view will automatically refresh the browser if you make any changes to
the document, so you can view the file as you edit it.

View a directory
----------------
This feature is most useful for looking at the rendered version of docs for a
python package. Simply target the directory with ``spinx-view`` and everything
should just work::

$ sphinx-view docs

For a directory, ``sphinx-view`` will watch for changes to any of the files
and update the browser with new changes
