#!/bin/bash

# Create CVS file with following titles as header
echo "Tests_run, Failures, Errors, Skipped, Test_group" > test-comparison/output-tests.csv

# Grep all Java test staistics in CSV file
grep -E --color=never '(Failures:.*Errors:.*Skipped:.*Time elapsed:)' output.txt >> test-comparison/output-tests.csv

# Generate text file with all failed Java tests without any colors
grep -E --color=never '[Error].*org.*<<< ERROR!|[Error].*org.*<<< FAILURE!' output.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test-comparison/java-test-failures.txt