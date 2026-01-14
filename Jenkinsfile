pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'musfiqdehan/lms-web'
        IMAGE_TAG = 'latest'
        SERVER_IP = "${env.SERVER_IP}"
        SERVER_USER = "${env.SERVER_USER}"
        APP_PATH = "${env.APP_PATH}"
        GITHUB_TOKEN = "${env.GITHUB_TOKEN}"
        GITHUB_USERNAME = "${env.GITHUB_USERNAME}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Image') {
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'ghcr-login') {
                        def customImage = docker.build("${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}", "-f deployment/Dockerfile .")
                        customImage.push()
                        customImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to VPS') {
            steps {
                sshagent(['vps-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'EOF'
                        cd ${APP_PATH}
                        
                        # Pull latest code
                        git pull origin main
                        
                        # Login and pull latest image
                        echo "${env.GITHUB_TOKEN}" | docker login ghcr.io -u ${env.GITHUB_USERNAME} --password-stdin
                        docker compose -f deployment/docker-compose.yml pull web
                        
                        # Restart services
                        docker compose -f deployment/docker-compose.yml up -d
                        
                        # Maintenance
                        docker compose -f deployment/docker-compose.yml exec -T web python manage.py migrate
                        docker compose -f deployment/docker-compose.yml exec -T web python manage.py collectstatic --noinput
                        
                        # Cleanup
                        docker image prune -f
EOF
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed. Please check the logs.'
        }
    }
}
