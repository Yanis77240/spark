#!/bin/bash

# Generate text file with all failed scala tests without any colors
grep -F --color=never --no-group-separator "*** FAILED ***" */target/surefire-reports/*TestSuite.txt */**/target/surefire-reports/*TestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test-diff/scala-tests.txt

# Generate text file with all Aborted modules without any colors
grep -o --color=never --no-group-separator "*** RUN ABORTED \*\*\*" */target/surefire-reports/*TestSuite.txt */**/target/surefire-reports/*TestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test-diff/aborted-tests.txt

# Generate text file with all scala test statistics without any colors
grep -E --color=never --no-group-separator "succeeded.*canceled.*ignored" */target/surefire-reports/*TestSuite.txt */**/target/surefire-reports/*TestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test-diff/scala-end-results.txt