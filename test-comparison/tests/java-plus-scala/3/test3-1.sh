#!/bin/bash

output=$(python3 ../../../src/python/main.py 2.20 3 results-1.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi



