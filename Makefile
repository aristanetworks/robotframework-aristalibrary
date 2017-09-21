#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for AristaLibrary
#
# useful targets:
#	make sdist -- build python source distribution
#	make flake8 -- flake8 checks
#	make pep8 -- pep8 checks
#	make pyflakes -- pyflakes checks
#	make tests -- run all of the tests
#       make unittest -- runs the unit tests
#       make systest -- runs the system tests
#	make clean -- clean distutils
#	make docs -- build docs
#
########################################################
# variable section

NAME = "AristaLibrary"

PYTHON=python
SITELIB = $(shell $(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

VERSION := $(shell cat VERSION)

########################################################

all: clean flake8 pep8 pyflakes

flake8:
	flake8 --ignore=E501 AristaLibrary/

pep8:
	-pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 AristaLibrary/

pyflakes:
	pyflakes AristaLibrary/

clean:
	@echo "Cleaning up distutils stuff"
	rm -rf build
	rm -rf dist
	rm -rf MANIFEST
	rm -rf *.egg-info
	@echo "Cleaning up byte compiled python stuff"
	find . -type f -regex ".*\.py[co]$$" -delete

sdist: clean
	$(PYTHON) setup.py sdist

tests: unittest systest

unittest: clean
	$(PYTHON) -m unittest discover test/unit -v

systest: clean
	$(PYTHON) -m unittest discover test/system -v

docs:
	$(PYTHON) doc/generateHTML.py

travis: clean flake8 pep8 pyflakes
