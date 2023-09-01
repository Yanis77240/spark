#!/bin/bash

# If the file comparison.json is empty, it means that no new errors appear compared to the previous run and the pipeline stops, otherwise everuthing is ok.

build_number=$1  # First argument passed to the script

file="comparison.csv"

if [ -s "$file" ]; then # if the file is not empty
    echo "There are new errors compared to the comparison run."
    # we send the list with the additional errors to the nexus repository
    curl -v -u $user:$pass --upload-file "$file" http://10.10.10.11:30000/repository/scala-test-comparison/spark/comparison-"$build_number".csv # Set the path to the test comparison folder in the external repository.
    exit 1  # Exit with an error code
else
    echo "No new errors in the tests."
    # Continues the pipeline
fi
