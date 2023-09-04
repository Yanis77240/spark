#!/bin/bash

output=$(python3 ../../../src/python/main.py 2.20 22 results-187.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi








