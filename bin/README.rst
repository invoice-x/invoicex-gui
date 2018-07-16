Building Executable
=====================

For building executable file we recommend using `pyinstaller <https://www.pyinstaller.org/>`_

Command
-------

::

    $ pip install pyinstaller
    $ pyinstaller invoicex_linux.spec

`invoicex_linux <invoicex_linux.spec>`_ is the spec to be used
`invoicex_windows <invoicex_windows.spec>`_ is the spec to be used

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

Make sure you have made changes to .spec file

Like:

- add _strptime.py to root from `usr/lib/python3/`
- change python version in `venv/lib/python3.6/../en.py`
