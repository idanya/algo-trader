.PHONY: test test-integration lint
SHELL = /bin/bash

test:
	pytest tests/unit --cov --cov-report term --cov-report xml:coverage.xml --junit-xml=report.xml

test-integration:
	pytest tests/integration --cov --cov-report term --cov-report xml:coverage.xml --junit-xml=report.xml

lint:
	ruff ./src/ ./tests/
	black ./src/ ./tests/ --check
	#pyright ./src/ ./tests/

reformat:
	black ./src/ ./tests/
	ruff ./src/ ./tests/ --fix
