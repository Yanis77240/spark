#!/bin/bash

output=$(python3 ../../main.py 1 0)

if [[ "$output" == *"Comparison succeeded"* ]]; then
    echo "Assertion succeeded."
else
    echo "Assertion failed."
fi








