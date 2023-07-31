podTemplate(containers: [
    containerTemplate(
        name: 'tdp-builder', 
        image: 'stbaum/jenkins-mysql', 
        command: 'sleep', 
        args: '30d'
        )
]) {

    node(POD_LABEL) {
        container('tdp-builder') {
            environment {
                number="${currentBuild.number}"
            }
            stage('Git Clone') {
                echo "Cloning..."
                git branch: 'branch-2.3-TDP-alliage-k8s', url: 'https://github.com/Yanis77240/spark'
            }   
            stage ('Build') {
                echo "Building..."
                sh '''
                ./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume
                '''
            }
            stage('Test') {
                echo "Testing..."
                withEnv(["number=${currentBuild.number}"]) {
                    withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh 'mvn clean test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume --batch-mode -Dsurefire.rerunFailingTestsCount=3 --fail-never'
                        sh 'mvn surefire-report:report-only  -Daggregate=true'
                        sh 'curl -v -u $user:$pass --upload-file target/site/surefire-report.html http://10.110.4.212:8081/repository/test-reports/spark-2.3/surefire-report-${number}.html'
                    }
                    withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh '''
                        grep -E --color=never --no-group-separator "*** FAILED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt > scala-tests.txt
                        grep -E --color=never --no-group-separator "*** RUN ABORTED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt > aborted-tests.txt
                        grep -E --color=never --no-group-separator "succeeded.*canceled.*ignored" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt > scala-end-results.txt
                        '''
                        sh'''
                        mysql -h 10.100.99.143 -u root -padmin tests -e "CREATE TABLE spark_2_test_list (Module VARCHAR(125), Message VARCHAR(255)); LOAD DATA INFILE '/var/lib/mysql-files/scala-tests.txt' INTO TABLE spark_2_test_list FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE spark_2_test_list SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', '');"
                        '''
                        sh '''
                        mysql -h 10.100.99.143 -u root -padmin tests -e "CREATE TABLE spark_2_aborted_tests (Module VARCHAR(125), Results VARCHAR(255)); LOAD DATA INFILE '/var/lib/mysql-files/aborted-tests.txt' INTO TABLE spark_2_aborted_tests FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; PDATE spark_2_aborted_tests SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', '');
                        '''
                        sh '''
                        mysql -h 10.100.99.143 -u root -padmin tests -e "CREATE TABLE spark_2_test_resume (Module VARCHAR(125), Results VARCHAR(255)); LOAD DATA INFILE '/var/lib/mysql-files/scala-end-results.txt' INTO TABLE spark_2_test_resume FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE spark_2_test_resume SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', ''); CREATE TABLE spark_2_results (SELECT Module, SUBSTRING_INDEX(Results, ',', 1) AS Succeeded,     SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 2), ',', -1) AS Failed,     SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 3), ',', -1) AS Canceled, SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 4), ',', -1) AS Ignored, SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 5), ',', -1) AS Pending  FROM spark_2_test_resume); drop table spark_2_test_resume; UPDATE spark_2_results SET Succeeded = SUBSTRING_INDEX(Succeded, ' ', -1), Failed = SUBSTRING_INDEX(Failed, ' ', -1), Canceled = SUBSTRING_INDEX(Canceled, ' ', -1), Ignored = SUBSTRING_INDEX(Ignored, ' ', -1), Pending = SUBSTRING_INDEX(Pending, ' ', -1);
                        '''
                    }
                }
            }
            stage('Deliver') {
                echo "Deploy..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh './dev/make-deployment.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume -s settings.xml'
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
