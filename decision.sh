#!/bin/bash

# If the file comparison.json is empty, it means that no new errors appear compared to the previous run and the pipeline stops, otherwise everuthing is ok.

file="comparison.csv"

if [ -s "$file" ]; then # if the file is not empty
    echo "There are new errors compared to the the comparison run."
    exit 1  # Exit with an error code
else
    echo "No new errors in the tests."
    # Continues the pipeline
fi
