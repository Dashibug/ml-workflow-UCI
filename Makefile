# Invoke from the root of ml-workflow-UCI
.PHONY: hw1-test hw1-compare hw2-test hw2-repro hw2-status hw2-dag

hw1-test:
	cd HW-1 && python -m pytest -q

hw1-compare:
	cd HW-1 && python -m src.compare

hw2-test:
	cd HW-2 && python -m pytest -q

hw2-repro:
	dvc repro

hw2-status:
	dvc status

hw2-dag:
	dvc dag
