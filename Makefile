SHELL=/bin/bash
PLATFORM=$(shell uname -s)

.PHONY: clean check deps run build testdeps

PYTHONPATH := PYTHONPATH=./:$$PYTHONPATH

CONDA_EXE=$(shell which conda)
ifeq ($(CONDA_EXE),)
	CONDA_PATH := $(HOME)/miniconda
	CONDA_EXE := $(CONDA_PATH)/bin/conda
else
	CONDA_PATH := $(shell dirname $(dir $(CONDA_EXE)))
endif

CONDA_ENV_PATH = ./conda_env
CONDA_ACTIVATE := source $(CONDA_PATH)/bin/activate $(CONDA_ENV_PATH)

PYBUILD_ARTEFACTS := ./build ./dist ./.cache ./.eggs

build: $(CONDA_ENV_PATH)

test: build
	$(CONDA_ACTIVATE) && $(PYTHONPATH) pytest -v --ignore $(CONDA_ENV_PATH)

pre-commit: build
	$(CONDA_ACTIVATE) && $(PYTHONPATH) pre-commit run --all-files

check: test pre-commit

ifeq ($(PLATFORM),Darwin)

CONDA_OS := MacOSX
BREWDEPS := coreutils autoconf libtool

deps:
	brew install $(BREWDEPS)


else ifeq ($(PLATFORM),Linux)

CONDA_OS := Linux

deps:
	sudo apt-get -yqq update
	sudo apt-get -yqq install bzip2 git wget

testdeps: deps
	sudo apt-get -yqq install openjdk-8-jdk

else

 $(error, Unknown platform)

endif

MINICONDA_URL := http://repo.continuum.io/miniconda/Miniconda3-latest-$(CONDA_OS)-x86_64.sh

$(CONDA_EXE):
	wget -q $(MINICONDA_URL) -O $(HOME)/miniconda.sh
	$(SHELL) $(HOME)/miniconda.sh -b -p $(HOME)/miniconda
	$(CONDA_EXE) install --yes boto3

$(CONDA_ENV_PATH): $(CONDA_EXE) environment.yml VERSION
	$(MAKE) clean
	$(CONDA_EXE) env create --file environment.yml --prefix $(CONDA_ENV_PATH)
	$(CONDA_ACTIVATE) && pre-commit install && python -m spacy download en

clean:
	rm -rf $(PYBUILD_ARTEFACTS)
	if test -d $(CONDA_ENV_PATH); then \
		$(CONDA_EXE) env remove --yes -p $(CONDA_ENV_PATH); \
	fi

