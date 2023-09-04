#!/bin/bash

output=$(python3 ../../../src/python/main.py 2.14 9 results-1.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi








