PYTHON ?= python

.PHONY: install install-dev data baseline experiment compare test all clean

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

data:
	$(PYTHON) -m src.prepare_data

baseline:
	$(PYTHON) -m src.train --config configs/baseline.yaml

experiment:
	$(PYTHON) -m src.train --config configs/experiment.yaml

compare:
	$(PYTHON) -m src.compare

test:
	$(PYTHON) -m pytest -q

all: data baseline experiment compare

clean:
	@echo "To remove local data and artifacts, delete data/raw/, data/processed/, artifacts/ manually."
