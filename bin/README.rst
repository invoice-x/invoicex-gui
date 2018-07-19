Building Executable
=====================

For building executable file we recommend using `pyinstaller <https://www.pyinstaller.org/>`_

Command
-------

::

    $ pip install pyinstaller
    $ pyinstaller invoicex_linux.spec

`invoicex_linux <https://github.com/invoice-x/invoicex-gui/blob/master/bin/invoicex_linux.spec>`_ is the spec to be used

`invoicex_windows <https://github.com/invoice-x/invoicex-gui/blob/master/bin/invoicex_windows.spec>`_ is the spec to be used

You can also make your own spec file

::

    $ pyi-makespec \
          --onefile \
          --noconsole \
          --name="Invoice-X GUI" \
          --icon=../invoicex/icons/logo.ico \
          ../main.py

Note
----

Files, ``_strptime.py`` and ``en.py`` are there for pyinstaller to discover
