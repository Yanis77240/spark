#!/bin/bash

output=$(python3 ../../main.py 3 results-1.json)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi



