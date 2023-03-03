pipeline {
    agent { 
        node {
            label 'docker-tdp-builder'
            }
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
        stage('Test') {
            steps {
                echo "Testing..."
                sh '''
                ./build/mvn test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume --fail-never
                '''
            }
        }
        stage("Publish to Nexus Repository Manager") {
            steps {
                echo "Deploy..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh './dev/make-distribution-deploy.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume -s settings.xml'
                }
            }        
        }
    }
}