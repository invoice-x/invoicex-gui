PROJECT := invoicex
TESTDIR := invoicex/tests

.PHONY: tests clean requirements linux windows macos help  

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
	-rm -rf .pytest_cache
	-rm -rf build/
	-rm -rf .load
	-rm -rf *.egg-info
	-rm -rf dist/

requirements:
	pip install -r requirements.txt
	pip install pytest

tests:
	py.test $(TESTDIR)

linux: clean requirements tests
	pyinstaller --clean bin/invoicex_linux.spec

windows: clean requirements tests
	pyinstaller --clean bin/invoicex_windows.spec

macos: clean requirements tests
	pyinstaller --clean bin/invoicex_macos.spec

help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "    clean         to clean up necessary files and remove build and dist files"
	@echo "    tests         to run tests"
	@echo "    requirements  to install requirements"
	@echo "    linux         build executable for linux distros"
	@echo "    windows       build executable for Windows"
	@echo "    macos         build executable for MacOS"