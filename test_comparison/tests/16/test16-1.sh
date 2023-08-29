#!/bin/bash

output=$(python3 ../../main.py 1 results-15.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi








