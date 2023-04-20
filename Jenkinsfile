podTemplate(containers: [
    containerTemplate(
        name: 'tdp-builder', 
        image: 'stbaum/jenkins:latest', 
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
                ./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Dscalastyle.skip=true -Denforcer.skip=true
                '''
            }
            /*stage('Test') {
                echo "Testing..."
                sh '''
                mvn test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Dscalastyle.skip=true -Denforcer.skip=true --fail-never
                '''
            }*/
            stage('Deliver') {
                echo "Deploy..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh './dev/make-distribution-deploy.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Dscalastyle.skip=true -Denforcer.skip=true -s settings.xml'
                }
            }
            stage("Publish tar.gz to Nexus") {
                echo "Publish tar.gz..."
                withCredentials([usernamePassword(credentialsId: '4b87bd68-ad4c-11ed-afa1-0242ac120002', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh 'curl -v -u $user:$pass --upload-file spark-3.2.2-TDP-0.1.0-SNAPSHOT-bin-tdp.tgz http://10.110.4.212:8081/repository/maven-tar-files/spark-3.2/spark-3.2.2-TDP-0.1.0-SNAPSHOT-bin-${number}.tar.gz'
                }
            }       
        }
    }
}  