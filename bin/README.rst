Building Execulatable
=====================

For building executable file we recommend using `pyinstaller <https://www.pyinstaller.org/>`_

Command
-------

::

    $ pip install pyinstaller
    $ pyinstaller invoicex_linux.spec

`invoicex_linux <invoicex_linux.spec>`_ is the spec to be used

You can also make your own spec file

::

    $ pyi-makespec \
          --onefile \
          --noconsole \
          --name="Invoice-X GUI" \
          --icon=../invoicex/icons/logo.ico \
          ../main.py
