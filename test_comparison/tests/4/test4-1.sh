#!/bin/bash

output=$(python3 ../../main.py 4 results-1.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi



