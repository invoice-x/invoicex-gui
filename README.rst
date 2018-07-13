GUI for factur-x - Invoice-X GUI
================================
Graphical User Interface for `factur-x <https://github.com/invoice-x/factur-x>`_ library with basic functionalities such as:

- Validate Metadata
- Export Metadata to (json|xml|yml)
- Add xml to PDF
- Extract fields from PDF
- Edit Fields

The application is built using `PyQt5 <https://www.riverbankcomputing.com/software/pyqt/intro>`_

Requirements
------------

External Dependencies:

- Imagemagick
- GhostScript

Running
-------

::

    $ git clone https://github.com/invoice-x/invoicex-gui.git
    $ cd invoicex-gui
    $ pip install -r requirements.txt
    $ python main.py

OR run from terminal

::

    $ $ git clone https://github.com/invoice-x/invoicex-gui.git
    $ cd invoicex-gui
    $ python setup.py install
    $ invoicex-gui

Status
------

**The project is under development**

Working Features:

- Preview Loaded PDF
- Load metadata to right Dock
- Edit Fields
- Save PDF file
- Export Metadata (json|xml|yml)

.. image:: Screenshots/mainWindow.png

.. image:: Screenshots/editDialog.png

Author
------
- `Harshit Joshi <https://github.com/duskybomb>`_
