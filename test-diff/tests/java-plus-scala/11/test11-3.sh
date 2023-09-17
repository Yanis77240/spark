#!/bin/bash

# Unit test to see if the file or schema is compatible with the code
output=$(python3 ../../../src/python/comparison_file_check.py results-11.html)

if [[ "$output" == *"Compatible schema"* ]]; then
    echo "Assertion failed."
else
    echo "Assertion succeeded."
fi