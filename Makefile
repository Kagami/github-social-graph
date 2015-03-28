VENV=.venv
PIP=$(VENV)/bin/pip2
PIP3=$(VENV)/bin/pip3
GSG=$(VENV)/bin/python2 $(VENV)/bin/gsg
GSG3=$(VENV)/bin/python3 $(VENV)/bin/gsg

# Just to be sure that `make' command won't do anything unexpectable.
all:

env:
	virtualenv -p python2 $(VENV)
	virtualenv -p python3 $(VENV)

clean-env:
	rm -rf $(VENV)

re-env: clean-env env

install-deps: env
	$(PIP) install -e .
	$(PIP3) install -e .

clean c:
	rm -rf github_social_graph.egg-info

mrproper: clean clean-env
	find -name '*.pyc' -delete

t:
	$(GSG) -i 1.json -o 1.png

t3:
	$(GSG3) -i 1.json -o 1.png
