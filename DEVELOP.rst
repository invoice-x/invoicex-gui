Development
===========

If you are looking to get involved improving ``invoicex-gui``, this
guide will help you get started quickly.

Development Guide
-----------------

1. Fork the `main repository <https://github.com/invoice-x/invoicex-gui>`_. Click on the 'Fork' button near the top of the page. This creates a copy of the code under your account on the GitHub server. (optional)

2. Clone this copy to your local disk: 

::

	$ git clone https://github.com/invoice-x/invoicex-gui
	$ cd invoicex-gui

3. Create a branch to hold your changes and start making changes. Don't work on ``master`` branch

::

	$ git checkout -b my_enhancement

4. Send Pull Request to ``dev`` branch of this repository

5. If the Pull Request is merged and is found out to be stable it will be merged to `master branch <https://github.com/invoice-x/invoicex-gui>`_

Build
-----
To build executable read `this <https://github.com/invoice-x/invoicex-gui/blob/master/bin/>`_

Organization
------------

Major folders in the ``invoicex`` package and their purpose:

-  ``factur-x``: Customised verison of `Factur-X <https://github.com/invoice-x/factur-x>`_ library.
-  ``icons``: Icons used in this application.

Major files:

- ``invoicex.py``: Contains core code for ``invoicex-gui``
- ``populate.py``: Has code to integrate `invoice2data <https://github.com/invoice-x/factur-x>`_ with this application.
