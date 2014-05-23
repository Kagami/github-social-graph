VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
PIP_VER=$(shell $(PIP) --version | cut -f2 -d' ')
PIP_VER_MAJOR=$(shell echo $(PIP_VER) | cut -f1 -d.)
PIP_VER_MINOR=$(shell echo $(PIP_VER) | cut -f2 -d.)
PIP_GE_1_5=$(shell [ $(PIP_VER_MAJOR) -gt 1 -o \( $(PIP_VER_MAJOR) -eq 1 -a $(PIP_VER_MINOR) -ge 5 \) ] && echo true)
GSG=$(VENV)/bin/gsg

# Just to be sure what empty `make' command won't do anything unexpectable.
all:

env:
	virtualenv $(VENV)

clean-env:
	rm -rf $(VENV)

re-env: clean-env env

install-deps: env
ifeq ($(PIP_GE_1_5),true)
	$(PIP) install --process-dependency-links -e .
else
	$(PIP) install -e .
endif

clean c:
	rm -rf github_social_graph.egg-info

mrproper: clean clean-env
	find -name '*.pyc' -delete

t:
	$(GSG) -i 1.json -o - -of png | feh -F -
