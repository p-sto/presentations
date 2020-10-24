PWD:=$(shell pwd)
PYTHONPATH=$(PWD)
VENV=venv/bin
PIP=$(VENV)/pip3
PIP_FLAGS=--trusted-host=http://pypi.python.org/simple/
PYTHON_VERSION=python3.7

.PHONY: all venv

all: venv

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv -p $(PYTHON_VERSION) venv
	$(PIP) $(PIP_FLAGS) install -Ur requirements.txt
	touch venv/bin/activate
