#!/bin/bash

# Unit test to see if the file or schema is compatible with the code
output=$(python3 ../../comparison-file-check.py results-3.json)

if [[ "$output" == *"Compatible schema"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi