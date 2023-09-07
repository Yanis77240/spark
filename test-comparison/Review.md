# Test comparison function

When launching in Maven the mvn test command, often tests fail for which no patch has yet been provided. However, you do not want to simply use the --fail-never argument since some important tests might fail which shouldn't happen.

The function below allows the user to compare failed tests of the current run with a list of failed test specified in json file located in an external repository. If one or several more tests fail the pipeline will break at the test phase, otherwise it will continue to the next stage in the pipeline.

## Scope of the function

The following function works only when Maven runs tests executed by the surefire plugin which are tests written in Java as well as Scala-tests executed by the scalatest plugin and where the output display has the same style as the maven-surefire-plugin version 2.14.1, 2.20.0 or 3.0.0M.

The Python functions work with Python >= 3.6. The code varies a little wether you use Python 3.6 or a version superior to 3.9. Go to the `scala_tranformer.py` and concerning the setting of `None` values for missing values and the boolean transformation of the `aborted` column, uncomment the instructions for the Python version you have and comment the other one. The tdp-builder image uses python 3.6 so the corresponding instructions are used if not modified.

## How to integrate the function into the project

1. Paste the folder `test-comparison` at the root of the project in the github repository.

2. In the Jenkinsfile, add the two following stages:

```groovy
stage('Chose comparison') {
    withEnv(["file=${input message: 'Select file in http://10.10.10.11:30000/path_to_the_project_results_directory/', parameters: [string('number of results file')]}"]) {
        withEnv(["number=${currentBuild.number}"]) {
            sh '''
            cd test-comparison
            curl -v http://path_to_the_project_results_directory/${file} > ${file}
            python3 src/python/comparison_file_check.py ${file}
            echo "python3 src/python/main.py {surefire-version} ${number} ${file}" > transformation.sh
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
            /*sh '''
            mvn clean test [-options] --fail-never -Dstyle.color=never | tee output.txt
            '''*/
            /*sh 'mvn surefire-report:report-only  -Daggregate=true'
            sh 'curl -v -u $user:$pass --upload-file target/site/surefire-report.html http://path_to_reporting_directory/surefire-report-${number}.html'
            /* extract the java-test and scalatest-plugin data output and remove all color signs */
            sh'./test-comparison/src/grep-commands/grep-surefire-{version}.sh'
            /*sh'./test-comparison/src/grep-commands/grep-scalatest.sh'*/
            /* Perform the data transformation and the comparison*/
            sh '''
            cd test-comparison
            ./transformation.sh
            ./src/decision.sh ${number}
            curl -v -u $user:$pass --upload-file results-${number}.json http://path_to_the_project_results_directory/results-${number}.json
            '''
        }
    }
}
```

3. Set the path `http://path_to_the_project_results_directory/` in these two stages.

**Note:** You need to put the Nexus service IP in the stages since Jenkins and the builder pod access the repository inside the K8s cluster, however to access Nexus from outside of the cluster (To browse or upload files) you need the cluster IP and its associated Node port for the Nexus service.

4. In the command `echo "python3 src/python/main.py {surefire-version} ${number} ${file}" > transformation.sh`, set the `{surefire-version}`. Chose between `2.14`, `2.20` and `3.0.0`.

5. In the testing stage set the `[-options]` for the Maven test command if necessary

6. Not mandatory but if you want to add a reporting function you can add the maven-surefire-report-plugin command after the Maven test command:

```groovy
sh 'mvn surefire-report:report-only  -Daggregate=true'
sh 'curl -v -u $user:$pass --upload-file target/site/surefire-report.html http://path_to_reporting_directory/surefire-report-${number}.html'
```
**Note:** You need to have the maven-surefire-report-plugin in your project. If you do not have it, you need to set the plugin in the pom.xml. Also do not forget to set the path `path_to_reporting_directory`.

7. Put the adequate surefire version grep command file

8. If you have scalatests comment out the command `sh'./test-comparison/src/grep-commands/grep-scalatest.sh'`

9. In the `decision.sh` script, Set the path to the test comparison folder in the external repository.