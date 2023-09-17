#!/bin/bash

output=$(python3 ../../../src/python/main.py 2.20 1 0)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi








