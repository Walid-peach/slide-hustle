PYTHON ?= .venv/bin/python

.PHONY: setup example generate export compare clean-output

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m playwright install chromium

generate:
	$(PYTHON) generate.py briefs/_template.yaml

export:
	$(PYTHON) export.py output/slide_hustle_example/slides.html

example: generate export

compare:
	$(PYTHON) compare_reference.py $(REFERENCE) output/slide_hustle_example

clean-output:
	rm -rf output/*
	touch output/.gitkeep
