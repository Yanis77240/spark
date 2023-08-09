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
                ./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume -Dstyle.color=never
                '''
            }
            stage('Test') {
                echo "Testing..."
                withEnv(["number=${currentBuild.number}"]) {
                    withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh 'mvn clean test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume --batch-mode -Dsurefire.rerunFailingTestsCount=3 --fail-never -Dstyle.color=never'
                        sh 'mvn surefire-report:report-only  -Daggregate=true'
                        sh 'curl -v -u $user:$pass --upload-file target/site/surefire-report.html http://10.110.4.212:8081/repository/test-reports/spark-2.3/surefire-report-${number}.html'
                    }
                    withCredentials([usernamePassword(credentialsId: '12b08ce0-3046-11ee-be56-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh script: $/
                        grep -F --color=never --no-group-separator "*** FAILED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > scala-tests.txt
                        grep -E --color=never --no-group-separator "*** RUN ABORTED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > aborted-tests.txt
                        grep -E --color=never --no-group-separator "succeeded.*canceled.*ignored" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > scala-end-results.txt
                        /$
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass -e "CREATE DATABASE IF NOT EXISTS SPARK2;"
                        '''
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e "CREATE TABLE test_list_${number} (Module VARCHAR(125), Test_Name VARCHAR(255)); LOAD DATA LOCAL INFILE 'scala-tests.txt' INTO TABLE test_list_${number} FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE test_list_${number} SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', '');"
                        '''
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e "CREATE TABLE aborted_tests_${number} (Module VARCHAR(125), Results VARCHAR(255)); LOAD DATA LOCAL INFILE 'aborted-tests.txt' INTO TABLE aborted_tests_${number} FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE aborted_tests_${number} SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', '');"
                        '''
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e "CREATE TABLE test_resume_${number} (Module VARCHAR(125), Results VARCHAR(255)); LOAD DATA LOCAL INFILE 'scala-end-results.txt' INTO TABLE test_resume_${number} FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE test_resume_${number} SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', ''); CREATE TABLE results_${number} (SELECT Module, SUBSTRING_INDEX(Results, ',', 1) AS Succeeded,     SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 2), ',', -1) AS Failed,     SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 3), ',', -1) AS Canceled, SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 4), ',', -1) AS Ignored, SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 5), ',', -1) AS Pending  FROM test_resume_${number}); drop table test_resume_${number}; UPDATE results_${number} SET Succeeded = SUBSTRING_INDEX(Succeeded, ' ', -1), Failed = SUBSTRING_INDEX(Failed, ' ', -1), Canceled = SUBSTRING_INDEX(Canceled, ' ', -1), Ignored = SUBSTRING_INDEX(Ignored, ' ', -1), Pending = SUBSTRING_INDEX(Pending, ' ', -1);"
                        '''
                        script{
                            def lastSuccessfulBuildID = 0
                            def build = currentBuild.previousBuild
                            while (build != null) {
                                if (build.result == "SUCCESS")
                                {
                                    lastSuccessfulBuildID = build.id as Integer
                                    break
                                }
                                build = build.previousBuild
                            }
                            println lastSuccessfulBuildID
                        }
                        
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e "CREATE TABLE IF NOT EXISTS test_list_${lastSuccessfulBuildID} AS SELECT * FROM test_list_${number};"
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK2 -e "CREATE TABLE comparison_${number} AS SELECT test_list_${number}.Module, test_list_${number}.Test_Name FROM test_list_${number} LEFT JOIN test_list_${lastSuccessfulBuildID} ON test_list_${number}.Test_Name=test_list_${lastSuccessfulBuildID}.Test_Name WHERE test_list_${lastSuccessfulBuildID}.Test_Name IS NULL;"
                        '''
                        sh '''
                       ./decision-script.sh ${number}
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
