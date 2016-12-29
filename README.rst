.. image::  https://badge.fury.io/py/sphinx-view.svg
   :target: https://badge.fury.io/py/sphinx-view
   :alt:    Latest Published Version

.. image::  https://travis-ci.org/dusktreader/py-buzz.svg?branch=integration
   :target: https://travis-ci.org/dusktreader/py-buzz
   :alt:    Build Status

.. image::  https://readthedocs.org/projects/sphinx-view/badge/?version=latest
   :target: http://sphinx-view.readthedocs.io/en/latest/?badge=latest
   :alt:    Documentation Build Status

*************
 sphinx-view
*************

---------------------------------------------------------------------
View your rendered Sphinx or ReStrucutredText documents in a browswer
---------------------------------------------------------------------

If you've ever done much work with Sphinx (or any ReStructuredText) documents,
you know how important it is to regularly check how they look when rendered
into html. Often, you get your formatting wrong or introduce a syntax error.
Constantly running sphinx-build by hand is really annoying.

There is a very nice tool called
`restview <https://github.com/mgedmin/restview>`_ that can be used to view
ReStructuredText files, but it doesn't support all the sphinx keywords and
features. Furthermore, it doesn't render with a style

The sphinx-view application automatically renders the documents using the
'alabaster' theme. It renders them using Sphinx itself. It is even capable of
rendering an entire directory at once and producing a full html page with
navigation between sub-pages. This is very handy if, for instance, you are
editing the ``docs`` folder of a python project.

In addition, sphinx-view will watch for changes to the documents, rebuild the
pages, and refresh the browser any time you save the documents you are viewing.

Super-quick Start
-----------------
 - requirements: `python3.5`
 - install through pip: `$ pip install sphinx-view`
 - view a document: `$ sphinx-view README.rst`

Full Documentation
------------------
 - `spinx-view documentation home <http://sphinx-view.readthedocs.io>`_
 - `raw reStructuredText docs
   <https://github.com/dusktreader/sphinx-view/tree/master/docs>`_
