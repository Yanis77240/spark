podTemplate(containers: [
    containerTemplate(
        name: 'tdp-builder', 
        image: 'stbaum/jenkins-mysql',
        resourceRequestCpu: "2000m",
        resourceRequestMemory: "8000Mi",
        resourceLimitCpu: "3000m",
        resourceLimitMemory: "11000Mi",
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
                git branch: 'branch-3.2-TDP-alliage-k8s', url: 'https://github.com/Yanis77240/spark'
            }   
            stage ('Build') {
                echo "Building..."
                sh '''
                export MAVEN_OPTS="-Xss64m -Xmx2g -XX:ReservedCodeCacheSize=1g"
                ./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Dscalastyle.skip=true -Denforcer.skip=true -Dstyle.color=never
                '''
            }
            stage('Test') {
                echo "Testing..."
                withEnv(["number=${currentBuild.number}"]) {
                    withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh '''export MAVEN_OPTS="-Xss64m -Xmx2g -XX:ReservedCodeCacheSize=1g"
                            export DEFAULT_ARTIFACT_REPOSITORY="file:$HOME/.m2/repository/"
                            '''
                        sh 'mvn clean'
                        sh './build/mvn test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Dsurefire.rerunFailingTestsCount=3 --fail-never -Dstyle.color=never'
                        sh 'mvn surefire-report:report-only  -Daggregate=true'
                        sh 'curl -v -u $user:$pass --upload-file target/site/surefire-report.html http://10.110.4.212:8081/repository/test-reports/spark-3.2/surefire-report-${number}.html'
                    }
                    withCredentials([usernamePassword(credentialsId: '12b08ce0-3046-11ee-be56-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh script: $/
                        grep -F --color=never --no-group-separator "*** FAILED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > scala-tests.txt
                        grep -E --color=never --no-group-separator "*** RUN ABORTED ***" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > aborted-tests.txt
                        grep -E --color=never --no-group-separator "succeeded.*canceled.*ignored" */target/surefire-reports/SparkTestSuite.txt */**/target/surefire-reports/SparkTestSuite.txt | sed -r "s|\x1B\[[0-9;]*[mK]||g" > scala-end-results.txt
                        /$
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass -e "CREATE DATABASE IF NOT EXISTS SPARK3_${number};"
                        '''
                        sh'''
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK3_${number} -e "CREATE TABLE test_list (Module VARCHAR(125), Test_Name VARCHAR(255)); LOAD DATA LOCAL INFILE 'scala-tests.txt' INTO TABLE test_list FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE test_list SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', '');"
                        '''
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK3_${number} -e "CREATE TABLE aborted_tests (Module VARCHAR(125), Results VARCHAR(255)); LOAD DATA LOCAL INFILE 'aborted-tests.txt' INTO TABLE aborted_tests FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE aborted_tests SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', '');"
                        '''
                        sh '''
                        mysql -h 10.100.99.143 -u $user -p$pass SPARK3_${number} -e "CREATE TABLE test_resume (Module VARCHAR(125), Results VARCHAR(255)); LOAD DATA LOCAL INFILE 'scala-end-results.txt' INTO TABLE test_resume FIELDS TERMINATED BY 'txt:' LINES TERMINATED by '\n'; UPDATE test_resume SET Module = REPLACE(Module, '/target/surefire-reports/SparkTestSuite.', ''); CREATE TABLE results (SELECT Module, SUBSTRING_INDEX(Results, ',', 1) AS Succeeded,     SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 2), ',', -1) AS Failed,     SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 3), ',', -1) AS Canceled, SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 4), ',', -1) AS Ignored, SUBSTRING_INDEX(SUBSTRING_INDEX(Results, ',', 5), ',', -1) AS Pending  FROM test_resume); drop table test_resume; UPDATE results SET Succeeded = SUBSTRING_INDEX(Succeeded, ' ', -1), Failed = SUBSTRING_INDEX(Failed, ' ', -1), Canceled = SUBSTRING_INDEX(Canceled, ' ', -1), Ignored = SUBSTRING_INDEX(Ignored, ' ', -1), Pending = SUBSTRING_INDEX(Pending, ' ', -1);"
                        '''
                    }
                }
            }
            stage('Deliver') {
                echo "Deploy..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh './dev/make-distribution-deploy.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Dscalastyle.skip=true -Denforcer.skip=true -Dstyle.color=never -s settings.xml'
                }
            }
            stage("Publish tar.gz to Nexus") {
                echo "Publish tar.gz..."
                withEnv(["number=${currentBuild.number}"]) {
                    withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh 'curl -v -u $user:$pass --upload-file spark-3.2.2-TDP-0.1.0-SNAPSHOT-bin-tdp.tgz http://10.110.4.212:8081/repository/maven-tar-files/spark-3.2/spark-3.2.2-TDP-0.1.0-SNAPSHOT-bin-${number}.tar.gz'
                    }
                }
            }       
        }
    }
}  