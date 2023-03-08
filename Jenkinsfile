pipeline {
    agent { 
        node {
            label 'docker-tdp-builder'
            }
      }
    environment {
        number="${currentBuild.number}"
      }
    triggers {
        pollSCM '0 1 * * *'
      }
    stages{
        stage('clone') {
            steps {
                echo "Cloning..."
                git branch: 'branch-2.3-TDP-alliage', url: 'https://github.com/Yanis77240/spark'
            }
        }
        stage('Build') {
            steps {
                echo "Building..."
                sh '''
                ./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume
                '''
            }
        }
        /*stage('Test') {
            steps {
                echo "Testing..."
                sh '''
                ./build/mvn clean test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume --fail-never
                '''
            }
        }*/
        stage("Publish to Nexus Repository Manager") {
            steps {
                echo "Deploy..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh 'mvn deploy -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume -DskipTests -s settings.xml'
                }
            }        
        }
        stage("Publish tar.gz to Nexus") {
            steps {
                echo "Publish tar.gz..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh 'curl -v -u $user:$pass --upload-file spark-2.3.5-TDP-0.1.0-SNAPSHOT-bin-tdp.tgz http://172.19.0.2:8081/repository/maven-tar-files/spark-2.3/spark-2.3.5-TDP-0.1.0-SNAPSHOT-bin-tdp-${number}.tar.gz'
                }
            }        
        }
    }
}