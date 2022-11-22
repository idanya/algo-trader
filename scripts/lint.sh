#!/usr/bin/env bash
flake8 $( dirname -- "$0"; )/../src --count --show-source --statistics