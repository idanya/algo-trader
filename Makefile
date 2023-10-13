.PHONY: test test-integration lint
SHELL = /bin/bash

test:
	pytest tests/unit --cov --cov-report term --cov-report xml:coverage.xml --junit-xml=report.xml

test-integration:
	pytest tests/integration --cov --cov-report term --cov-report xml:coverage.xml --junit-xml=report.xml

lint:
	flake8 src/ tests/ --count --show-source --statistics