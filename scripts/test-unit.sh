#!/usr/bin/env bash
source test-setup.sh

coverage run --rcfile=../.coveragerc -m unittest discover -s ../tests/unit
coverage report -m