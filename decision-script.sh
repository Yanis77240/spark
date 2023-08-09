#!/bin/bash

# This scripts checks wether the last test run has errors which were not in the previous successful run and if it is the case drops all its tables and fails the pipeline

number=$1

if [ "$(mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e 'SELECT CASE WHEN EXISTS (SELECT 1 FROM comparison_aborted_'$number') THEN 0 ELSE 1 END INTO @passed_aborted; SELECT @passed_aborted;' -sN)" = 0 ]; then
    echo "Pipeline terminated due to an increase of aborted modules." >&2
    exit 1
elif [ "$(mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e 'SELECT CASE WHEN EXISTS (SELECT 1 FROM comparison_tests_'$number')  THEN 0 ELSE 1 END INTO @passed_tests; SELECT @passed_tests;' -sN)" = 0 ]; then
    echo "Pipeline terminated due to an increase of failed tests." >&2
    exit 1
elif [ "$(mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e 'SELECT COUNT(*) FROM test_list_'$number';' -sN)" -gt 600 ]; then
    echo "Pipeline terminated due to too many failed tests." >&2
    exit 1
else
    echo "No further Test errors and aborted modules than before"
fi