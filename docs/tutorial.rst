Getting Started
===============

Browsing the archive by hand
----------------------------

You can browse the UDN archive by hand with a web browser at `the UDN website.`_
However, for doing more serious research, the web interface
can be lacking. For example, trying to browse examples of documents from a specific document
type would require opening multiple tabs by hand and searching through them.
You would need to track which documents you've already seen, and skip those
manually by browsing search results pages if you return to your research later. Instead, ``udn-nlp`` includes
scripts to streamline the browsing process.

``runscript view-docs docs/types/birth 5`` will open 5 documents of the
``birth`` type at a time, by creating new tabs in your web browser. You can
view and read those documents in the web viewer, then press ENTER in your
terminal when you're ready for 5 more. The ``view-docs`` script also allows you to skip documents you've already seen by providing a starting index as a second argument.

If you intend to use UDN documents as research material for any serious
projects, we recommend installing Zotero to make keeping lists of important
documents you've referenced. There is also an experimental script, ``cite``,
that can generate an API citation for a document, although you'll want to
verify that its result is correct.

.. _the UDN website.: https://digitalnewspapers.org

Building a Corpus
-----------------

The main purpose of this library is to construct corpora out of
related documents in the Utah Digital Newspapers archive. For example,
one of the example corpora in the [UDN Corpora repository](/udn-corpora/)
contains nearly every issue of the Heartitorium advice column
which first appeared in the Salt Lake Telegram in 1917. It was created
by running the ``build-corpus.py`` script like so::

    # Mac/Linux command
    runscript build-corpus heartitorium docs/search/Heartitorium
    # Windows command
    python "scripts/build-corpus.py" heartitorium docs/search/Heartitorium

Try running this script for yourself. Notice that ``build-corpus`` prints
an estimate of the resulting file size for your corpus. Make sure you have
the space (and time to wait!) for building a corpus from your query.

Also notice that by default, ``build-corpus`` actually generates *two* corpora:
one that is filtered, and one that is unfiltered. Because the UDN archive
currently contains a high density of OCR errors, you'll usually only want to
run NLTK analysis on the filtered version, when contains annotations where
OCR errors have been redacted from the text.

``[3;15]`` indicates that three words totalling 15 characters have been redacted.

If you ever want to see the full original OCR of your corpus, search through the
``-unfiltered`` corpus that was generated. If you wish not to create an unfiltered
corpus, add the argument ``0`` at the end of your ``build-corpus`` command.

``build-corpus`` can generate all kinds of corpora from the UDN archive. Any
set of documents that can be represented by a UDN API query can be made into a corpus.
For example, one of the more depressing sample corpora in our repository was created
like so::

    # Mac/Linux command
    runscript build-corpus death docs/types/death
    # Windows command
    python "scripts/build-corpus.py" death docs/types/death

A more complete reference of the API queries you could use to build corpora
is available `here`_.

.. _here: https://api.lib.utah.edu/docs/udn-v1.html

Analyzing a corpus
------------------

TODO document open-corpus, collocations and concordances

TODO comment on avoiding bad data caused by redactions


Classifying documents
---------------------

TODO this is the next major feature planned for udn-nlp.