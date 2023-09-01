# Test comparison function

When launching in Maven the mvn test command, often tests fail for which no patch has yet been provided. However, you do not want to simply use the --fail-never argument since some important tests might fail which shouldn't happen.

The function below allows the user to compare failed tests of the current run with a list of failed test specified in json file located in an external repository. If one or several more tests fail the pipeline will break at the test phase, otherwise it will continue to the next stage in the pipeline.

## Scope of the function

The following function works only when Maven runs tests executed by the surefire plugin which are tests written in Java as well as Scala-tests executed by the scalatest plugin and where the output display has the same style as the maven-surefire-plugin version 2.21.0. Older versions such as 2.14.1 have got another output display and an adapted version of this function must be used.

## How to integrate the function into the project

1. Paste the folder `test_comparison` at the root of the project in the github repository.

2. In the Jenkinsfile, add the two following stages:

```groovy
stage('Chose comparison') {
    withEnv(["file=${input message: 'Select file in http://10.10.10.11:30000/repository/java-test-reports/', parameters: [string('number of results file')]}"]) {
        withEnv(["number=${currentBuild.number}"]) {
            sh '''
            cd test_comparison
            curl -v http://path_to_the_project_results_directory/${file} > ${file}
            python3 comparison-file-check.py ${file}
            echo "python3 main.py ${number} ${file}" > transformation.sh
            chmod 777 transformation.sh
            '''
        }
    }
}
```

and

```groovy
stage('Test') {
    echo "Testing..."
    withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
        withEnv(["number=${currentBuild.number}"]) {
            /* Perform the tests and the surefire reporting*/
            sh '''
            mvn clean test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume --batch-mode --fail-never -Dstyle.color=never | tee output.txt
            '''
            /* extract the scalatest-plugin data and java-test data output and remove all color signs */
            sh script: $/
            # Generate text file with all failed scala tests without any colors
            grep -F --color=never --no-group-separator "*** FAILED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test_comparison/scala-tests.txt
            # Generate text file with all Aborted modules without any colors
            grep -E --color=never --no-group-separator "*** RUN ABORTED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test_comparison/aborted-tests.txt
            # Generate text file with all scala test statistics without any colors
            grep -E --color=never --no-group-separator "succeeded.*canceled.*ignored" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test_comparison/scala-end-results.txt
            # Create CVS file with following titles as header
            echo "Tests_run, Failures, Errors, Skipped, Test_group" > test_comparison/output-tests.csv
            # Grep all Java test statistics in CSV file
            grep -E --color=never '(Failures:.*Errors:.*Skipped:.*Time elapsed:)' output.txt >> test_comparison/output-tests.csv
            # Generate text file with all failed Java tests without any colors
            grep -E --color=never '[Error].*org.*<<< ERROR!|[Error].*org.*<<< FAILURE!' output.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test_comparison/java-test-failures.txt
            /$
            /* Perform the data transformation and the comparison*/
            sh '''
            cd test_comparison
            ./transformation.sh
            ./decision.sh ${number}
            curl -v -u $user:$pass --upload-file results-${number}.json http://path_to_the_project_results_directory/results-${number}.json
            '''
        }
    }
}
```

3. Set the path `http://path_to_the_project_results_directory/` in these two stages.

4. In the testing stage set the `[-options]` for the Maven test command if necessary

5. Not mandatory but if you want to add a reporting function you can add the maven-surefire-report-plugin command after the Maven test command:

```groovy
sh 'mvn surefire-report:report-only  -Daggregate=true'
sh 'curl -v -u $user:$pass --upload-file target/site/surefire-report.html http://path_to_reporting_directory/surefire-report-${number}.html'
```
**Note:** You need to have the maven-surefire-report-plugin in your project. If you do not have it, you need to set the plugin in the pom.xml. Also do not forget to set the path `path_to_reporting_directory`.

6. In the `decision.sh` script, Set the path to the test comparison folder in the external repository.