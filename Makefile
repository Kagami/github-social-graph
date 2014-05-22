VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
GSG=$(VENV)/bin/gsg

# Just to be sure what empty `make' command won't do anything unexpectable.
all:

env:
	virtualenv $(VENV)

clean-env:
	rm -rf $(VENV)

re-env: clean-env env

install-deps: env
	$(PIP) install -e .

clean c:
	rm -rf github_social_graph.egg-info

mrproper: clean clean-env
	find -name '*.pyc' -delete

t:
	$(GSG) -i 1.json -o - -of png | feh -F -
