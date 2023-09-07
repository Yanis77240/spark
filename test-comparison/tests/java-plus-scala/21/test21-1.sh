#!/bin/bash

output=$(python3 ../../../src/python/main.py 2.20 21 results-no-scala.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi








