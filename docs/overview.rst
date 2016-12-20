Overview
========

If you've ever done much work with Sphinx (or any ReStructuredText) documents,
you know how important it is to regularly check how they look when rendered
into html. Often, you get your formatting wrong or introduce a syntax error.
Constantly running sphinx-build by hand is really annoying.

There is a very nice tool called `restview <https://github.com/mgedmin/restview>`_
that can be used to view ReStructuredText files, but it doesn't support all the
sphinx keywords and features. Furthermore, it doesn't render with a style

The sphinx-view application automatically renders the documents using the
'alabaster' theme. It renders them using Sphinx itself. It is even capable of
rendering an entire directory at once and producing a full html page with
navigation between sub-pages. This is very handy if, for instance, you are
editing the ``docs`` folder of a python project.

In addition, sphinx-view will watch for changes to the documents, rebuild the
pages, and refresh the browser any time you save the documents you are viewing.
