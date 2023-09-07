#!/bin/bash

# Unit test to see if the file or schema is compatible with the code
output=$(python3 ../../../src/python/comparison_file_check.py results-6.json)

if [[ "$output" == *"Compatible schema"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi