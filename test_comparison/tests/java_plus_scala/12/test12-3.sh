#!/bin/bash

# Unit test to see if the file or schema is compatible with the code
output=$(python3 ../../../src/python/comparison-file-check.py results-12.json)

if [[ "$output" == *"Compatible schema"* ]]; then
    echo "Assertion failed."
else
    echo "Assertion succeeded."
fi