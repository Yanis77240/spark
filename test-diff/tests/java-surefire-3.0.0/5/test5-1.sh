#!/bin/bash

output=$(python3 ../../../src/python/main.py 3.0.0 5 results-4.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi



