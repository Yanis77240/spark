podTemplate(containers: [
    containerTemplate(
        name: 'tdp-builder', 
        image: 'stbaum/jenkins-mysql',
        resourceLimitCpu: "3000m",
        resourceLimitMemory: "10000Mi", 
        command: 'sleep', 
        args: '30d'
        )
]) {

    node(POD_LABEL) {
        container('tdp-builder') {
            stage('Git Clone') {
                echo "Cloning..."
                git branch: 'branch-2.3-TDP-alliage-k8s', url: 'https://github.com/Yanis77240/spark'
            }
            stage('Chose comparison') {
                withEnv(["file=${input message: 'Select file in http://10.10.10.11:30000/repository/scala-test-reports/', parameters: [string('number of results file')]}"]) {
                    withEnv(["number=${currentBuild.number}"]) {
                        sh '''
                        cd test_comparison
                        curl -v http://10.10.10.11:30000/repository/scala-test-reports/spark/${file} > ${file}
                        python3 comparison-file-check.py ${file}
                        echo "python3 main.py ${number} ${file}" > transformation.sh
                        chmod 777 transformation.sh
                        '''
                    }
                }
            }
            stage('Build') {
                echo "Building..."
                sh '''
                ./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume -Dstyle.color=never
                '''
            }
            stage('Test') {
                echo "Testing..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    withEnv(["number=${currentBuild.number}"]) {
                        /* Perform the tests and the surefire reporting*/
                        sh '''
                        mvn clean test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume --batch-mode --fail-never -Dstyle.color=never | tee output.txt
                        '''
                        /*sh 'mvn surefire-report:report-only  -Daggregate=true'
                        sh 'curl -v -u $user:$pass --upload-file target/site/surefire-report.html http://10.110.4.212:8081/repository/test-reports/spark-2.3/surefire-report-${number}.html'
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
                        # Grep all Java test staistics in CSV file
                        grep -E --color=never '(Failures:.*Errors:.*Skipped:.*Time elapsed:)' output.txt >> test_comparison/output-tests.csv
                        # Generate text file with all failed Java tests without any colors
                        grep -E --color=never '[Error].*org.*<<< ERROR!|[Error].*org.*<<< FAILURE!' output.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > test_comparison/java-test-failures.txt
                        /$
                        /* Perform the data transformation and the comparison*/
                        sh '''
                        cd test_comparison
                        ./transformation.sh
                        ./decision.sh ${number}
                        curl -v -u $user:$pass --upload-file results-${number}.json http://10.110.4.212:8081/repository/scala-test-reports/spark/results-${number}.json
                        '''
                    }
                }
            }
            stage('Deliver') {
                echo "Deploy..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh './dev/make-deployment.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume -Dstyle.color=never -s settings.xml'
                }
            }
            stage("Publish tar.gz to Nexus") {
                echo "Publish tar.gz..."
                withEnv(["number=${currentBuild.number}"]) {
                    withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh 'curl -v -u $user:$pass --upload-file spark-2.3.5-TDP-0.1.0-SNAPSHOT-bin-tdp.tgz http://10.110.4.212:8081/repository/maven-tar-files/spark-2.3/spark-2.3.5-TDP-0.1.0-SNAPSHOT-bin-tdp-${number}.tar.gz'
                    }
                }
            }       
        }
    }
}
