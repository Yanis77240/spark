#!/bin/bash

number=$1

if [ "$(mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e 'SELECT CASE WHEN EXISTS (SELECT 1 FROM comparison_'$number') THEN 0 ELSE 1 END INTO @passed; SELECT @passed;' -sN)" = 0 ]; then
    mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e "DROP TABLE test_list_${number}, aborted_tests_${number}, results_${number}, comparison_${number};"
    echo "Pipeline terminated due to an increase of failed tests." >&2
    exit 1
else
    echo "No further Test errors than before"
fi

