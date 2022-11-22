#!/usr/bin/env bash
flake8 $( dirname -- "$0"; )/../ --count --show-source --statistics