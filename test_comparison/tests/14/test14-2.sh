#!/bin/bash

output=$(../../decision.sh)

if [ "$output" == "No new errors in the tests." ]; then
    echo "Assertion failed."
else
    echo "Assertion succeeded."
fi
