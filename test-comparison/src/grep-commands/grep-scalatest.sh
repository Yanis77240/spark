#!/bin/bash

# Generate text file with all failed scala tests without any colors
grep -F --color=never --no-group-separator "*** FAILED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test-comparison/scala-tests.txt

# Generate text file with all Aborted modules without any colors
grep -E --color=never --no-group-separator "*** RUN ABORTED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test-comparison/aborted-tests.txt

# Generate text file with all scala test statistics without any colors
grep -E --color=never --no-group-separator "succeeded.*canceled.*ignored" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test-comparison/scala-end-results.txt