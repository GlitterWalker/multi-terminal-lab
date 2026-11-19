pipeline {
  agent any

  environment {
    HOST = 'ubuntu@13.235.86.32'
    DIR  = '/home/ubuntu/project'
  }

  stages {
    stage('Syntax check') {
      steps {
        sh 'python3 -m py_compile app.py pages.py quiz.py'
      }
    }

    stage('Deploy') {
      steps {
        sshagent(['lab-server-ssh']) {
          sh '''
            rsync -az --delete \
              --exclude venv --exclude results --exclude .git \
              -e "ssh -o StrictHostKeyChecking=no" \
              ./ $HOST:$DIR/

            ssh -o StrictHostKeyChecking=no $HOST \
              "cd $DIR && docker build -t lab-image . && sudo systemctl restart lab"
          '''
        }
      }
    }

    stage('Verify') {
      steps {
        sh 'sleep 3 && curl -fs http://13.235.86.32:5000/ > /dev/null'
      }
    }
  }

  post {
    success { echo 'Deployed successfully' }
    failure { echo 'Deploy failed, check the console output' }
  }
}