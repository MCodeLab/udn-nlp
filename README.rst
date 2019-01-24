README
======

Utilities for applying NLTK natural language processing to the Utah Digital Newspapers archive.

Setup (All systems)
-------------------

Remember to clone all submodules by running ``git submodule update --init``.

Setup (Mac/Linux)
-----------------

``python3`` must be available in your system PATH and ``setuptools`` must be installed. Run the following in your terminal::

    python3 -m pip install --upgrade pip setuptools wheel
    source functions.sh
    reinstall

Setup (Windows)
---------------

Ensure that the first ``python.exe`` in your system PATH is a valid installation of Python 3.
Run the following command from an administrator terminal::

    python setup.py install

Running the scripts (Mac & Linux)
---------------------------------

The ``functions.sh`` file contains useful commands for the bash terminal. Type ``source functions.sh`` to access them.

* ``reinstall``: Install the local version of the module code on your system.
* ``runscript``: Run one of the udn-nlp scripts (from the `scripts` directory).
    Will print usage guide if script's arguments are incorrect.
* ``dev_runscript``: For use when modifying modules and scripts at the same time.
    Guarantee that the latest version of the udn-nlp modules is installed before running a script.

Running the scripts (Windows)
-----------------------------

To make sure the latest version of the modules is installed, run `python setup.py install` from an administrator terminal.
To run one of the udn-nlp scripts, type `python "scripts/[scriptname].py" [args]` (no administrator privileges required).

Getting started
---------------

Once you have udn-nlp installed and know how to run scripts, see the `Getting Started`_ guide.

.. _Getting Started: docs/tutorial.html