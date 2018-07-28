# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path


setup(
    name='invoicex-gui',
    version='0.0.6',
    author='Harshit Joshi',
    author_email='harshit.joshi@outlook.com',
    url='https://github.com/invoice-x/invoicex-gui',
    description='Graphical User Interface for factur-x library with basic functionalities',
    license="GNU General Public License (GPL)",
    long_description=open(path.join(path.dirname(__file__), 'README.rst')).read(),
    package_data = {
        'invoicex.facturx.flavors': [
            '*.yml',
            'factur-x/xml/*.xml',
            'factur-x/xmp/*.xmp',
            'factur-x/xsd/*.xsd',
            'zugferd/xml/*.xml',
            'zugferd/xmp/*.xmp',
            'zugferd/xsd/*.xsd',
           ],
        'invoicex':['icons/*.png']
        },
    packages=find_packages(),
    install_requires=[
        r.strip() for r in open(
            path.join(path.dirname(__file__), 'requirements.txt')
                ).read().splitlines() if not r.startswith('#')
        ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'invoicex-gui = invoicex.invoicex:main',
        ]
    }
)